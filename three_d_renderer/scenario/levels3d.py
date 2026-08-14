from three_d_renderer.entities.base3d import Cube, Dodeca, Ico, Tetra
from three_d_renderer.scenario.level3d import Level3D


def build_level_3d_1() -> Level3D:
    ico1 = Ico(
        position=[70, 170, -20],
        size=20,
        angle=[0, 30, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[-3, 5, 1],
    )
    dode = Dodeca(
        position=[0, 100, 20],
        size=18,
        angle=[0, 30, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[2, -3, -1],
    )
    cube = Cube(
        position=[-25, 150, -50],
        size=30,
        angle=[0, 5, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[0, 1, 0],
    )
    tetra = Tetra(
        position=[50, 50, -100],
        size=14,
        angle=[0, 17, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[1, 1, -1],
    )
    return Level3D(entities=[dode, ico1, cube, tetra])
