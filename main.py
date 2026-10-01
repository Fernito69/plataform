import argparse

from game import Game
from model.game import GameStatus


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Terminal game engine.")
    parser.add_argument(
        "--threaded",
        action="store_true",
        help="calculate frame N+1 on a worker thread while frame N is being drawn",
    )
    parser.add_argument(
        "--render-workers",
        type=int,
        default=0,
        metavar="N",
        help=(
            "resolve entity pixels on N threads (0 or 1 = serial). "
            "Only actually parallel on a free-threaded interpreter, e.g. `py -V:3.14t`"
        ),
    )
    return parser.parse_args()


def main():
    args = _parse_args()
    game = Game(threaded=args.threaded, render_workers=args.render_workers)

    try:
        while game.status == GameStatus.RUNNING:
            game.main_loop()
    finally:
        game.shutdown()


if __name__ == "__main__":
    main()
