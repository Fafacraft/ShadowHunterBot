import asyncio
import discord
import lgel.characters_functions as cf
import random
from lgel.player import Player

async def start_lgel(players, message, client):
    nb_players = len(players)
    if (nb_players < 0): # DEBUG = at 3. At 0 to be able to play solo.
        await message.reply("Nombre insuffisant de joueur.")
        return
    if (nb_players > 18):
        await message.reply("Malheureusement, le jeu ne supporte pas plus de 18 joueurs actuellement.")
        return
    

    message = await message.reply("Bienvenue dans la partie. Joueurs ;\n" + get_player_list(players))

    all_characters, wolf_players_list, = await chose_and_give_characters(players)
    nb_sv = 0
    nb_wolf = 0
    i = 0
    for elm in all_characters:
        if elm.name == "Simple Villageois":
            nb_sv += 1
        if elm.name == "Loup-garou":
            nb_wolf += 1
    list_characters = "Les personnages ont été distribués ! Il y a dans cette partie ;\n- " + str(nb_sv) + " Simple Villageois\n- " + str(nb_wolf) + " Loup-garous\n"
    for elm in all_characters:
        if elm.name not in ["Simple Villageois", "Loup-garou"]:
            list_characters += "- " + elm.name + "\n"
    message = await message.reply(list_characters)


    couple = await cupidon_couple(message, players, client)
    # voleur if there is such thing, etc, all preplay
    await run_game(message, players, couple, client)

# let's run the game
async def run_game(message, players, couple, client):
    # TODO first, process the first night

    message = await message.reply("Le village se réveille.")

# players of type Player[]
async def chose_and_give_characters(players):
    nb_players = len(players)+5
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
            print(temp_char[0].name)
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
        await player.user.send("Voici la liste des loups :\n" + get_player_list(wolf_players_list))
            

    random.shuffle(all_characters)
    return all_characters, wolf_players_list

async def cupidon_couple(message, players, client):
    # cupidon
    couple=[]
    for player in players:
        if player.character.name == "Cupidon": 
            await message.reply("Cupidon tire ses flèches...")

            await player.user.send("Choisissez le premier amoureux :\n" + get_player_list(players))

            couple1 = None
            attempts = 0

            while attempts < 3:
                couple1 = await get_player_named_by_player(player, players, client)
                if couple1 is not None:
                    couple.append(couple1)
                    attempts = 4
                else:
                    await player.user.send("Joueur non reconnue, reessayez.")
                attempts += 1
                if attempts == 3:
                    await player.user.send("Trop d'erreur, pas de couple !")

                    

            if couple1 is not None:
                attempts = 0
                couple2 = None
                await player.user.send("Avec qui voulez-vous mettre en couple " + couple[0].name + " ?\n")
                while attempts < 3:
                    couple2 = await get_player_named_by_player(player, players, client)
                    if couple1 is not None:
                        couple.append(couple2)
                        attempts = 4
                    else:
                        await player.user.send("Joueur non reconnue, reessayez.")
                    attempts += 1
                    if attempts == 3:
                        await player.user.send("Trop d'erreur, pas de couple !")
            
            if couple1 is not None and couple2 is not None:
                await couple[0].send("Cupidon vous à mis en couple avec " + couple[1].name + " ! Votre destin est maintenant scellé avec elle ou lui, pour le bien... ou le pire !")
                await couple[1].send("Cupidon vous à mis en couple avec " + couple[0].name + " ! Votre destin est maintenant scellé avec elle ou lui, pour le bien... ou le pire !")
                #to our cupidon
                await player.user.send(couple[0].name + " et " + couple[1].name + " sont a présents amoureux et leur sort est scellé, pour le bien... ou le pire !")

    return couple
            


# what does this do again
async def get_player_named_by_player(player, players, client):
        def check(m):
            return m.author == player[0]

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
            return player.user
    return None
