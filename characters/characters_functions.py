from characters.characters_list import characters

def get_all_characters():
    return characters

def get_characters_by_allegiance(allegiance):
    result = []
    for character in characters:
        if character.allegiance == allegiance:
            result.append(character)
    return result

