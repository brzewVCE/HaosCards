from flask import Flask, render_template, request, jsonify, Response, send_from_directory, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit, close_room, rooms
from flask_session import Session
import json
import random
from classes import Game, Player, Lobby, generate_gamecode
from color_print import print_info, print_error, print_warning
import eventlet
import random
import uuid
import os

lobbies={}
games={}
acknowledgements = {}
nickname_max_len = 12
min_players = 2

def register_events(socketio):

    @socketio.on('validate_game_code')
    def validate_game_code(gamecode, nickname):
        print(f"Received game code: {gamecode}")
        if gamecode in lobbies:
            if nickname in lobbies[gamecode].players:
                return emit('game_code_valid', {'valid': 'Name'})
            return emit('game_code_valid', {'valid': 'True'})
        else:
            emit('game_code_valid', {'valid': 'False'})


    @socketio.on('create_lobby')
    def create_lobby(nickname, gamecode):
        if len(nickname) > nickname_max_len:
            return print_error(f"Nickname {nickname} too long")
        session['nickname'] = nickname
        session['room'] = gamecode
        new_lobby = Lobby(gamecode=gamecode)
        lobbies[gamecode] = new_lobby
        print(new_lobby)
        print(f'{nickname} generated lobby {gamecode}')
        lobbies_as_strings = [str(lobby) for lobby in lobbies]
        print(f'All lobbies: {lobbies_as_strings}')
        join(nickname, gamecode)


    @socketio.on('join')
    def join(nickname, gamecode):
        if gamecode not in lobbies:
            return print_error(f"Gamecode {gamecode} not found")
        if len(nickname) > nickname_max_len:
            return print_error(f"Nickname {nickname} too long")
        session['nickname'] = nickname
        session['room'] = gamecode
        player_room = str(uuid.uuid4())
        session['player_room'] = player_room
        new_player = Player(name=nickname, 
                            status = 'player',
                            unique_room = player_room)
        lobbies[gamecode].player_data.append(new_player)
        print_info(f"{str(lobbies[gamecode].player_data)}")
        join_room(gamecode)
        join_room(player_room)
        print_info(f'{nickname} joined {player_room} and {gamecode}')
        print_error(f"{nickname}'s rooms: {rooms()}")
        print_info(f'{str(new_player)}')

    @socketio.on('player_update')
    def player_update(action):
        nickname = session['nickname']
        gamecode = session['room']
        if gamecode not in lobbies:
            return print_error(f"Gamecode {gamecode} not found")
        if len(nickname) > nickname_max_len:
            return print_error(f"Nickname {nickname} too long")
        if action == 'join':
            join_room(gamecode)
            join_room(session['player_room'])
            if lobbies[gamecode].owner == None:
                lobbies[gamecode].owner = nickname
            
            if nickname not in lobbies[gamecode].players:
                lobbies[gamecode].players.append(nickname)
            print(f'{nickname} joined {gamecode}')
        
        if action == 'leave':
            lobbies[gamecode].players.remove(nickname)
            player = [player for player in lobbies[gamecode].player_data if player.name == nickname][0]
            lobbies[gamecode].player_data.remove(player)
            if lobbies[gamecode].owner == nickname:
                if len(lobbies[gamecode].players) != 0:
                    lobbies[gamecode].owner = random.choice(lobbies[gamecode].players)
                else:
                    lobbies.pop(gamecode)
                    close_room(gamecode)
                    print(f'{nickname} left {gamecode}, deleting it')
                    return leave_lobby(gamecode, nickname)
            leave_lobby(gamecode, nickname)

        print(f'All lobbies: {str(lobbies)}')
        data_update(gamecode)

    
    def leave_lobby(gamecode, nickname):
        unique_room = session['player_room']
        leave_room(unique_room)
        leave_room(gamecode)
        session.clear()
        print(f'{nickname} left {gamecode}')

    @socketio.on('kick_player')
    def kick_player(nickname):
        gamecode = session['room']
        if gamecode not in lobbies:
            return print_error(f"Gamecode {gamecode} not found")
        if session['nickname'] != lobbies[gamecode].owner:
            return print_error(f"{session['nickname']} is not the owner of {gamecode}")
        if nickname in lobbies[gamecode].players:
            data = {'nickname': nickname}
            send_data('kicked', data, gamecode)
            print_warning(f'{nickname} was kicked from {gamecode}')
            return data_update(gamecode)
        else:
            print_error(f'{nickname} not found in {gamecode}')

    @socketio.on('start_game')
    def start_game(data):
        gamecode = session['room']
        if gamecode not in lobbies:
            return print_error(f"Gamecode {gamecode} not found")
        if session['nickname'] != lobbies[gamecode].owner:
            return print_error(f"{session['nickname']} is not the owner of {gamecode}")
        if len(lobbies[gamecode].players) < min_players:
            return print_error(f"Not enough players in {gamecode}")
        settings = lobbies[gamecode].settings
        # Open the file
        print(os.listdir())
        with open('./HaosCards/cards/white_cards.json', 'r') as file:
            # Load the JSON data from the file
            white_cards_data = json.load(file)
        with open('./HaosCards/cards/black_cards.json', 'r') as file:
            # Load the JSON data from the file
            black_cards_data = json.load(file)
        white_cards = white_cards_data['white_cards']
        black_cards = black_cards_data['black_cards']
        print_error(f"White cards: {white_cards}")
        print_error(f"Black cards: {black_cards}")
        black_cards_dict = {i: card for i, card in enumerate(black_cards)}
        white_cards_dict = {i: card for i, card in enumerate(white_cards)}
        print_error(f"White cards: {white_cards_dict}")
        print_error(f"Black cards: {black_cards_dict}")
        new_game = Game(gamecode, settings['p2w'], settings['rt'], settings['cpp'], lobbies[gamecode].players, white_cards_dict, black_cards_dict)
        games[gamecode] = new_game
        print_error(f"{str(new_game)}")       
        send_data('game_started', {}, gamecode)
        print(f'All lobbies: {str(lobbies)}')

    @socketio.on('get_data')
    def get_data(gamecode):
        data_update(gamecode)

    def data_update(gamecode):
        players = lobbies[gamecode].players
        owner = lobbies[gamecode].owner
        data = {'players': players, 'owner':owner}
        send_data('data_update', data, gamecode)
        print(f'Updated with data {players} {owner}')

    @socketio.on('request_settings')
    def request_settings(gamecode):
        settings = lobbies[gamecode].settings
        send_data("settings_data", settings, gamecode)
       
    @socketio.on('change_settings')
    def change_settings(data):
        value = data['value']
        target = data['target']
        gamecode = session['room']
        if gamecode not in lobbies:
            return print_error(f"Gamecode {gamecode} not found")
        settings = lobbies[gamecode].settings
        settings[target] = value
        send_data('settings_data', settings, gamecode)
        server_response(data)

    def send_data(function_name, data, gamecode):
        attempts = 0
        attempts_limit = 50
        if gamecode not in lobbies:
            return print_error(f"Gamecode {gamecode} not found")
        players = lobbies[gamecode].player_data
        for player in players:
            player_room = player.unique_room
            print_info(str(rooms()))
            acknowledgement_id = str(uuid.uuid4())
            acknowledgements[acknowledgement_id] = False
            data['acknowledgement_id'] = acknowledgement_id
            print_warning(f"data: {data}")
            while acknowledgements[acknowledgement_id] != True and attempts < attempts_limit:
                emit(function_name, data, to=player_room)
                print_info(f"Sent {function_name} to {player_room}")
                eventlet.sleep(0.12)
                attempts += 1
            if attempts == attempts_limit:
                print_error(f"Failed to receive acknowledgement for {acknowledgement_id}")
                leave_lobby(gamecode, session['nickname'])

    @socketio.on('client_response')
    def client_response(id):
        acknowledgements[id] = True
        nickname = session['nickname']
        room = session['player_room']
        print_info(f"{nickname} acknowledged newest data {id} ")
    
    def server_response(data):
        acknowledgement_id = data['acknowledgement_id']
        emit('server_response', {'acknowledgement_id' : acknowledgement_id}, to=session['player_room'])
        print_info(f'server response {acknowledgement_id} sent to {session["nickname"]} in {session["player_room"]}')
