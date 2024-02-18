class Character:
    def __init__(self, name, allegiance, pv, image, wincondition, power):
        self.name = name
        self.allegiance = allegiance
        self.pv = pv
        self.image = image
        self.wincondition = wincondition
        self.power = power

    def get_card(self):
        message = self.name + ", " + self.allegiance + ", " + str(self.pv) + "PV\n**Condition de victoire :** " + self.wincondition + "\n**Pouvoir :** " + self.power
        return message