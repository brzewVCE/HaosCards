import random
import string

def generate_gamecode(length=6):
    # Define the characters to choose from (letters and digits)
    characters = string.digits
    
    # Generate the random string
    random_string = ''.join(random.choice(characters) for _ in range(length))
    
    return random_string

class Player:
    def __init__(self, name, cards={}, score=0, status="player"):
        self.name = name  # Player's name
        self.score = score  # Player's score (default to 0)
        self.cards = cards 
        self.status = status  # Player's status 
    pass

class Game:
    def __init__(self, point2win, gamecode, cards, players, usedCards={}): 

        pass

class Lobby:
    def __init__(self, gamecode, settings={'p2w': 10, "rt":30, "cpp": 8}, players=[], owner=None):
        self.gamecode = gamecode
        self.settings = {'p2w': 10, "rt":30, "cpp": 8}
        self.players = []
        self.owner = None
    def __str__(self):
        return f'Lobby(gamecode={self.gamecode}, players={self.players}, owner={self.owner}, settings={self.settings})'

if __name__ =="__main__":
    print(generate_gamecode())