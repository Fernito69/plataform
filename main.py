from entities.player2d import Player2D
from game import Game
from levels_2d import build_level1
from model.game import GameStatus
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.scenario.levels_3d import build_level_3d_1


def main():
    player = Player2D(1)
    player_3d = Player3D(1)
    levels_2d = [build_level1()]
    levels_3d = [build_level_3d_1()]

    # hardcoded cool place
    player_3d.position = [18, 84, -33]  # [-3, -126, -48]

    game = Game(player_2d=player, levels=levels_2d, player_3d=player_3d, levels_3d=levels_3d)

    # TODO: should be different loops per game type
    while (
        game.status == GameStatus.MODE_2D
        or game.status == GameStatus.MODE_3D
        or game.status == GameStatus.MODE_3D_V2
    ):
        game.game_loop()


if __name__ == "__main__":
    main()
