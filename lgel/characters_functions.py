from lgel.characters_list import characters

def get_all_characters():
    return characters

def get_all_wolf_characters(characters = characters):
    result = []
    for character in characters:
        if character.wolf:
            result.append(character)
    return result

def get_all_villagers_characters(characters = characters):
    result = []
    for character in characters:
        if (character.wolf == False):
            result.append(character)
    return result


def get_all_priority_characters(priority, characters = characters):
    result = []
    for character in characters:
        if (character.priority == priority):
            result.append(character)
    return result
