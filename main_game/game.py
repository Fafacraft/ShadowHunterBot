class Game:
    def __init__(self, players):
        self.players = players

        self.location = []

        self.vision_card_deck = []
        self.vision_card_deck_used = []
        self.dark_card_deck = []
        self.dark_card_deck_used = []
        self.light_card_deck = []
        self.light_card_deck_used = []
