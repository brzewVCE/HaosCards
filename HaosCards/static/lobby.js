var socket;
    $(document).ready(function() {
        socket = io.connect('http://' + document.domain + ':' + location.port+'/');
        
        console.log('Connection established');
        
        socket.emit('player_update','{{session["nickname"]}}', "{{ session['room'] }}", 'join');
        
        socket.on('data_update', function(data) {
            console.log(data)
            var players = data.players;
            var owner = data.owner;
            generate_players_counter(players);
            generate_players(players, owner);
            toggleStyle(players,owner);
            //tutaj patrzy czy to owner i daje inne css
        })

        $('#game-code').click(function() {
            var content = $('#game-code').text();
            copyToClipboard(content);
        });
        
        $(window).on('beforeunload', function(){
        //leave_lobby();
        });
    });
    function leave_lobby() {
        nickname = "{{ session['nickname'] }}"
        gamecode = "{{ session['room'] }}"
        console.log(nickname," left the lobby");
        socket.emit('player_update', nickname, gamecode, 'leave', function() {
            socket.disconnect();
            window.location.href = "{{ url_for('home') }}";
    });
    }

    function kickFromLobby(nickname) {
        gamecode = "{{ session['room'] }}"

    }

    function generate_players_counter(players) {
        var playerCount = players.length;
        let counter = document.getElementById("playerCounter");
        counter.textContent = playerCount;
        const container = document.getElementById('player-list-container');
        $('#playerCounter').val(playerCount);
    }

    function generate_players(players, owner) {
        var nickname = '{{ session["nickname"] }}';
        const container = document.getElementById('player-list-container');

        container.innerHTML = '';
        players.forEach(player => {
            const playerInstance = new Player(player);
            const playerElement = document.createElement('div');
            playerElement.classList.add('player');

            const playerNameElement = document.createElement('span');
            playerNameElement.classList.add('player-name');
            playerNameElement.innerHTML = player;
            playerElement.appendChild(playerNameElement);

            const kickButton = document.createElement('button');
            if(player !== owner){

                kickButton.classList.add('kick-button');

                kickButton.innerHTML = 'Kick';

                kickButton.addEventListener('click', () => {

                console.log(`Kicking ${player}`);
            });
                playerElement.appendChild(kickButton);
            } else {
                const ownerButton = document.createElement('button');
                ownerButton.classList.add('owner-button');
                ownerButton.innerHTML = 'Owner';
                playerElement.appendChild(ownerButton);
            }
            
            
            container.appendChild(playerElement);
            });
    }

    function copyToClipboard(text) {
        var input = document.createElement('textarea');
        input.value = text;
        document.body.appendChild(input);
        input.select();
        document.execCommand('copy');
        document.body.removeChild(input);
        alert('Gamecode copied!');
        }

    function toggleStyle(players,owner) {
        nickname = "{{ session['nickname'] }}"
        var kickButtons = document.getElementsByClassName('kick-button');
        var inputs = document.getElementsByClassName('input');
        var startButton = document.getElementById('start-button');

        // Reset styles for all elements
        for (var i = 0; i < kickButtons.length; i++) {
            kickButtons[i].classList.remove('hidden');
        }
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].classList.remove('disabled-input');
        }
        startButton.classList.remove('hidden', 'disabled-button');

        if (owner !== nickname){
            for (var i = 0; i < kickButtons.length; i++) {
                kickButtons[i].classList.add('hidden');
            }
            for (var i = 0; i < inputs.length; i++) {
                inputs[i].classList.add('disabled-input');
            }
            startButton.classList.add('hidden');

        }
        if (players.length < 3){
            startButton.classList.add('disabled-button');
        }
    }


    $( window ).resize(function() {
        $(".content").addClass("mobile")
    });
    
    class Player {
    constructor(name) {
        this.name = name;
    }
}