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

lobbies={}
games={}
acknowledgements = {}

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
    def player_update(nickname, gamecode, action):
        if gamecode not in lobbies:
            return print_error(f"Gamecode {gamecode} not found")
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
    def change_settings(gamecode, action, target):
        if gamecode not in lobbies:
            return print_error(f"Gamecode {gamecode} not found")
        settings = lobbies[gamecode].settings
        if target != 'rt':
            x=1
        else:
            x=5
        if action == '+':
            settings[target] += x
        else:
            settings[target] -= x
        send_data('settings_data', settings, gamecode)
        #tu zmiana

    def send_settings(gamecode,settings):
        emit('settings_data', settings, to=gamecode)


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
                eventlet.sleep(0.1)
                attempts += 1
            if attempts == attempts_limit:
                print_error(f"Failed to receive acknowledgement for {acknowledgement_id}")
                leave_lobby(gamecode, session['nickname'])

    @socketio.on('acknowledge')
    def acknowledge(id):
        acknowledgements[id] = True
        print_info(f"ACKNOWLEDGED {id}")

