from game import Game
from model.game import GameStatus


def main():

    game = Game()

    # TODO: should be different loops per game type
    while (
        game.status == GameStatus.MODE_2D
        or game.status == GameStatus.MODE_3D
        or game.status == GameStatus.MODE_3D_V2
        or game.status == GameStatus.MODE_PHYSICS_2D
    ):
        game.game_loop()


if __name__ == "__main__":
    main()
