from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from flask_socketio import SocketIO
from flask_session import Session
from sckt import register_events, lobbies, games

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'your_session_cookie_name'

Session(app)

socketio = SocketIO(app, manage_session=False, async_mode = 'eventlet')

register_events(socketio) # Add this line after initializing socketio
                            
                            #STRONY
@app.route('/', methods=['GET','POST'])
def home():
    if session.get('room') in lobbies and session.get('nickname') is not None:
        print(f"Returned player to {session.get('room')}")
        return redirect(url_for('lobby'))
    
    return render_template('index.html', session=session)


@app.route('/play', methods=['GET','POST'])
def play():
     
    return render_template('play.html')

@app.route('/lobby', methods=['GET','POST'])
def lobby():
    if session.get('room') in lobbies:
        return render_template('lobby.html', session=session)

    return redirect(url_for('home'))


@app.route('/static/<path:filename>')
def get_static_file(filename):
    return send_from_directory('static', filename)


if __name__ == "__main__":
    socketio.run(app, port=5000)
