from three_d_renderer.entities.base3d import Cube, Dodeca, F_Letter, Ico, Tetra
from three_d_renderer.scenario.level_3d import Level3D


def build_level_3d_1() -> Level3D:
    # f = F_Letter(
    #     position=[0,170, 0],
    #     size=20,
    #     angle=[0, 0, 0],
    #     movMatrix=[0, 0, 0],
    #     rotMatrix=[1, 0, 0],
    # )

    ico1 = Ico(
        position=[20, 170, -20],
        size=20,
        angle=[0, 0, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[1, 0, 0],
    )
    dode = Dodeca(
        position=[0, 100, 20],
        size=18,
        angle=[0, 30, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[-1, 2, 0],
    )
    cube = Cube(
        position=[-25, 150, -50],
        size=30,
        angle=[0, 5, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[-3, 3, 1],
    )
    cube2 = Cube(
        position=[+25, 60, 50],
        size=15,
        angle=[0, -4, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[2, 2, 1],
    )
    tetra = Tetra(
        position=[50, 50, -80],
        size=14,
        angle=[0, 17, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[-3, 5, 1],
    )
    universe = Dodeca(
        position=[0, 0, 0],
        size=100,
        angle=[0, 30, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[-1, 2, 0],
    )
    return Level3D(entities=[dode, ico1, cube, tetra, cube2, universe])
