import asyncio
import discord
import lgel.characters_functions as cf
import random
from lgel.player import Player
from collections import Counter

# maybe clean later, for now we follow the soso popo in raw caveman ways
SOSO_used_life = False
SOSO_used_death = False

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
    game_on = True
    # one night and day each loop
    while game_on:
        message = await message.reply("La nuit tombe.")
        message = await activate_vovo(message, players, client)
        message, wolves_target = await activate_wolves(message, players, client)
        message, soso_kill, wolves_kill = await activate_soso(message, players, client, wolves_target)
        message = await message.reply("Le village se réveille.")
        if wolves_kill != None:
            game_on = not await kill_player(message, client, players, couple, wolves_kill)
        if soso_kill != None:
            game_on = not await kill_player(message, client, players, couple, soso_kill)
        message = await message.reply("Il est temps pour les villageois de voter ! Qui sera pendu ce soir ?\nVous avez 3min.\n*vote [name]*\n" + get_player_list(get_all_alive(players)))
        
        # we check on all players alive
        def check(m):
                return any(m.author == player.user for player in get_all_alive(players))
        start_time = asyncio.get_event_loop().time()
        ten_mark = False
        thirty_mark = False
        sixty_mark = False
        # voting phase
        while asyncio.get_event_loop().time() - start_time < 180:
            # some timer help, to alert of time end
            if asyncio.get_event_loop().time() - start_time > 120:
                if asyncio.get_event_loop().time() - start_time > 150:
                    if asyncio.get_event_loop().time() - start_time > 170:
                        if not ten_mark:
                            message = await message.reply("10s restant !")
                            ten_mark = True
                    else:
                        if not thirty_mark:
                            message = await message.reply("30s restant !")
                            thirty_mark = True
                else :
                    if not sixty_mark:
                        message = await message.reply("60s restant !")
                        sixty_mark = True
            try:
                msg = await client.wait_for('message', timeout=1.0, check=check) # short timeout as we're in a loop and need to check time passing
                # check if it is a vote
                if msg.content.startswith("vote "):
                    targetString = msg.content[len("vote "):].strip()
                    targetPlayer = get_player_by_name(targetString, players)
                    if targetPlayer == None:
                        await msg.reply("Pseudo non reconnu, réessayez")
                        continue
                    # find the player who send the vote to add it
                    for player in players:
                        if player.user == msg.author:
                            player.Vote = targetPlayer
                    await msg.reply(msg.author.mention + " a voté contre " + targetPlayer.user.mention + " !")
            except asyncio.TimeoutError:
                pass
        # vote calcul
        votes = []
        for player in players:
            if player.Vote != None:
                votes.append(player.Vote)
                player.Vote = None
        counters = Counter(votes)
        winners = [player for player, count in counters.items() if count == max(counters.values())]
        if len(winners) != 1:
            await message.reply("Egalité ! Pas de mort aujourd'hui.")
        else:
            # we have a winner !... rip him
            await message.reply("Vous décidez de pendre " + winners[0].user.mention)
            game_on = not (await kill_player(message, client, players, couple, winners[0]))


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
                    couple1.isCouple = True
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
                        couple2.isCouple = True
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
            
# handle voyante turn
async def activate_vovo(message, players, client):
    for player in players:
        # found a vovo
        if player.character.name == "La Voyante" and player.alive == True:
            message = await message.reply("La voyante espionne quelqu'un...")

            # MP
            await player.user.send("Vous pouvez espionner quelqu'un ! :\n" + get_player_list(get_all_alive(players)))
            attempts = 0
            # Get target by asking
            while attempts < 3:
                target = await get_player_named_by_player(player, players, client)
                if target is not None:
                    # get the player, send the message and end the activation, by returning current main channel message
                    await player.user.send(target.user.name + " est : " + target.character.name )
                    return message
                else:
                    await player.user.send("Joueur non reconnue, réessayez.")
                attempts += 1
                if attempts == 3:
                    await player.user.send("Trop d'erreur, tampis !")
    return message

