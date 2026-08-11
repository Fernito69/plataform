"""Entry point: wires up the player, levels and game loop."""

from model.game import GameStatus
from model.player import PlayerStatus
from entities.player import Player
from game import Game
from levels import build_level1
from terminal import clear


def main():
    clear()

    player = Player(0)
    level1 = build_level1()

    game = Game(player=player, levels=[level1])

    while game.status == GameStatus.PLAYING:
        game.game_loop()

    if game.player.status == PlayerStatus.EXIT:
        game.levels[game.current_level_index].print_message("YOU WON!")
    elif game.player.status == PlayerStatus.DEAD:
        game.levels[game.current_level_index].print_message("GAME OVER")


if __name__ == "__main__":
    main()
