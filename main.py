from entities.player2d import Player2D
from game import Game
from levels_2d import build_level1
from model.game import GameStatus
from three_d_renderer.entities.player3d import Player3D


def main():
    player = Player2D(1)
    player_3d = Player3D(1)
    level1 = build_level1()

    # hardcoded cool place
    player_3d.position = [-3, -126, -48]

    game = Game(player_2d=player, levels=[level1], player_3d=player_3d)

    while game.status == GameStatus.MODE_2D or game.status == GameStatus.MODE_3D:
        game.game_loop()


if __name__ == "__main__":
    main()
