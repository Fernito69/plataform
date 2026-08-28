from constants import I_PHI, PHI, R2O2
from model.base import Point3F
from model.theme import RGB
from three_d_renderer.entities.base3d import Entity3D
from utils import add_triplet


# REFACTOR vertices stuff, it's sooo repetitive
class Cube(Entity3D):
    vertex_connections: list[tuple[int, int]] = [
        (0, 1),
        (0, 2),
        (0, 4),
        (1, 3),
        (1, 5),
        (2, 3),
        (2, 6),
        (3, 7),
        (4, 5),
        (4, 6),
        (5, 7),
        (6, 7),
    ]

    def __init__(
        self,
        position: Point3F,
        size: float,
        angle: Point3F,
        color: RGB = RGB(),
        movMatrix: Point3F = (0, 0, 0),
        rotMatrix: Point3F = (0, 0, 0),
        vertices: list[Point3F] = [],
    ):
        Entity3D.__init__(
            self,
            position=position,
            size=size,
            angle=angle,
            movMatrix=movMatrix,
            rotMatrix=rotMatrix,
            vertices=vertices,
            color=color,
        )

    def get_diameter(self) -> float:
        # "diameter" for cube is just the size
        return self.size

    def calc_main_vertexes(self, apply: bool = False) -> list[Point3F]:
        vertexes = []
        x, y, z = self.position
        s = self.size

        vertexes.append((x + s / 2, y + s / 2, z + s / 2))  # 0
        vertexes.append((x + s / 2, y - s / 2, z + s / 2))  # 1
        vertexes.append((x - s / 2, y + s / 2, z + s / 2))  # 2
        vertexes.append((x - s / 2, y - s / 2, z + s / 2))  # 3
        vertexes.append((x + s / 2, y + s / 2, z - s / 2))  # 4
        vertexes.append((x + s / 2, y - s / 2, z - s / 2))  # 5
        vertexes.append((x - s / 2, y + s / 2, z - s / 2))  # 6
        vertexes.append((x - s / 2, y - s / 2, z - s / 2))  # 7

        if apply:
            self.vertices = vertexes

        return vertexes

    def calc_legacy_voxels(self):
        # TODO: this should also check for velocity / previous position
        if self.is_lazy() and self.vertices and len(self.vertices) > 0:
            return

        vertexes = self.calc_main_vertexes()
        x, y, z = self.position
        s = self.size

        # "voxels" for the edges
        for i in range(round(s)):
            vertexes.append((x + s / 2 - i, y + s / 2, z + s / 2))
            vertexes.append((x + s / 2, y + s / 2 - i, z + s / 2))
            vertexes.append((x + s / 2, y + s / 2, z + s / 2 - i))

            vertexes.append((x - s / 2, y + s / 2 - i, z + s / 2))
            vertexes.append((x - s / 2, y + s / 2, z + s / 2 - i))

            vertexes.append((x + s / 2 - i, y - s / 2, z + s / 2))
            vertexes.append((x + s / 2, y - s / 2, z + s / 2 - i))

            vertexes.append((x + s / 2 - i, y + s / 2, z - s / 2))
            vertexes.append((x + s / 2, y + s / 2 - i, z - s / 2))

            vertexes.append((x + s / 2 - i, y + s / 2, z - s / 2))
            vertexes.append((x + s / 2, y + s / 2 - i, z - s / 2))

            vertexes.append((x + s / 2 - i, y - s / 2, z - s / 2))
            vertexes.append((x - s / 2, y + s / 2 - i, z - s / 2))
            vertexes.append((x - s / 2, y - s / 2, z + s / 2 - i))

        self.vertices = vertexes
        self.apply_rotations()


################


