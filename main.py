from game import Game
from model.game import GameStatus
from model.theme import BR


def main():
    game = Game()

    while game.status == GameStatus.RUNNING:
        game.main_loop()

    game.display.print_message("BYE BYE!" + BR + "Thanks for messing around with this program :)")


if __name__ == "__main__":
    main()
