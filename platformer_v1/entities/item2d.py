from entities.base import Entity2D


# TODO: do something
class Item2D(Entity2D):
    def __init__(self, item_type):
        Entity2D.__init__(self)
        self.item_type = item_type
