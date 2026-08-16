from dataclasses import dataclass

from model.base import DistVector3D, Point3
from model.theme import RGB
from three_d_renderer.entities.base3d import Entity3D


# TODO: Move
@dataclass
class Vertex3:
    # Index of vertex in the Entity (check calc_vertex_v2 method)
    index: int
    point: Point3


@dataclass
class RenderingObj:
    entity_idx: int
    entity: Entity3D
    vertex: Vertex3
    dist_vector: DistVector3D


@dataclass
class SubpixelContribution:
    distance_from_spec: float
    """
    Usage is calculated based on how close the line passes to the center of the pixel
    e.g. at pixel (x1, y1), if the line crosses at:
    - (x1, y1) -> 0% usage, it barely touches the pixel
    - (x1 + 0.5, y1 + 0.5) -> 100% usage, the line pases exactly through the middle of the pixel
    """
    pixel_usage_ratio: float
    color: RGB | None = None


@dataclass
# Represents the contribution of a line segment to filling in the pixel's content
class PixelContribution:
    upper_subpixel: SubpixelContribution
    lower_subpixel: SubpixelContribution


@dataclass
class ScreenData:
    contributions: list[SubpixelContribution]
