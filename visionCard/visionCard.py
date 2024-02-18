class VisionCard:
    def __init__(self, name, description, image):
        self.name = name
        self.description = description
        self.image = image

    def get_card(self):
        message = "**" + self.name + "**\n" + self.description
        return message