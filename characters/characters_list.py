from characters.character import Character

characters = []

george = Character("George", "Hunter", 14, "./static/images/characters/George.webp", "Tuez tous les shadows", "(Une fois dans la partie) \nChoisissez un joueur et lancer un dé à 4 faces. Faîtes-lui autant de dégâts que le résultat de ce dé.")
characters.append(george)


franklin = Character("Franklin", "Hunter", 12, "./static/images/characters/Franklin.webp", "Tuez tous les shadows", "(Une fois dans la partie) \nChoisissez un joueur et lancer un dé à 6 faces. Faîtes-lui autant de dégâts que le résultat de ce dé.")
characters.append(franklin)

vampire = Character("Vampire", "Shadow", 13, "./static/images/characters/Vampire.webp", "Tuez tous les hunters ou trois neutres", "Si vous attaquez un joueur et infligez des dégâts, soignez vous de deux blessures.")
characters.append(vampire)

loup_garou = Character("Loup Garou", "Shadow", 14, "./static/images/characters/Loup_Garou.webp", "Tuez tous les hunters ou trois neutres", "Après que vous soyez attaqué, vous pouvez contre-attaqué ce joueur immédiatement.")
characters.append(loup_garou)
