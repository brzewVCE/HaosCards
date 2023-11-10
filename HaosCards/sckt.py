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
        session['nickname'] = nickname
        session['room'] = gamecode
        player_room = str(uuid.uuid4())
        session['player_room'] = player_room
        join_room(player_room)
        new_player = Player(name=nickname, 
                            status = 'player',
                            unique_room = player_room)
        if gamecode in lobbies:
            lobbies[gamecode].player_data.append(new_player)
            print_warning(f"{lobbies[gamecode].player_data}")
        join_room(gamecode)
        print(f'{nickname} joined {player_room}')
        print_error(f"{nickname}'s rooms: {rooms()}")
        print(f'{str(new_player)}')

    @socketio.on('player_update')
    def player_update(nickname, gamecode, action):
        if gamecode in lobbies:
            if action == 'join':
                join_room(gamecode)
                if lobbies[gamecode].owner == None:
                    lobbies[gamecode].owner = nickname
                
                if nickname not in lobbies[gamecode].players:
                    lobbies[gamecode].players.append(nickname)
                print(f'{nickname} joined {gamecode}')
            
            if action == 'leave':
                if gamecode in lobbies:
                    lobbies[gamecode].players.remove(nickname)
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
        emit('data_update', data, to=gamecode)
        print(f'Updated with data {players} {owner}')

    @socketio.on('request_settings')
    def request_settings(gamecode):
        settings = lobbies[gamecode].settings
        send_data("settings_data", settings, gamecode)
        # send_settings(gamecode,settings)
       
    @socketio.on('change_settings')
    def change_settings(gamecode, action, target):
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
        players = lobbies[gamecode].player_data
        for player in players:
            player_room = player.unique_room
            session_id = request.sid
            print_error(f"session_id: {session_id}")
            acknowledgement_id = str(uuid.uuid4())
            acknowledgements[acknowledgement_id] = False
            data['acknowledgement_id'] = acknowledgement_id
            print_warning(f"data: {data}")
            while acknowledgements[acknowledgement_id] != True:
                emit(function_name, data, to=player_room)
                print_info(f"Sent {function_name} to {player_room}")
                print_info(f"{acknowledgement_id} {acknowledgements[acknowledgement_id]}")
                eventlet.sleep(0.1)
            

    @socketio.on('acknowledge')
    def acknowledge(id):
        acknowledgements[id] = True
        print_info(f"ACKNOWLEDGED {id}")

