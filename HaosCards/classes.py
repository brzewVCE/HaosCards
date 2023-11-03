import random
import string

def generate_gamecode(length=6):
    characters = string.digits
    
    random_string = ''.join(random.choice(characters) for _ in range(length))
    
    return random_string

class Player:
    def __init__(self, name, status):
        self.name = name  
        self.score = 0
        self.cards = {}
        self.status = status
    pass

class Game:
    def __init__(self, point2win, gamecode, cards, players): 
        self.usedCards = {}

class Lobby:
    def __init__(self, gamecode):
        self.gamecode = gamecode
        self.settings = {'p2w': 10, "rt":30, "cpp": 8}
        self.players = []
        self.owner = None
    def __str__(self):
        return f'Lobby(gamecode={self.gamecode}, players={self.players}, owner={self.owner}, settings={self.settings})'

if __name__ =="__main__":
    print(generate_gamecode())
