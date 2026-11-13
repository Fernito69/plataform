import math
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from physics2d.model.shared import BoundingBox, RenderInfo
from physics2d.shape.base import Shape

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

from model.theme import RGB

type BM = list[list[RGB | None]]
BLACK = RGB(0, 0, 0, opacity=0)


class Bitmap(Shape):
    bitmap: BM
    origin: PointF

    def __init__(
        self,
        engine: "Physics2D",
        origin: PointF,
        bitmap: BM,
        angle: float = 0,
        x_scale: float = 1,
        y_scale: float = 1,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        floating_multi: float = 0,
        density: float = 1,
        is_collideable: bool = False,
    ):
        self.origin = origin
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.bitmap = bitmap
        self._update_center_of_mass()
        self.density = density
        self.volume = self._get_width() * self._get_height()
        self.weight = self.volume * self.density

        super().__init__(
            angle=angle,
            own_gravity=own_gravity,
            initial_angular_velocity=initial_angular_velocity,
            affected_by_gravity=affected_by_gravity,
            floating_multi=floating_multi,
            initial_velocity=initial_velocity,
            center_of_mass=self.center_of_mass,
            name="Bitmap",
            volume=self.volume,
            density=self.density,
            is_collideable=is_collideable,
            engine=engine,
        )

    def _update_center_of_mass(self) -> None:
        self.center_of_mass = self.origin + PointF(
            x=self._get_width(),
            y=self._get_height(),
        )

    def _get_width(self, scaled: bool = True) -> float:
        return (self.x_scale if scaled else 1) * len(self.bitmap[0])

    def _get_height(self, scaled: bool = True) -> float:
        return (self.y_scale if scaled else 1) * len(self.bitmap)

    def get_bounding_box(self) -> BoundingBox | None:
        min_x, min_y, _ = self.origin

        return BoundingBox(
            min_x=min_x,
            min_y=min_y,
            max_x=min_x + self._get_width(),
            max_y=min_y - self._get_height(),
        )

    def get_render_info(self) -> list[RenderInfo]:
        # TODO: implement scale. For now, ignore it
        width: int = int(self._get_width(scaled=False))
        height: int = int(self._get_height(scaled=False))

        render_info: list[RenderInfo] = []

        range_x = range(math.floor(self.origin.x), math.ceil(self.origin.x + width))
        range_y = range(math.floor(self.origin.y), math.ceil(self.origin.y + height))

        d_x: float = self.origin.x % 1
        d_y: float = self.origin.y % 1

        for x_idx, x_screen in enumerate(range_x):
            for y_idx, y_screen in enumerate(range_y):
                pixel_color: RGB | None = (
                    self.bitmap[y_idx][x_idx]
                    if y_idx <= height - 1 and x_idx <= width - 1
                    else BLACK
                )

                if not pixel_color:
                    continue

                point = PointF(x=x_screen, y=y_screen)

                # find out color contribution per sub-pixel "quadrant"
                q1_contrib = (1 - d_x) * (1 - d_y)
                q2_contrib = d_x * (1 - d_y)
                q3_contrib = d_x * d_y
                q4_contrib = (1 - d_x) * d_y

                out_of_range: bool = y_idx > height - 1 or x_idx > width - 1

                # TODO: redo!!!!
                q1_color = pixel_color
                q2_color = BLACK if x_idx < 1 or out_of_range else self.bitmap[y_idx][x_idx - 1]
                q3_color = (
                    BLACK
                    if x_idx < 1 or y_idx < 1 or out_of_range
                    else self.bitmap[y_idx - 1][x_idx - 1]
                )
                q4_color = BLACK if y_idx < 1 or out_of_range else self.bitmap[y_idx - 1][x_idx]

                # self._engine.game._display.debug_log(
                #     f"quadrants = {q1_contrib + q2_contrib + q3_contrib + q4_contrib}"
                # )

                # TODO: STUPID; do better
                factor = (
                    q1_contrib * (1 if q1_color != BLACK else 0)
                    + q2_contrib * (1 if q2_color != BLACK else 0)
                    + q3_contrib * (1 if q3_color != BLACK else 0)
                    + q4_contrib * (1 if q4_color != BLACK else 0)
                )
                distance_to_pixel_center = 0
                pixel_color = (
                    q1_contrib * (q1_color or BLACK)
                    + q2_contrib * (q2_color or BLACK)
                    + q3_contrib * (q3_color or BLACK)
                    + q4_contrib * (q4_color or BLACK)
                )

                render_info.append(
                    RenderInfo(
                        point=point,
                        distance_to_pixel_center=distance_to_pixel_center,
                        color=pixel_color,
                    )
                )

        # for y_idx, row in enumerate(bitmap):
        #     for x_idx, pixel_color in enumerate(row):
        #         if not pixel_color:
        #             continue

        #         point = PointF(
        #             x=self.origin.x + x_idx,
        #             y=self.origin.y + y_idx,
        #         )
        #         # two cases: whether it's a perfect match with the pixel or not
        #         d_x: float = self.origin.x % 1
        #         d_y: float = self.origin.y % 1
        #         color: RGB | None = pixel_color

        #         if abs(d_x) < ALMOST_ZERO and abs(d_y) < ALMOST_ZERO:
        #             distance_to_pixel_center = 0
        #         else:
        #             # find out color contribution per sub-pixel "quadrant"
        #             BLACK = RGB(0, 0, 0)

        #             q1_contrib = (1 - d_x) * (1 - d_y)
        #             q2_contrib = d_x * (1 - d_y)
        #             q3_contrib = d_x * d_y
        #             q4_contrib = (1 - d_x) * d_y

        #             q1_color = BLACK if x_idx < 1 else bitmap[y_idx][x_idx - 1]
        #             q2_color = pixel_color
        #             q3_color = BLACK if x_idx < 1 or y_idx < 1 else bitmap[y_idx - 1][x_idx - 1]
        #             q4_color = BLACK if y_idx < 1 else bitmap[y_idx - 1][x_idx]

        #             # TODO: STUPID; do better
        #             distance_to_pixel_center = 1 - (
        #                 q1_contrib * (1 if q1_color != BLACK else 0)
        #                 + q2_contrib * (1 if q2_color != BLACK else 0)
        #                 + q3_contrib * (1 if q3_color != BLACK else 0)
        #                 + q4_contrib * (1 if q4_color != BLACK else 0)
        #             )
        #             color = (
        #                 q1_contrib * (q1_color or BLACK)
        #                 + q2_contrib * (q2_color or BLACK)
        #                 + q3_contrib * (q3_color or BLACK)
        #                 + q4_contrib * (q4_color or BLACK)
        #             )

        #         render_info.append(
        #             RenderInfo(
        #                 point=point,
        #                 distance_to_pixel_center=distance_to_pixel_center,
        #                 color=color,
        #             )
        #         )

        return render_info

    def do_your_thing(self) -> None:
        return self._apply_movement()

    def _apply_movement(self) -> None:
        self.origin += self.velocity
        self._update_center_of_mass()
