import random

from factories.theme import Blue, Cyan, Green, Magenta, Orange, Red, Violet, White, Yellow
from model.base import PointF, VectorF
from three_d_renderer.entities.base3d import Entity3D
from three_d_renderer.entities.polyhedra import Cube, Dodeca, Ico, Tetra
from three_d_renderer.scenario.level_3d import Level3D


def build_level_3d_1() -> Level3D:
    colors = [White, Cyan, Red, Blue, Green, Magenta, Yellow, Violet, Orange]
    random.shuffle(colors)

    ico1 = Ico(
        position=PointF(20, 170, -20),
        size=20,
        angle=VectorF(0, 0, 0),
        mov_vector=VectorF(0, 0, 0),
        # rot_vector=(0, 0, 0)
        rot_vector=VectorF(1, 0, 0),
        color=colors[1](),
    )
    dode = Dodeca(
        position=PointF(0, 100, 20),
        size=18,
        angle=VectorF(0, 30, 0),
        mov_vector=VectorF(0, 0, 0),
        rot_vector=VectorF(-1, 2, 0),
        # # rot_vector=[0, 0, 0)
    )
    cube = Cube(
        position=PointF(-25, 150, -30),
        size=30,
        angle=VectorF(0, 5, 0),
        mov_vector=VectorF(0, 0, 0),
        # # rot_vector=(0, 0, 0)
        rot_vector=VectorF(-3, 3, 1),
    )
    cube2 = Cube(
        position=PointF(+25, 60, 50),
        size=15,
        angle=VectorF(0, -4, 0),
        mov_vector=VectorF(0, 0, 0),
        rot_vector=VectorF(2, 2, 1),
        # # rot_vector=(0, 0, 0)
    )
    tetra = Tetra(
        position=PointF(50, 50, -80),
        size=14,
        angle=VectorF(0, 17, 0),
        mov_vector=VectorF(0, 0, 0),
        rot_vector=VectorF(-3, 5, 1),
        # # rot_vector=(0, 0, 0)
    )
    universe = Dodeca(
        position=PointF(0, 0, 0),
        size=100,
        angle=VectorF(0, 30, 0),
        mov_vector=VectorF(0, 0, 0),
        rot_vector=VectorF(-1, 2, 0),
    )

    entities: list[Entity3D] = [dode, ico1, cube, tetra, cube2, universe]

    # Hack to assign colors
    for i, e in enumerate(entities):
        e.theme.color = colors[i]()

    return Level3D(entities=entities)


def build_3d_levels() -> list[Level3D]:
    return [
        build_level_3d_1(),
    ]
