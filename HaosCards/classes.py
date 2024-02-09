import random
import string
import json

def generate_gamecode(length=6):
    characters = string.digits
    
    random_string = ''.join(random.choice(characters) for _ in range(length))
    
    return random_string

class Player:
    def __init__(self, name, status, unique_room):
        self.name = name  
        self.score = 0
        self.cards = {}
        self.status = status
        self.unique_room = unique_room
        self.acknowledgement = False
        self.lobby_score = 0
        self.game_score = 0

    def __str__(self):
        return f"Name: {self.name}, Score: {self.score}, Status: {self.status}, Unique Room: {self.unique_room}, Acknowledgement: {self.acknowledgement}, Lobby Score: {self.lobby_score}, Game Score: {self.game_score}"
class Game:
    def __init__(self, gamecode, point2win, round_time, cards_per_player, players, white_cards, black_cards, player_cards): 
        self.white_cards = white_cards
        self.black_cards = black_cards
        self.player_cards = player_cards
        self.used_white_cards = []
        self.used_black_cards = []
        self.gamecode = gamecode
        self.point2win = point2win
        self.round_time = round_time
        self.cards_per_player = cards_per_player
        self.players = players
        self.current_black_card = None
        self.current_white_cards = {}
        
    def __str__(self):
        return f'Game(gamecode={self.gamecode}, point2win={self.point2win}, round_time={self.round_time}, cards_per_player={self.cards_per_player}, players={self.players}, player_cards={self.player_cards}, white_cards={self.white_cards}, black_cards={self.black_cards})'
class Lobby:
    def __init__(self, gamecode):
        self.gamecode = gamecode
        self.settings = {'p2w': 10, "rt":30, "cpp": 8}
        self.players = []
        self.player_data = []
        self.owner = None
    def __str__(self):
        return f'Lobby(gamecode={self.gamecode}, players={self.players}, owner={self.owner}, settings={self.settings})'

if __name__ =="__main__":
    print(generate_gamecode())
