from model.base import Point2
from model.theme import Theme


class ScenarioPiece:
    theme: Theme

    def __init__(self, theme: Theme = Theme()):
        self.theme = theme


class RectanglePiece(ScenarioPiece):
    vertices: tuple[Point2, Point2]

    def __init__(self, vertices: tuple[Point2, Point2], theme: Theme = Theme()):
        ScenarioPiece.__init__(self, theme)
        self.vertices = vertices

    def get_render_info(self):
        pass
