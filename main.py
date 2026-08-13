from entities.player2d import Player2D
from three_d_renderer.entities.player3d import Player3D
from game import Game
from levels2d import build_level1
from model.game import GameStatus


def main():
    player = Player2D(1)
    player_3d = Player3D(1)
    level1 = build_level1()

    game = Game(player_2d=player, levels=[level1], player_3d=player_3d)

    while (
        game.status == GameStatus.PLAYING or game.status == GameStatus.THREE_D_RENDERER
    ):
        game.game_loop()


if __name__ == "__main__":
    main()
