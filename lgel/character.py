class Character:
    def __init__(self, name, wolf, priority, image, text):
        self.name = name
        self.wolf = wolf
        self.priority = priority
        self.image = image
        self.text = text

    def get_card(self):
        message = self.name + ",\n" + self.text
        return message