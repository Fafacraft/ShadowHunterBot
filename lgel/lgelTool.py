import asyncio
import discord
import lgel.characters_functions as cf
import random
    

# players of type Player[]
async def chose_and_give_characters(players):
    nb_players = len(players)
    nb_wolf = int(nb_players/3) # third of the players or villagers, rounded down. 6 = 2 wolves. 8 = 2 wolves. 9 = 3 wolves. 12 = 4 wolves.
    nb_villagers = nb_players-nb_wolf
    all_characters = []

    wolves = []
    villagers = []
    possible_wolves = cf.get_all_wolf_characters()
    priority = 0
    while len(wolves) < nb_wolf and priority <=10:
        temp_char = cf.get_all_priority_characters(priority, possible_wolves)
        random.shuffle(temp_char)
        while len(wolves) < nb_wolf and len(temp_char) > 0:
            print(temp_char[0].name)
            wolves.append(temp_char[0])
            all_characters.append(temp_char[0])
            temp_char.pop(0)
        priority += 1


    possible_villagers = cf.get_all_villagers_characters()
    priority = 0
    while len(villagers) < nb_villagers and priority <=10:
        temp_char = cf.get_all_priority_characters(priority, possible_villagers)
        random.shuffle(temp_char)
        while len(villagers) < nb_villagers and len(temp_char) > 0:
            villagers.append(temp_char[0])
            all_characters.append(temp_char[0])
            temp_char.pop(0)
        priority += 1
    
    random.shuffle(all_characters)
    
    wolf_players_list = []
    for i in range(len(players)):
        players[i].character = all_characters[i]
        # send character in mp
        await players[i].user.send("Votre personnage est :\n\n" + players[i].character.get_card(), file=discord.File(players[i].character.image))
        if players[i].character.wolf:
            wolf_players_list.append(players[i])

    for player in wolf_players_list:
        player.isWolf = True
        await player.user.send("Voici la liste des loups :\n" + get_player_list(wolf_players_list))
            

    random.shuffle(all_characters)
    return all_characters
    


# this gets the name a player told (when he needs to choose from a list)
# returns a Player.
async def get_player_named_by_player(player, players, client):
    def check(m):
        return m.author == player.user

    try:
        msg = await client.wait_for('message', timeout = 30, check=check)
    except asyncio.TimeoutError:
        return None
    if (msg.content in get_playername_array(players)):
        return get_player_by_name(msg.content, players)
    else:
        return None

# get the player, or playername in python lists
def get_player_list(players):
    player_list = ""
    for player in players:
        player_list += "- " + player.user.name + "\n"
    return player_list
def get_playername_array(players):
    player_list = []
    for player in players:
        player_list.append(player.user.name)
    return player_list
def get_player_by_name(name, players):
    for player in players:
        if player.user.name == name:
            return player
    return None

# get all players alive from the players args, a python list of Player
def get_all_alive(players):
    player_list = []
    for player in players:
        if player.alive == True:
            player_list.append(player)
    return player_list
