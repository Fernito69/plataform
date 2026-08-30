from game import Game
from model.game import GameStatus


def main():
    game = Game()

    while game.status == GameStatus.RUNNING:
        game.main_loop()

    game.display.print_message("BYE BYE!")


if __name__ == "__main__":
    main()