# handle wolves turn
async def activate_wolves(message, players, client):
    message = await message.reply("Les loups vont décider qui éliminer...")
    wolves = []
    # get all alive wolves
    for player in players:
        if player.character.wolf == True and player.alive == True:
            await player.user.send("Vous avez 30s pour discuter avec les autres loups et dévorer quelqu'un !\n(tapez 'manger [pseudo]' pour manger !)\n" + get_player_list(get_all_alive(players)))
            wolves.append(player)

    # we get all wolves chat 
    def check(m):
            return any(m.author == wolf.user for wolf in wolves)
    try:
        start_time = asyncio.get_event_loop().time()
        # wolf voting phase
        while asyncio.get_event_loop().time() - start_time < 30:
            msg = await client.wait_for('message', timeout=30, check=check)
            is_vote = False
            # check if it is a vote
            if msg.content.startswith("manger "):
                is_vote = True
                targetString = msg.content[len("manger "):].strip()
                targetPlayer = get_player_by_name(targetString, players)
                # stop here if we didn't recognize the player, not sending the message to others
                if targetPlayer == None:
                    await msg.author.send("Pseudo non reconnu, réessayez")
                    continue
                # find the player who send the vote to add it
                for player in players:
                    if player.user == msg.author:
                        player.Vote = targetPlayer
                await msg.author.send("*Vous avez décidé de dévorer " + targetPlayer.user.name + "*")
                
            # Relay all wolves messages to all other wolves
            for wolf in wolves:
                if wolf.user != msg.author:
                    await wolf.user.send(msg.author.name + " : " + msg.content)
    except asyncio.TimeoutError:
        pass
    # main thread info
    message = await message.reply("Les loups ont fait leur choix.")
    # vote calcul
    votes = []
    for wolve in wolves:
        if wolve.Vote != None:
            votes.append(wolve.Vote)
            wolve.Vote = None
    counters = Counter(votes)
    winners = [player for player, count in counters.items() if count == max(counters.values())]
    if len(winners) > 1:
        for wolf in wolves:
            await wolf.user.send("Egalité ! Personne ne mange.")
    elif len(winners) == 0:
        for wolf in wolves:
            await wolf.user.send("Personne n'a voté.")
    else:
        # we have a winner !... rip him
        for wolf in wolves:
            await wolf.user.send("Vous décidez de manger : " + winners[0].user.name)
            return message, winners[0]
    # no winner, rip wolves
    return message, None

# handle soso turn
async def activate_soso(message, players, client, wolves_target):
    global SOSO_used_death
    global SOSO_used_life
    for player in players:
        # found a soso
        if player.character.name == "La Sorcière" and player.alive == True:
            # check if all potions used first.
            if (SOSO_used_death and SOSO_used_life):
                message = await message.reply("La sorcière a utilisé toutes ses potions.")
                return message, None, wolves_target

            message = await message.reply("La sorcière décide si elle veut utilisé ses potions...")
            # check target of wolves
            gonna_die_msg = "Les loups ne tuent personne ce soir."
            if wolves_target != None:
                gonna_die_msg = wolves_target.user.name + " va se faire dévorer ce soir !"

            # MP
            mp = await player.user.send("Vous pouvez utiliser vos potions ! :\n*Cliquez sur une des réactions*" + get_player_list(get_all_alive(players))
                                        + "\n" + gonna_die_msg)
            await mp.add_reaction('❌')
            if not (SOSO_used_life) or wolves_target != None:
                await mp.add_reaction('🩹')
            if not (SOSO_used_death):
                await mp.add_reaction('🔪')
            if not (SOSO_used_death or SOSO_used_life):
                await mp.add_reaction('2️⃣')

            def check(reaction, user):
                emoji_list = ['🩹', '🔪', '❌', '2️⃣']
                return player.user == user and str(reaction.emoji) in emoji_list
            
            try:
                reaction, _ = await client.wait_for('reaction_add', timeout=30.0, check=check)
                match reaction.emoji:
                    case '❌':
                        await player.user.send("Vous n'utilisez aucune potion cette nuit.")
                        return
                    case '🩹':
                        if SOSO_used_life or wolves_target == None:
                            await player.user.send('*Nice try, cheater :p*')

                        await player.user.send("Vous sauvez " + wolves_target.user.name)
                        wolves_target = None
                        SOSO_used_life = True
                    case '🔪':
                        if SOSO_used_death:
                            await player.user.send('*Nice try, cheater :p*')

                        await player.user.send("Qui souhaitez vous tuer ?\n" + get_player_list(get_all_alive(players)))
                        attempts = 0
                        # Get target by asking soso
                        while attempts < 3:
                            target = await get_player_named_by_player(player, players, client)
                            if target is not None:
                                # get the player, send the message and end the activation, by returning current main channel message
                                await player.user.send("Vous tuez froidement " + target.user.name + " cette nuit.")
                                return message, target, wolves_target
                            else:
                                await player.user.send("Joueur non reconnue, réessayez.")
                            attempts += 1
                            if attempts == 3:
                                await player.user.send("Trop d'erreur, tampis !")
                        
                    case '2️⃣':
                        if not (SOSO_used_death or SOSO_used_life):
                            await player.user.send('*Nice try, cheater :p*')
                        # do both, so no break
                        await player.user.send("Vous sauvez " + wolves_target.user.name)
                        wolves_target = None
                        await player.user.send("Qui souhaitez vous tuer ?\n" + get_player_list(get_all_alive(players)))
                        attempts = 0
                        # Get target by asking soso
                        while attempts < 3:
                            target = await get_player_named_by_player(player, players, client)
                            if target is not None:
                                # get the player, send the message and end the activation, by returning current main channel message
                                await player.user.send("Vous tuez froidement " + target.user.name + " cette nuit.")
                                return message, target, wolves_target
                            else:
                                await player.user.send("Joueur non reconnue, réessayez.")
                            attempts += 1
                            if attempts == 3:
                                await player.user.send("Trop d'erreur, tampis !")
                
            except asyncio.TimeoutError:
                await player.user.send("Aucune réponse ; pas de potion cette nuit !")
    return message, None, wolves_target

