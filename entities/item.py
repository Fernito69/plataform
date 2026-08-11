from entities.entity import Entity


class Item(Entity):
    def __init__(self, item_type):
        Entity.__init__(self)
        self.item_type = item_type
