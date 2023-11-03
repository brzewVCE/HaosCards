from flask import Flask, render_template, request, jsonify, Response, send_from_directory, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit, close_room, rooms
from flask_session import Session
import json
import flask
import random
from classes import Game, Player, Lobby, generate_gamecode

lobbies={}
games={}

def register_events(socketio):

    @socketio.on('validate_game_code')
    def validate_game_code(gamecode, nickname):
        #niech sprawdza czy jest tez gracz o takiej nazwie
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
        join(nickname=nickname,gamecode=gamecode)


    @socketio.on('join')
    def join(nickname, gamecode):
        session['nickname'] = nickname
        session['room'] = gamecode
        room = request.sid
        new_player = Player(name=nickname, 
                            status = 'player',
                            unique_room = room)
        if gamecode in lobbies:
            lobbies[gamecode].player_data.append(new_player)
            print(f"{lobbies[gamecode].player_data}")
        join_room(gamecode)
        print(f'{nickname} joined {room}')
        print(f"{nickname}'s rooms: {rooms()}")
        print(f'{str(new_player)}')

    @socketio.on('player_update')
    def player_update(nickname, gamecode, action):
        if action == 'join':
            if gamecode in lobbies:
                join_room(gamecode)
                if lobbies[gamecode].owner == None:
                    lobbies[gamecode].owner = nickname
                
                if nickname not in lobbies[gamecode].players:
                    lobbies[gamecode].players.append(nickname)
                    
                print(str(lobbies[gamecode]))
                data_update(gamecode)
        if action == 'leave':
            if gamecode in lobbies:
                leave_room(gamecode)
                lobbies[gamecode].players.remove(nickname)
                if lobbies[gamecode].owner == nickname:
                    if len(lobbies[gamecode].players) != 0:
                        lobbies[gamecode].owner = random.choice(lobbies[gamecode].players)
                    else:
                        lobbies.pop(gamecode)
                        leave_room(gamecode)
                        session.clear()
                        print(f'{nickname} left {gamecode}, deleting it')
                        return print(f'All lobbies: {str(lobbies)}')
                leave_room(gamecode)
                session.clear()
                print(f'{nickname} left {gamecode}')
                print(f'All lobbies: {str(lobbies)}')
                data_update(gamecode)


    @socketio.on('left_lobby')
    def left(message):
        gamecode = session.get('room')
        nickname = session.get('nickname')
        leave_room(gamecode)
        session.clear()
        print(f'{nickname} left {gamecode}')

    @socketio.on('pr')
    def pr(message):
        return print(f'{message}')

    @socketio.on('get_data')
    def get_data(gamecode):
        data_update(gamecode)

    def data_update(gamecode):
        players = lobbies[gamecode].players
        owner = lobbies[gamecode].owner
        emit('data_update', {'players': players, 'owner':owner}, to=gamecode)
        print(f'Updated with data {players} {owner}')

    @socketio.on('request_settings')
    def request_settings(gamecode):
        settings = lobbies[gamecode].settings
        send_settings(gamecode,settings)
       
    @socketio.on('change_settings')
    def change_settings(gamecode, action, target):
        #//funkcja
        settings = lobbies[gamecode].settings
        if target != 'rt':
            x=1
        else:
            x=5
        if action == '+':
            settings[target] += x
        else:
            settings[target] -= x
        send_settings(gamecode, settings)


    def send_settings(gamecode,settings):
        emit('settings_data', settings, to=gamecode)