class Tetra(Entity3D):
    vertex_connections: list[tuple[int, int]] = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

    def __init__(
        self,
        position: Point3F,
        size: float,
        angle: Point3F,
        color: RGB = RGB(),
        movMatrix: Point3F = (0, 0, 0),
        rotMatrix: Point3F = (0, 0, 0),
        vertices: list[Point3F] = [],
    ):
        Entity3D.__init__(
            self,
            position=position,
            size=size,
            angle=angle,
            movMatrix=movMatrix,
            rotMatrix=rotMatrix,
            vertices=vertices,
            color=color,
        )
        self.name = "Tetrahedron"

    def get_diameter(self) -> float:
        # hmmm also roughly sqrt2? the size? TODO: do proper calc later
        return self.size * R2O2 * 2

    def calc_main_vertexes(self, apply: bool = False) -> list[Point3F]:
        x = self.position[0]
        y = self.position[1]
        z = self.position[2]
        s = self.size

        vertexes = []

        vertexes.append((x + s, y, z - R2O2 * s))
        vertexes.append((x - s, y, z - R2O2 * s))
        vertexes.append((x, y + s, z + R2O2 * s))
        vertexes.append((x, y - s, z + R2O2 * s))

        if apply:
            self.vertices = vertexes

        return vertexes

    def calc_legacy_voxels(self):
        # TODO: this should also check for velocity / previous position
        if self.is_lazy() and self.vertices and len(self.vertices) > 0:
            return

        vertexes = self.calc_main_vertexes()
        x = self.position[0]
        y = self.position[1]
        z = self.position[2]

        s = self.size

        for t in range(round(s * 2)):
            vertexes.append(((x - s + t), (y), (z - R2O2 * s)))  # 1 - 2
            vertexes.append(((x + s - t / 2), (y + t / 2), (z - R2O2 * s + R2O2 * t)))  # 1 - 3
            vertexes.append(((x + s - t / 2), (y - t / 2), (z - R2O2 * s + R2O2 * t)))  # 1 - 4
            vertexes.append(((x - s + t / 2), (y + t / 2), (z - R2O2 * s + R2O2 * t)))  # 2 - 3
            vertexes.append(((x - s + t / 2), (y - t / 2), (z - R2O2 * s + R2O2 * t)))  # 2 - 4
            vertexes.append(((x), (y - s + t), (z + R2O2 * s)))  # 3 - 4

        self.vertices = vertexes
        self.apply_rotations()


################


