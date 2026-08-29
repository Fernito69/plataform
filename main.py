from game import Game
from model.game import GameStatus


def main():
    game = Game()

    while game.status not in [GameStatus.QUIT, GameStatus.GAMEOVER]:
        game.game_loop()


if __name__ == "__main__":
    main()
