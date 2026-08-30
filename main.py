from game import Game
from model.game import GameStatus


def main():
    game = Game()

    while game.status == GameStatus.RUNNING:
        game.main_loop()
    else:
        game.handle_quit()


if __name__ == "__main__":
    main()