class Ico(Entity3D):
    vertex_connections: list[tuple[int, int]] = [
        (0, 1),
        (0, 4),
        (0, 6),
        (0, 8),
        (0, 10),
        (1, 5),
        (1, 7),
        (1, 8),
        (1, 10),
        (2, 4),
        (2, 6),
        (2, 9),
        (2, 11),
        (3, 5),
        (3, 7),
        (3, 9),
        (3, 11),
        (4, 8),
        (4, 9),
        (5, 8),
        (5, 9),
        (6, 10),
        (6, 11),
        (7, 10),
        (7, 11),
        (8, 9),
        (10, 11),
    ]

    def __init__(
        self,
        position: Point3F,
        size: float,
        angle: Point3F,
        color: RGB,
        movMatrix: Point3F = (0, 0, 0),
        rotMatrix: Point3F = (0, 0, 0),
        vertices: list[Point3F] = [],
    ):
        Entity3D.__init__(
            self,
            position=position,
            size=size,
            angle=angle,
            movMatrix=(0, 0, 0),
            rotMatrix=(0, 0, 0),
            color=color,
            vertices=vertices,
        )
        self.position = position
        self.size = size
        self.angle = angle  # XY, XZ, YZ
        self.movMatrix = movMatrix
        self.rotMatrix = rotMatrix
        self.name = "Icosahedron"
        self.vertices = vertices

    def get_diameter(self) -> float:
        # let's say 2*phi?
        return self.size * 2 * PHI

    def calc_main_vertexes(self, apply: bool = False) -> list[Point3F]:
        vertexes = []
        x = self.position[0]
        y = self.position[1]
        z = self.position[2]
        s = self.size

        vertexes.append((x, y + s, z + PHI * s))  # vertex 1
        vertexes.append((x, y - s, z + PHI * s))  # vertex 2
        vertexes.append((x, y + s, z - PHI * s))  # vertex 3
        vertexes.append((x, y - s, z - PHI * s))  # vertex 4

        vertexes.append((x + s, y + PHI * s, z))  # vertex 5
        vertexes.append((x + s, y - PHI * s, z))  # vertex 6
        vertexes.append((x - s, y + PHI * s, z))  # vertex 7
        vertexes.append((x - s, y - PHI * s, z))  # vertex 8

        vertexes.append((x + PHI * s, y, z + s))  # vertex 9
        vertexes.append((x + PHI * s, y, z - s))  # vertex 10
        vertexes.append((x - PHI * s, y, z + s))  # vertex 11
        vertexes.append((x - PHI * s, y, z - s))  # vertex 12

        if apply:
            self.vertices = vertexes
            # print("VERTICES:" + str(self.vertices))
            # raise InterruptedError("popo")

        return vertexes

    def calc_legacy_voxels(self):
        # TODO: this should also check for velocity / previous position
        if self.is_lazy() and self.vertices and len(self.vertices) > 0:
            return

        vertexes = self.calc_main_vertexes()

        x, y, z = self.position
        s = self.size

        # edges of icosahedron
        for t in range(round(s)):
            vertexes.append(((x), (y + s - 2 * t), (z + PHI * s)))  # vertex 1 - 2
            vertexes.append(
                ((x + t), (y + s - t * (1 - PHI)), (z + PHI * s - PHI * t))
            )  # vertex 1 - 5
            vertexes.append(
                ((x - t), (y + s - t * (1 - PHI)), (z + PHI * s - PHI * t))
            )  # vertex 1 - 7
            vertexes.append(
                ((x + PHI * t), (y + s - t), (z + PHI * s - t * (PHI - 1)))
            )  # vertex 1 - 9
            vertexes.append(
                ((x - PHI * t), (y + s - t), (z + PHI * s - t * (PHI - 1)))
            )  # vertex 1 - 11

            vertexes.append(
                ((x + PHI * t), (y - s + t), (z + PHI * s - t * (PHI - 1)))
            )  # vertex 2 - 9
            vertexes.append(
                ((x + t), (y - s + t * (1 - PHI)), (z + PHI * s - PHI * t))
            )  # vertex 2 - 6
            vertexes.append(
                ((x - t), (y - s + t * (1 - PHI)), (z + PHI * s - PHI * t))
            )  # vertex 2 - 8
            vertexes.append(
                ((x - PHI * t), (y - s + t), (z + PHI * s - t * (PHI - 1)))
            )  # vertex 2 - 11

            vertexes.append(
                ((x + t), (y + s - t * (1 - PHI)), (z - PHI * s + PHI * t))
            )  # vertex 3 - 5
            vertexes.append(((x), (y + s - 2 * t), (z - PHI * s)))  # vertex 3 - 4
            vertexes.append(
                ((x - t), (y + s - t * (1 - PHI)), (z - PHI * s + PHI * t))
            )  # vertex 3 - 7
            vertexes.append(
                ((x + PHI * t), (y + s - t), (z - PHI * s + t * (PHI - 1)))
            )  # vertex 3 - 10
            vertexes.append(
                ((x - PHI * t), (y + s - t), (z - PHI * s + t * (PHI - 1)))
            )  # vertex 3 - 12

            vertexes.append(
                ((x + t), (y - s + t * (1 - PHI)), (z - PHI * s + PHI * t))
            )  # vertex 4 - 6
            vertexes.append(
                ((x - t), (y - s + t * (1 - PHI)), (z - PHI * s + PHI * t))
            )  # vertex 4 - 8
            vertexes.append(
                ((x + PHI * t), (y - s + t), (z - PHI * s + t * (PHI - 1)))
            )  # vertex 4 - 10
            vertexes.append(
                ((x - PHI * t), (y - s + t), (z - PHI * s + t * (PHI - 1)))
            )  # vertex 4 - 12

            vertexes.append(((x + s - 2 * t), (y + PHI * s), (z)))  # vertex 5 - 7
            vertexes.append(
                ((x + s - t * (1 - PHI)), (y + PHI * s - PHI * t), (z + t))
            )  # vertex 5 - 9
            vertexes.append(
                ((x + s - t * (1 - PHI)), (y + PHI * s - PHI * t), (z - t))
            )  # vertex 5 - 10

            vertexes.append(((x + s - 2 * t), (y - PHI * s), (z)))  # vertex 6 - 8
            vertexes.append(
                ((x + s - t * (1 - PHI)), (y - PHI * s + PHI * t), (z + t))
            )  # vertex 6 - 9
            vertexes.append(
                ((x + s - t * (1 - PHI)), (y - PHI * s + PHI * t), (z - t))
            )  # vertex 6 - 10

            vertexes.append(
                ((x - s + t * (1 - PHI)), (y + PHI * s - PHI * t), (z + t))
            )  # vertex 7 - 11
            vertexes.append(
                ((x - s + t * (1 - PHI)), (y + PHI * s - PHI * t), (z - t))
            )  # vertex 7 - 12

            vertexes.append(
                ((x - s + t * (1 - PHI)), (y - PHI * s + PHI * t), (z + t))
            )  # vertex 8 - 11
            vertexes.append(
                ((x - s + t * (1 - PHI)), (y - PHI * s + PHI * t), (z - t))
            )  # vertex 8 - 12

            vertexes.append(((x + PHI * s), (y), (z + s - 2 * t)))  # vertex 9 - 10

            vertexes.append(((x - PHI * s), (y), (z + s - 2 * t)))  # vertex 11 - 12

        self.vertices = vertexes


