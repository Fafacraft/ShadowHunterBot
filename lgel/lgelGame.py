import lgel.lgelTool as lt
import asyncio
import discord
import lgel.characters_functions as cf
import random
from lgel.player import Player
from collections import Counter

class lgelGame:
    def __init__(self, players, message, client):
        self.gameOn = True
        self.players = players
        self.currentMessage = message
        self.client = client
        self.SOSO_used_life = False
        self.SOSO_used_death = False

        self.couple = []
        self.wolves_target = None
        self.soso_target = None


    async def start_lgel(self):
        nb_players = len(self.players)
        if (nb_players < 3): # DEBUG = at 3. At 0 to be able to play solo.
            await self.currentMessage.reply("Nombre insuffisant de joueur.")
            return
        if (nb_players > 18):
            await self.currentMessage.reply("Malheureusement, le jeu ne supporte pas plus de 18 joueurs actuellement.")
            return
        

        self.currentMessage = await self.currentMessage.reply("Bienvenue dans la partie. Joueurs ;\n" + lt.get_player_list(self.players))

        all_characters = await lt.chose_and_give_characters(self.players)
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
        self.currentMessage = await self.currentMessage.reply(list_characters)


        await self.activate_cupidon()
        # voleur if there is such thing, etc, all preplay
        await self.run_game()


    # let's run the game
    async def run_game(self):
        # one night and day each loop
        while self.gameOn:
            self.currentMessage = await self.currentMessage.reply("La nuit tombe.")
            await self.activate_vovo()
            await self.activate_wolves()
            await self.activate_soso()
            self.currentMessage = await self.currentMessage.reply("Le village se réveille.")
            if self.wolves_target != None:
                await self.kill_player(self.wolves_target)
            if self.soso_target != None:
                await self.kill_player(self.soso_target)
            self.currentMessage = await self.currentMessage.reply("Il est temps pour les villageois de voter ! Qui sera pendu ce soir ?\nVous avez 3min.\n*vote [name]*\n" + lt.get_player_list(lt.get_all_alive(self.players)))
            
            # we check on all players alive
            def check(m):
                    return any(m.author == player.user for player in lt.get_all_alive(self.players))
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
                                self.currentMessage = await self.currentMessage.reply("10s restant !")
                                ten_mark = True
                        else:
                            if not thirty_mark:
                                self.currentMessage = await self.currentMessage.reply("30s restant !")
                                thirty_mark = True
                    else :
                        if not sixty_mark:
                            self.currentMessage = await self.currentMessage.reply("60s restant !")
                            sixty_mark = True
                try:
                    msg = await self.client.wait_for('message', timeout=1.0, check=check) # short timeout as we're in a loop and need to check time passing
                    # check if it is a vote
                    if msg.content.startswith("vote "):
                        targetString = msg.content[len("vote "):].strip()
                        targetPlayer = lt.get_player_by_name(targetString, self.players)
                        if targetPlayer == None:
                            await msg.reply("Pseudo non reconnu, réessayez")
                            continue
                        # find the player who send the vote to add it
                        for player in self.players:
                            if player.user == msg.author:
                                player.Vote = targetPlayer
                        await msg.reply(msg.author.mention + " a voté contre " + targetPlayer.user.mention + " !")
                except asyncio.TimeoutError:
                    pass
            # vote calcul
            votes = []
            for player in self.players:
                if player.Vote != None:
                    votes.append(player.Vote)
                    player.Vote = None
            counters = Counter(votes)
            winners = [player for player, count in counters.items() if count == max(counters.values())]
            if len(winners) != 1:
                await self.currentMessage.reply("Egalité ! Pas de mort aujourd'hui.")
            else:
                # we have a winner !... rip him
                await self.currentMessage.reply("Vous décidez de pendre " + winners[0].user.mention)
                await self.kill_player(winners[0])


    # return [Player1, Player2]
    async def activate_cupidon(self):
        # cupidon
        couple=[]
        for player in self.players:
            if player.character.name == "Cupidon": 
                await self.message.reply("Cupidon tire ses flèches...")

                await player.user.send("Choisissez le premier amoureux :\n" + lt.get_player_list(self.players))

                couple1 = None
                attempts = 0

                while attempts < 3:
                    couple1 = await lt.get_player_named_by_player(player, self.players, self.client)
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
                        couple2 = await lt.get_player_named_by_player(player, self.players, self.client)
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

        self.couple = couple
                
    # handle voyante turn
    async def activate_vovo(self):
        for player in self.players:
            # found a vovo
            if player.character.name == "La Voyante" and player.alive == True:
                self.currentMessage = await self.currentMessage.reply("La voyante espionne quelqu'un...")

                # MP
                await player.user.send("Vous pouvez espionner quelqu'un ! :\n" + lt.get_player_list(lt.get_all_alive(self.players)))
                attempts = 0
                # Get target by asking
                while attempts < 3:
                    target = await lt.get_player_named_by_player(player, self.players, self.client)
                    if target is not None:
                        # get the player, send the message and end the activation, by returning current main channel message
                        await player.user.send(target.user.name + " est : " + target.character.name )
                        return self.currentMessage
                    else:
                        await player.user.send("Joueur non reconnue, réessayez.")
                    attempts += 1
                    if attempts == 3:
                        await player.user.send("Trop d'erreur, tampis !")

    # handle wolves turn
    async def activate_wolves(self):
        self.wovlves_target = None
        self.currentMessage = await self.currentMessage.reply("Les loups vont décider qui éliminer...")
        wolves = []
        # get all alive wolves
        for player in self.players:
            if player.character.wolf == True and player.alive == True:
                await player.user.send("Vous avez 30s pour discuter avec les autres loups et dévorer quelqu'un !\n(tapez 'manger [pseudo]' pour manger !)\n" + lt.get_player_list(lt.get_all_alive(self.players)))
                wolves.append(player)

        # we get all wolves chat 
        def check(m):
                return any(m.author == wolf.user for wolf in wolves)
        try:
            start_time = asyncio.get_event_loop().time()
            # wolf voting phase
            while asyncio.get_event_loop().time() - start_time < 30:
                msg = await self.client.wait_for('message', timeout=30, check=check)
                is_vote = False
                # check if it is a vote
                if msg.content.startswith("manger "):
                    is_vote = True
                    targetString = msg.content[len("manger "):].strip()
                    targetPlayer = lt.get_player_by_name(targetString, self.players)
                    # stop here if we didn't recognize the player, not sending the message to others
                    if targetPlayer == None:
                        await msg.author.send("Pseudo non reconnu, réessayez")
                        continue
                    # find the player who send the vote to add it
                    for player in self.players:
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
        self.currentMessage = await self.currentMessage.reply("Les loups ont fait leur choix.")
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
                self.wolves_target = winners[0]
        # no winner, rip wolves
        self.wovlves_target = None

    # handle soso turn
    async def activate_soso(self):
        self.soso_target = None
        for player in self.players:
            # found a soso
            if player.character.name == "La Sorcière" and player.alive == True:
                # check if all potions used first.
                if (self.SOSO_used_death and self.SOSO_used_life):
                    self.currentMessage = await self.currentMessage.reply("La sorcière a utilisé toutes ses potions.")

                
                self.currentMessage = await self.currentMessage.reply("La sorcière décide si elle veut utilisé ses potions...")
                # check target of wolves
                gonna_die_msg = "Les loups ne tuent personne ce soir."
                if self.wolves_target != None:
                    gonna_die_msg = self.wolves_target.user.name + " va se faire dévorer ce soir !"

                # MP
                mp = await player.user.send("Vous pouvez utiliser vos potions ! :\n*Cliquez sur une des réactions*" + lt.get_player_list(lt.get_all_alive(players))
                                            + "\n" + gonna_die_msg)
                await mp.add_reaction('❌')
                if not (self.SOSO_used_life) and self.wolves_target != None:
                    await mp.add_reaction('🩹')
                if not (self.SOSO_used_death):
                    await mp.add_reaction('🔪')
                if not (self.SOSO_used_death or self.SOSO_used_life):
                    await mp.add_reaction('2️⃣')

                def check(reaction, user):
                    emoji_list = ['🩹', '🔪', '❌', '2️⃣']
                    return player.user == user and str(reaction.emoji) in emoji_list
                
                try:
                    reaction, _ = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                    match reaction.emoji:
                        case '❌':
                            await player.user.send("Vous n'utilisez aucune potion cette nuit.")
                            return
                        case '🩹':
                            if self.SOSO_used_life or self.wolves_target == None:
                                await player.user.send('*Nice try, cheater :p*')

                            await player.user.send("Vous sauvez " + self.wolves_target.user.name)
                            self.wolves_target = None
                            self.SOSO_used_life = True
                        case '🔪':
                            if self.SOSO_used_death:
                                await player.user.send('*Nice try, cheater :p*')

                            await player.user.send("Qui souhaitez vous tuer ?\n" + lt.get_player_list(lt.get_all_alive(self.players)))
                            attempts = 0
                            # Get target by asking soso
                            while attempts < 3:
                                target = await lt.get_player_named_by_player(player, self.players, self.client)
                                if target is not None:
                                    # get the player, send the message and end the activation, by returning current main channel message
                                    await player.user.send("Vous tuez froidement " + target.user.name + " cette nuit.")
                                    self.soso_target = target
                                else:
                                    await player.user.send("Joueur non reconnue, réessayez.")
                                attempts += 1
                                if attempts == 3:
                                    await player.user.send("Trop d'erreur, tampis !")
                            
                        case '2️⃣':
                            if not (self.SOSO_used_death or self.SOSO_used_life):
                                await player.user.send('*Nice try, cheater :p*')
                            # do both, so no break
                            await player.user.send("Vous sauvez " + self.wolves_target.user.name)
                            self.SOSO_used_life = True
                            self.wolves_target = None
                            await player.user.send("Qui souhaitez vous tuer ?\n" + lt.get_player_list(lt.get_all_alive(self.players)))
                            attempts = 0
                            # Get target by asking soso
                            while attempts < 3:
                                target = await lt.get_player_named_by_player(player, self.players, self.client)
                                if target is not None:
                                    # get the player, send the message and end the activation, by returning current main channel message
                                    await player.user.send("Vous tuez froidement " + target.user.name + " cette nuit.")
                                    self.SOSO_used_death = True
                                    self.soso_target = target
                                else:
                                    await player.user.send("Joueur non reconnue, réessayez.")
                                attempts += 1
                                if attempts == 3:
                                    await player.user.send("Trop d'erreur, tampis !")
                    
                except asyncio.TimeoutError:
                    await player.user.send("Aucune réponse ; pas de potion cette nuit !")

    # handle the kill of a player
    async def kill_player(self, player_to_kill):
        self.currentMessage = await self.currentMessage.reply(player_to_kill.user.name + " est mort !")
        player_to_kill.alive = False

        # check if couple
        if player_to_kill.isCouple:
            other_couple = self.couple[0]
            if self.couple[0] == player_to_kill:
                other_couple = self.couple[1]
            if other_couple.alive:
                self.currentMessage.reply(player_to_kill.user.name + " était en couple avec " + other_couple.user.name + ", qui le/la suis dans la tombe !")
                await self.kill_player(other_couple)

        # check if it is chassou
        if player_to_kill.character.name == "Le Chasseur":
            self.currentMessage = await self.currentMessage.reply("C'était le chasseur ! Avant de faire son dernier souffle, il peut décider de tirer sur quelqu'un...")
            await player_to_kill.user.send("Vous êtes mort ! Mais pas tout seul, décidez qui tuer :\n" + lt.get_player_list(lt.get_all_alive(self.players)))
            attempts = 0
            # Get target by asking chassou
            while attempts < 3:
                target = await lt.get_player_named_by_player(player_to_kill, self.players, self.client)
                if target is not None:
                    # BAM, he ded
                    await self.currentMessage.reply(player_to_kill.user.name + " abat " + target.user.name + " dans un dernier souffle.")
                    await self.kill_player(target)
                    # stop here the attempts
                    attempts = 4
                else:
                    await player_to_kill.user.send("Joueur non reconnu, réessayez.")
                attempts += 1
                if attempts == 3:
                    await player_to_kill.user.send("Trop d'erreur, tampis !")

        else:
            self.currentMessage = await self.currentMessage.reply(player_to_kill.user.name + " était en faite " + player_to_kill.character.name)
        await self.check_victory()

    # check if end game is now
    async def check_victory(self):
        alive_players = lt.get_all_alive(self.players)
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
            await self.end_game("couple")
            self.gameOn = False
        # then, check the villagers ; if there is no wolves left, and there is at least one villager still alive, they win
        if len(alive_wolves) == 0 and len(alive_villagers) > 0:
            await self.end_game("villagers")
            self.gameOn = False
        # finally, check wolves. If they are more numerous than villagers, they win
        if len(alive_wolves) > len(alive_villagers):
            await self.end_game("wolves")
            self.gameOn = False
        # if everyone is dead, it is a draw
        if len(alive_players) == 0:
            await self.end_game("draw")
            self.gameOn = False
        # else, not the end

    # end the game, depending how in condition
    async def end_game(self, condition):
        
        winners = []
        losers = []
        if condition == "villagers":
            await self.currentMessage.reply("Tous les loups sont morts, les villageois ont gagné !")
            winners = [player for player in self.players if not player.isWolf]
            losers = [player for player in self.players if player.isWolf]
        
        elif condition == "wolves":
            await self.currentMessage.reply("Tous les villageois sont morts, les loups ont gagné !")
            winners = [player for player in self.players if player.isWolf]
            losers = [player for player in self.players if not player.isWolf]
        
        elif condition == "couple":
            await self.currentMessage.reply("Le couple a gagné seul !")
            winners = [player for player in self.players if player.isCouple]
            losers = [player for player in self.players if not player.isCouple]
        
        elif condition == "draw":
            await self.currentMessage.reply("Tout le monde est mort, pas de gagnant !")
            losers = self.players
        
        end_msg = "GAGNANTS\n"
        for winner in winners:
            end_msg += winner.user.mention + " qui était " + winner.character.name + "\n"
        end_msg += "PERDANTS\n"
        for loser in losers:
            end_msg += loser.user.mention + " qui était " + loser.character.name + "\n"
        self.currentMessage = await self.currentMessage.reply(end_msg)

