class Player:
    def __init__(self, user):
        self.user = user
        self.character = None
        self.alive = True
        self.isWolf = False
        self.isCouple = False
        self.Vote = None
        