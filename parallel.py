import math
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Sequence, TypeVar

_T = TypeVar("_T")
_R = TypeVar("_R")


class RenderPool:
    """Threads for the parts of a frame that split cleanly into independent work.

    Only actually parallel on a free-threaded interpreter (python3.14t). Under
    the GIL this just adds overhead, which is why it is opt-in.
    """

    def __init__(self, workers: int):
        self._workers = workers
        self._pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="render")

    def map(self, work: Callable[[_T], _R], items: Sequence[_T]) -> list[_R]:
        """One task per item, in the order they were given.

        For items that are individually expensive, like resolving an entity's
        pixels.
        """
        return list(self._pool.map(work, items))

    def map_bands(
        self,
        work: Callable[[Sequence[_T]], list[_R]],
        items: Sequence[_T],
    ) -> list[_R]:
        """One task per contiguous band of items, flattened back in order.

        For items that are individually cheap and cost about the same each,
        like a screen row, where one task apiece would cost more in overhead
        than it saves. Use `map` instead when the items vary in cost.
        """
        if len(items) <= 1:
            return work(items)

        size = math.ceil(len(items) / self._workers)
        bands = [items[i : i + size] for i in range(0, len(items), size)]

        return [result for band in self._pool.map(work, bands) for result in band]

    def shutdown(self) -> None:
        self._pool.shutdown(wait=False, cancel_futures=True)


def make_render_pool(workers: int) -> RenderPool | None:
    """None when there's nothing to gain, so callers can take the serial path."""
    return RenderPool(workers) if workers > 1 else None
