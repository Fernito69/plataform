import queue
import threading
from typing import Callable, Protocol

from physics2d.model.frame import FrameSnapshot

type CalculateFrame = Callable[[], FrameSnapshot | None]
type RenderFrame = Callable[[FrameSnapshot | None], None]

_SHUTDOWN_TIMEOUT = 1


class FramePipeline(Protocol):
    """How one frame gets from the calculation stage to the render stage.

    Implementations decide whether the two stages overlap. A process-based one
    can be dropped in here too, as long as the FrameSnapshot stays picklable.
    """

    def run_frame(self) -> None: ...

    def shutdown(self) -> None: ...


class SequentialFramePipeline:
    """Calculate frame N, then render frame N, both on the calling thread."""

    def __init__(self, calculate: CalculateFrame, render: RenderFrame):
        self._calculate = calculate
        self._render = render

    def run_frame(self) -> None:
        self._render(self._calculate())

    def shutdown(self) -> None:
        pass


_WORK = object()
_STOP = object()


class ThreadedFramePipeline:
    """Calculate frame N+1 on a worker thread while frame N is rendered here.

    The worker owns all mutable game state (physics, input, scenario); the
    calling thread only ever touches the FrameSnapshot it was handed, plus the
    terminal. Since writing a full frame to the terminal releases the GIL, that
    write overlaps with the next frame's calculation.
    """

    def __init__(self, calculate: CalculateFrame, render: RenderFrame):
        self._calculate = calculate
        self._render = render

        # Both bounded to 1: at most one frame in flight, so the renderer can
        # never fall behind and start showing stale frames.
        self._requests: queue.Queue = queue.Queue(maxsize=1)
        self._frames: queue.Queue = queue.Queue(maxsize=1)

        self._worker = threading.Thread(target=self._work, name="frame-calc", daemon=True)
        self._running = False

    def _work(self) -> None:
        while self._requests.get() is not _STOP:
            try:
                self._frames.put(self._calculate())
            except BaseException as error:
                # Re-raised on the calling thread, otherwise it dies silently.
                self._frames.put(error)
                return

    def run_frame(self) -> None:
        if not self._running:
            self._running = True
            self._worker.start()
            self._requests.put(_WORK)

        frame = self._frames.get()

        if isinstance(frame, BaseException):
            self._running = False
            raise frame

        # Ask for N+1 *before* rendering N. That overlap is the whole point.
        self._requests.put(_WORK)

        self._render(frame)

    def shutdown(self) -> None:
        if not self._running:
            return

        self._running = False

        try:
            self._requests.put_nowait(_STOP)
        except queue.Full:
            pass

        # Unblock a worker that is holding a finished frame nobody will render.
        try:
            self._frames.get_nowait()
        except queue.Empty:
            pass

        self._worker.join(timeout=_SHUTDOWN_TIMEOUT)
