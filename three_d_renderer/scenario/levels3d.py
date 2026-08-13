from three_d_renderer.entities.base3d import Ico, Dodeca
from three_d_renderer.scenario.level3d import Level3D


def build_level_3d_1() -> Level3D:
    # ico1 = Ico(
    #     position=[0, 100, 20],
    #     size=20,
    #     angle=[0, 30, 0],
    #     # movMatrix=[0, -4, 0],
    #     # rotMatrix=[2, -5, 0],
    #     movMatrix=[0, 0, 0],
    #     rotMatrix=[2, -5, 0],
    # )
    dode = Dodeca(
        position=[0, 100, 20],
        size=18,
        angle=[0, 30, 0],
        # movMatrix=[0, -4, 0],
        # rotMatrix=[2, -5, 0],
        movMatrix=[0, 0, 0],
        rotMatrix=[2, -5, 0],
    )
    return Level3D(entities=[dode])
