import asyncio
import discord
import random
from visionCard.visionCard_function import get_all_visionCard

class Game:
    def __init__(self, players):
        self.players = players  #[[player, character], [player2, character], ...]

        self.location = []

        self.vision_card_deck = get_all_visionCard()
        random.shuffle(self.vision_card_deck)
        self.vision_card_deck_used = []
        self.dark_card_deck = []
        self.dark_card_deck_used = []
        self.light_card_deck = []
        self.light_card_deck_used = []

    async def draw_vision(self, user, ctx, client):
        user_local_id = 0
        for i in range(len(self.players)):
            if (self.players[i][0].name == user.name):
                user_local_id = i
        
        # if deck is empty
        if (len(self.vision_card_deck) <= 0):
            self.vision_card_deck = self.vision_card_deck_used
            random.shuffle(self.vision_card_deck)
            self.vision_card_deck_used = []

        card_drawn = self.vision_card_deck.pop(0)
        self.vision_card_deck_used.append(card_drawn)
        emoji_list=["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
        nb = len(self.players)
        player_list_message = ""
        for i in range(nb):
            player_list_message += emoji_list[i] + " : "
            player_list_message += self.players[i][0].name + "\n"

        response = await self.players[user_local_id][0].send("Vous avez piochez :\n\n" + card_drawn.get_card() + "\n\nA qui voulez-vous la donner ?\n" + player_list_message, file=discord.File(card_drawn.image))

        # allow to send the card to another player
        for i in range(nb):
            await response.add_reaction(emoji_list[i])

        def check(reaction, user):
            return str(reaction.emoji) in emoji_list
        
        receiver_local_id = random.randint(0, nb-1)
        try:
            reaction, _ = await client.wait_for('reaction_add', timeout=120.0, check=check)
            match reaction.emoji:
                case '1️⃣':
                    receiver_local_id = 0
                    pass
                case '2️⃣':
                    receiver_local_id = 1
                    pass
                case '3️⃣':
                    receiver_local_id = 2
                    pass
                case '4️⃣':
                    receiver_local_id = 3
                    pass
                case '5️⃣':
                    receiver_local_id = 4
                    pass
                case '6️⃣':
                    receiver_local_id = 5
                    pass
                case '7️⃣':
                    receiver_local_id = 6
                    pass
                case '8️⃣':
                    receiver_local_id = 7
                    pass
        
        except asyncio.TimeoutError:
            await self.players[user_local_id][0].send("Aucune réponse ; un joueur aléatoire a été choisi")

        # send the card to the other player
        await self.players[receiver_local_id][0].send("Vous avez reçu de la part de " + self.players[user_local_id][0].name + " :\n\n" + card_drawn.get_card(), file=discord.File(card_drawn.image))
        
        # send comfirmation in mp to the sender
        await self.players[user_local_id][0].send("Carte envoyé à " + self.players[receiver_local_id][0].name)

        # send message to the global channel
        await ctx.send(self.players[user_local_id][0].name + " a donner une carte vision à " + self.players[receiver_local_id][0].name)