# handle the kill of a player, return if end_game
async def kill_player(message, client, players, couple, player_to_kill):
    message = await message.reply(player_to_kill.user.name + " est mort !")
    player_to_kill.alive = False

    # check if couple
    if player_to_kill.isCouple:
        other_couple = couple[0]
        if couple[0] == player_to_kill:
            other_couple = couple[1]
        if other_couple.alive:
            message.reply(player_to_kill.user.name + " était en couple avec " + other_couple.user.name + ", qui le/la suis dans la tombe !")
            await kill_player(message, client, players, couple, other_couple)

    # check if it is chassou
    if player_to_kill.character.name == "Le Chasseur":
        message = await message.reply("C'était le chasseur ! Avant de faire son dernier souffle, il peut décider de tirer sur quelqu'un...")
        await player_to_kill.user.send("Vous êtes mort ! Mais pas tout seul, décidez qui tuer :\n" + get_player_list(get_all_alive(players)))
        attempts = 0
        # Get target by asking chassou
        while attempts < 3:
            target = await get_player_named_by_player(player_to_kill, players, client)
            if target is not None:
                # BAM, he ded
                await message.reply(player_to_kill.user.name + " abat " + target.user.name + " dans un dernier souffle.")
                await kill_player(message, client, players, couple, target)
                # stop here the attempts
                attempts = 4
            else:
                await player_to_kill.user.send("Joueur non reconnu, réessayez.")
            attempts += 1
            if attempts == 3:
                await player_to_kill.user.send("Trop d'erreur, tampis !")

    else:
        message = await message.reply(player_to_kill.user.name + " était en faite " + player_to_kill.character.name)
    return await check_victory(message, players)

# check if end game is now, return if end_game
async def check_victory(message, players):
    alive_players = get_all_alive(players)
    # separate all player by victory condition
    alive_wolves = []
    alive_villagers = []
    alive_couple = []
    for player in alive_players:
        if player.isCouple:
            alive_couple.append(player)

        if player.character.wolf:
            alive_wolves.append(player)
        else:
            alive_villagers.append(player)
    
    # first, check the couple ; if there is three player left and they are alive, they win
    if len(alive_couple) != 0 and (len(alive_players) <= 3):
        message = await end_game(message, players, "couple")
        return True
    # then, check the villagers ; if there is no wolves left, and there is at least one villager still alive, they win
    if len(alive_wolves) == 0 and len(alive_villagers) > 0:
        message = await end_game(message, players, "villagers")
        return True
    # finally, check wolves. If they are more numerous than villagers, they win
    if len(alive_wolves) > len(alive_villagers):
        message = await end_game(message, players, "wolves")
        return True
    # if everyone is dead, it is a draw
    if len(alive_players) == 0:
        message = await end_game(message, players, "draw")
        return True
    # else, not the end
    return False

# end the game, depending how in condition
async def end_game(message, players, condition):
    winners = []
    losers = []
    if condition == "villagers":
        await message.reply("Tous les loups sont morts, les villageois ont gagné !")
        winners = [player for player in players if not player.wolf]
        losers = [player for player in players if player.wolf]
    
    elif condition == "wolves":
        await message.reply("Tous les villageois sont morts, les loups ont gagné !")
        winners = [player for player in players if player.wolf]
        losers = [player for player in players if not player.wolf]
    
    elif condition == "couple":
        await message.reply("Le couple a gagné seul !")
        winners = [player for player in players if player.isCouple]
        losers = [player for player in players if not player.isCouple]
    
    elif condition == "draw":
        await message.reply("Tout le monde est mort, pas de gagnant !")
        losers = players
    
    end_msg = "GAGNANTS\n"
    for winner in winners:
        end_msg += winner.user.mention + " qui était " + winner.character.name + "\n"
    end_msg += "PERDANTS\n"
    for loser in losers:
        end_msg += loser.user.mention + " qui était " + loser.character.name + "\n"
    await message.reply(end_msg)



    
    


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
def get_all_alive(players):
    player_list = []
    for player in players:
        if player.alive == True:
            player_list.append(player)
    return player_list
