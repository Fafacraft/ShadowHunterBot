from characters.character import Character

characters = []

george = Character("George", "Hunter", 14, "./static/images/characters/George.webp", "Tous les shadows sont morts", "(Une fois dans la partie) \nChoisissez un joueur et lancer un dé à 4 faces. Faîtes-lui autant de dégâts que le résultat de ce dé.")
characters.append(george)

franklin = Character("Franklin", "Hunter", 12, "./static/images/characters/Franklin.webp", "Tous les shadows sont morts", "(Une fois dans la partie) \nChoisissez un joueur et lancer un dé à 6 faces. Faîtes-lui autant de dégâts que le résultat de ce dé.")
characters.append(franklin)

emi = Character("Emi", "Hunter", 10, "./static/images/characters/Emi.webp", "Tous les shadows sont morts", "Quand vous vous déplacez, vous pouvez utilisé le dé normalement ou bouger dans le lieu adjacent de votre zone.")
characters.append(emi)

vampire = Character("Vampire", "Shadow", 13, "./static/images/characters/Vampire.webp", "Tous les hunters sont morts", "Si vous attaquez un joueur et infligez des dégâts, soignez vous de deux blessures.")
characters.append(vampire)

loup_garou = Character("Loup Garou", "Shadow", 14, "./static/images/characters/Loup_Garou.webp", "Tous les hunters sont morts", "Après que vous soyez attaqué, vous pouvez contre-attaqué ce joueur immédiatement.")
characters.append(loup_garou)

metamorphe = Character("Métamorphe", "Shadow", 11, "./static/images/characters/Metamorphe.webp", "Tous les hunters sont morts", "Vous pouvez mentir aux cartes visions. Vous n'avez PAS besoin de vous révéler pour cela.")
characters.append(metamorphe)

allie = Character("Allie", "Neutre", 8, "./static/images/characters/Allie.webp", "Soyez en vie à la fin de la partie", "(Une fois dans la partie) \n Soignez toutes vos blessures.")
characters.append(allie)

bob = Character("Bob", "Neutre", 10, "./static/images/characters/Bob.webp", "Vous avez 5 cartes équipements ou plus.", "4-6 joueurs : Si vous infligez deux dégats ou plus, vous pouvez voler une carte équipements à la place.\n7-8 joueurs : Si votre attaque tue un joueur, vous récupérer toutes ses cartes équipements.")
characters.append(bob)

charles = Character("Charles", "Neutre", 11, "./static/images/characters/Charles.webp", "Tuez un joueur alors qu'il y a déjà deux morts ou plus.", "Après votre attaque, vous pouvez vous infliger 2 dégâts pour attaquer à nouveau le même personnage.")
characters.append(charles)

daniel = Character("Daniel", "Neutre", 13, "./static/images/characters/Daniel.webp", "Soyez le premier à mourir OU soyez en vie lorsque tout les shadows sont morts.", "Si quelqu'un meurt, vous DEVEZ vous révéler.")
characters.append(daniel)
