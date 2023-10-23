from flask import Flask, render_template, request, jsonify, Response, send_from_directory, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit, close_room, rooms
from flask_session import Session
import json
import flask
import random
from classes import Game, Player, Lobby, generate_gamecode

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'your_session_cookie_name'


Session(app)

socketio = SocketIO(app, manage_session=False, async_mode = 'eventlet')

lobbies={}
games={}
                            #STRONY
@app.route('/', methods=['GET','POST'])
def home():
    if session.get('room') in lobbies and session.get('nickname') is not None:
        print(f"Returned player to {session.get('room')}")
        return redirect(url_for('lobby'))
    
    return render_template('index.html', session=session)


@app.route('/play', methods=['GET','POST'])
def play():
    if session.get('room') not in games:
        return redirect(url_for('home'))
    return render_template('play.html')

@app.route('/lobby', methods=['GET','POST'])
def lobby():
    if session.get('room') in lobbies:
        return render_template('lobby.html', session=session)

    return redirect(url_for('home'))

@socketio.on('validate_game_code')
def validate_game_code(gamecode):
    #niech sprawdza czy jest tez gracz o takiej nazwie
    print(f"Received game code: {gamecode}")
    if gamecode in lobbies:
        return emit('game_code_valid', {'valid': True})
    else:
        emit('game_code_valid', {'valid': False})


@socketio.on('create_lobby')
def create_lobby(nickname):
    gamecode = generate_gamecode()
    session['nickname'] = nickname
    session['room'] = gamecode
    new_lobby = Lobby(gamecode=gamecode)
    lobbies[gamecode] = new_lobby
    print(new_lobby)
    print(f'{nickname} generated lobby {gamecode}')
    lobbies_as_strings = [str(lobby) for lobby in lobbies]
    print(f'All lobbies: {lobbies_as_strings}')
    join(gamecode, nickname)

    

@socketio.on('join_lobby')
def join_lobby(nickname, gamecode):
    session['nickname'] = nickname
    session['room'] = gamecode
    join(gamecode,nickname)

def join(gamecode, nickname):
    #TO DO
    join_room(gamecode)
    print(f'{nickname} joined {gamecode}')

@socketio.on('player_update')
def player_update(nickname, gamecode, action):
    #usuwanie przy leave
    if action == 'join':
        if gamecode in lobbies:
            if lobbies[gamecode].owner == None:
                lobbies[gamecode].owner = nickname
            
            if nickname not in lobbies[gamecode].players:
                lobbies[gamecode].players.append(nickname)
                
            print(str(lobbies[gamecode]))
            data_update(gamecode)
    if action == 'leave':
        if gamecode in lobbies:
            lobbies[gamecode].players.remove(nickname)
            if lobbies[gamecode].owner == nickname:
                if len(lobbies[gamecode].players) != 0:
                    lobbies[gamecode].owner = random.choice(lobbies[gamecode].players)
                else:
                    lobbies.pop(gamecode)
            leave_room(gamecode)
            session.clear()
            print(f'{nickname} left {gamecode}')
            print(str(lobbies))
            data_update(gamecode)
            #zmniejsza liczbe graczy i zmienia wlasciciela na ekranie


@socketio.on('left_lobby')
def left(message):
    gamecode = session.get('room')
    nickname = session.get('nickname')
    leave_room(gamecode)
    session.clear()
    print(f'{nickname} left {gamecode}')
    #emit('status', {'msg': username + ' has left the room.'}, room=room)

@socketio.on('pr')
def pr(message):
    return print(f'{message}')

def data_update(gamecode):
    players = lobbies[gamecode].players
    owner = lobbies[gamecode].owner
    emit('data_update', {'players': players, 'owner':owner},to=gamecode, broadcast=True)
    print(f'Updated with data {players} {owner}')




@app.route('/static/<filename>')
def get_static_file(filename):
    return send_from_directory('static', filename)

    


if __name__ == "__main__":
    socketio.run(app, port=5000)