################


class Dodeca(Entity3D):
    vertex_connections: list[tuple[int, int]] = [
        (0, 8),
        (0, 12),
        (0, 16),
        (1, 9),
        (1, 12),
        (1, 17),
        (2, 10),
        (2, 13),
        (2, 16),
        (3, 11),
        (3, 13),
        (3, 17),
        (4, 8),
        (4, 14),
        (4, 18),
        (5, 9),
        (5, 14),
        (5, 19),
        (6, 10),
        (6, 15),
        (6, 18),
        (7, 11),
        (7, 15),
        (7, 19),
    ]

    def __init__(
        self,
        position: Point3F,
        size: float,
        angle: Point3F,
        color: RGB = RGB(),
        movMatrix: Point3F = (0, 0, 0),
        rotMatrix: Point3F = (0, 0, 0),
        vertices: list[Point3F] = [],
    ):
        Entity3D.__init__(
            self,
            position=position,
            size=size,
            angle=angle,
            movMatrix=movMatrix,
            rotMatrix=rotMatrix,
            vertices=vertices,
            color=color,
        )
        self.name = "Dodecahedron"

    def get_diameter(self) -> float:
        # similar to ico?
        return self.size * 2 * PHI

    def calc_main_vertexes(self, apply: bool = False) -> list[Point3F]:
        vertexes = []
        x, y, z = self.position
        s = self.size

        vertexes.append((x + s, y + s, z + s))  # vertex 1
        vertexes.append((x + s, y - s, z + s))  # vertex 2
        vertexes.append((x + s, y + s, z - s))  # vertex 3
        vertexes.append((x + s, y - s, z - s))  # vertex 4
        vertexes.append((x - s, y + s, z + s))  # vertex 5
        vertexes.append((x - s, y - s, z + s))  # vertex 6
        vertexes.append((x - s, y + s, z - s))  # vertex 7
        vertexes.append((x - s, y - s, z - s))  # vertex 8

        vertexes.append((x, y + PHI * s, z + I_PHI * s))  # vertex 9
        vertexes.append((x, y - PHI * s, z + I_PHI * s))  # vertex 10
        vertexes.append((x, y + PHI * s, z - I_PHI * s))  # vertex 11
        vertexes.append((x, y - PHI * s, z - I_PHI * s))  # vertex 12

        vertexes.append((x + I_PHI * s, y, z + PHI * s))  # vertex 13
        vertexes.append((x + I_PHI * s, y, z - PHI * s))  # vertex 14
        vertexes.append((x - I_PHI * s, y, z + PHI * s))  # vertex 15
        vertexes.append((x - I_PHI * s, y, z - PHI * s))  # vertex 16

        vertexes.append((x + PHI * s, y + I_PHI * s, z))  # vertex 17
        vertexes.append((x + PHI * s, y - I_PHI * s, z))  # vertex 18
        vertexes.append((x - PHI * s, y + I_PHI * s, z))  # vertex 19
        vertexes.append((x - PHI * s, y - I_PHI * s, z))  # vertex 20

        if apply:
            self.vertices = vertexes

        return vertexes

    def calc_legacy_voxels(self):
        # TODO: this should also check for velocity / previous position
        if self.is_lazy() and self.vertices and len(self.vertices) > 0:
            return

        vertexes = self.calc_main_vertexes()
        x, y, z = self.position
        s = self.size

        # TODO: create a mapping of segments that are joined and use that instead.
        # Instead of looping through the size, we print the line mapped to a char to the screen right away! Should be ok if we do it in order of closeness, right? TODO: order vertexer in order of closeness!
        for t in range(round(s)):
            vertexes.append(
                ((x + s - t), (y + s - t * (1 - PHI)), (z + s - t * (1 - I_PHI)))
            )  # vertex 1 - 9
            vertexes.append(
                ((x + s - t * (1 - I_PHI)), (y + s - t), (z + s - t * (1 - PHI)))
            )  # vertex 1 - 13
            vertexes.append(
                ((x + s - t * (1 - PHI)), (y + s - t * (1 - I_PHI)), (z + s - t))
            )  # vertex 1 - 17

            vertexes.append(
                ((x + s - t), (y - s + t * (1 - PHI)), (z + s - t * (1 - I_PHI)))
            )  # vertex 2 - 10
            vertexes.append(
                ((x + s - t * (1 - I_PHI)), (y - s + t), (z + s - t * (1 - PHI)))
            )  # vertex 2 - 13
            vertexes.append(
                ((x + s - t * (1 - PHI)), (y - s + t * (1 - I_PHI)), (z + s - t))
            )  # vertex 2 - 18 3HBE

            vertexes.append(
                ((x + s - t), (y + s - t * (1 - PHI)), (z - s + t * (1 - I_PHI)))
            )  # vertex 3 - 11
            vertexes.append(
                ((x + s - t * (1 - I_PHI)), (y + s - t), (z - s + t * (1 - PHI)))
            )  # vertex 3 - 14
            vertexes.append(
                ((x + s - t * (1 - PHI)), (y + s - t * (1 - I_PHI)), (z - s + t))
            )  # vertex 3 - 17 4CEI

            vertexes.append(
                ((x + s - t), (y - s + t * (1 - PHI)), (z - s + t * (1 - I_PHI)))
            )  # vertex 4 - 12
            vertexes.append(
                ((x + s - t * (1 - I_PHI)), (y - s + t), (z - s + t * (1 - PHI)))
            )  # vertex 4 - 14
            vertexes.append(
                ((x + s - t * (1 - PHI)), (y - s + t * (1 - I_PHI)), (z - s + t))
            )  # vertex 4 - 18 59FJ

            vertexes.append(
                ((x - s + t), (y + s - t * (1 - PHI)), (z + s - t * (1 - I_PHI)))
            )  # vertex 5 - 9
            vertexes.append(
                ((x - s + t * (1 - I_PHI)), (y + s - t), (z + s - t * (1 - PHI)))
            )  # vertex 5 - 15
            vertexes.append(
                ((x - s + t * (1 - PHI)), (y + s - t * (1 - I_PHI)), (z + s - t))
            )  # vertex 5 - 19 6AFK

            vertexes.append(
                ((x - s + t), (y - s + t * (1 - PHI)), (z + s - t * (1 - I_PHI)))
            )  # vertex 6 - 10
            vertexes.append(
                ((x - s + t * (1 - I_PHI)), (y - s + t), (z + s - t * (1 - PHI)))
            )  # vertex 6 - 15
            vertexes.append(
                ((x - s + t * (1 - PHI)), (y - s + t * (1 - I_PHI)), (z + s - t))
            )  # vertex 6 - 20 7BGJ

            vertexes.append(
                ((x - s + t), (y + s - t * (1 - PHI)), (z - s + t * (1 - I_PHI)))
            )  # vertex 7 - 11
            vertexes.append(
                ((x - s + t * (1 - I_PHI)), (y + s - t), (z - s + t * (1 - PHI)))
            )  # vertex 7 - 16
            vertexes.append(
                ((x - s + t * (1 - PHI)), (y + s - t * (1 - I_PHI)), (z - s + t))
            )  # vertex 7 - 19 8CGK

            vertexes.append(
                ((x - s + t), (y - s + t * (1 - PHI)), (z - s + t * (1 - I_PHI)))
            )  # vertex 8 - 12
            vertexes.append(
                ((x - s + t * (1 - I_PHI)), (y - s + t), (z - s + t * (1 - PHI)))
            )  # vertex 8 - 16
            vertexes.append(
                ((x - s + t * (1 - PHI)), (y - s + t * (1 - I_PHI)), (z - s + t))
            )  # vertex 8 - 20

            vertexes.append(((x), (y + PHI * s), (z + I_PHI * s - 2 * I_PHI * t)))  # vertex 9 - 11
            vertexes.append(((x), (y - PHI * s), (z + I_PHI * s - 2 * I_PHI * t)))  # vertex 10 - 12
            vertexes.append(((x + I_PHI * s - 2 * I_PHI * t), (y), (z - PHI * s)))  # vertex 13 - 15
            vertexes.append(((x + I_PHI * s - 2 * I_PHI * t), (y), (z + PHI * s)))  # vertex 14 - 16
            vertexes.append(((x + PHI * s), (y + I_PHI * s - 2 * I_PHI * t), (z)))  # vertex 17 - 18
            vertexes.append(((x - PHI * s), (y + I_PHI * s - 2 * I_PHI * t), (z)))  # vertex 19 - 20

        self.vertices = vertexes
        self.apply_rotations()


