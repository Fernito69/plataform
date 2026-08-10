"""Entry point: wires up the player, levels and game loop."""

from entities.player import Player
from game import Game
from levels import build_level1
from terminal import clear


def main():
    clear()

    player = Player(0)
    level1 = build_level1()

    game = Game(player=player, levels=[level1])

    while game.status == "playing":
        player.player_movement()

        if player.status != "alive":
            match player.status:
                case "dead":
                    message = "GAME OVER"
                case "quit":
                    message = "BYE BYE"

            level1.print_message(message)
            game.status = "gameover"

        game.print_playfield()


if __name__ == "__main__":
    main()
