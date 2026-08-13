from entities.player import Player
from game import Game
from levels import build_level1
from model.game import GameStatus


def main():
    player = Player(0)
    level1 = build_level1()

    game = Game(player=player, levels=[level1])

    while game.status == GameStatus.PLAYING:
        game.game_loop()


if __name__ == "__main__":
    main()