####


"""
CUSTOMSHITTT
"""


# TODO: brokeeeen, fix!
class F_Letter(Entity3D):
    def __init__(
        self,
        position: Point3F,
        size: float,
        angle: Point3F,
        color: RGB,
        movMatrix=(0, 0, 0),
        rotMatrix=(0, 0, 0),
        vertices: list[Point3F] = [],
    ):
        Entity3D.__init__(
            self,
            position=position,
            size=size,
            angle=angle,
            movMatrix=movMatrix,
            rotMatrix=rotMatrix,
            vertices=vertices,
            color=color,
        )

    def calc_legacy_voxels(self):
        # TODO: this should also check for velocity / previous position
        # if self.is_lazy() and self.objVertexes and len(self.objVertexes) > 0:
        #     return

        vertexes = []
        s = self.size

        letter_points: list[list[float]] = [
            [0, 0],
            [0, 6],
            [3, 6],
            [3, 5],
            [1, 5],
            [1, 4],
            [3.5, 4],
            [3.3, 3],
            [1, 3],
            [1, 0],
        ]

        for l_index, l_point in enumerate(letter_points):
            x_l, y_l = l_point
            prev_point_index = len(letter_points) - 1 if l_index == 0 else l_index - 1
            prev_x_l, prev_y_l = letter_points[prev_point_index]

            # Add main points
            vertexes.append(list(add_triplet((x_l, y_l, 0), self.position)))

            for x_v, y_v, z_v in vertexes:
                pass
                # TODO: debug this shit
                # Vertical line down
                # for t in range(s):
                #     vertexes.append([x_v, y_v, z_v - t])
                #     vertexes.append(
                #         (
                #             (x_l * (s - t) + prev_x_l * t) / s,
                #             (y_l * (s - t) + prev_y_l * t) / s,
                #             z_v,
                #         )
                #     )

        self.vertices = vertexes
        self.apply_rotations()
