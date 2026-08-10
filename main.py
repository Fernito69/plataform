"""Entry point: wires up the player, levels and game loop."""
from entities import Player
from game import Game
from levels import build_level1
from terminal import clear


def main():
    clear()

    player = Player(0)
    level1 = build_level1()

    game = Game(player=player, levels=[level1])

    while game.status == "playing":
        if player.player_movement() == "q":
            level1.print_message("BYE BYE")
            game.status = "gameover"

        if player.status == "dead":
            level1.print_message("GAME OVER")
            game.status = "gameover"

        game.print_playfield()


if __name__ == "__main__":
    main()
