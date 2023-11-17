var socket;
    $(document).ready(function() {
        socket = io.connect('http://' + document.domain + ':' + location.port+'/');
        var PlayersDatabase = null;
        var selectedButton = null;
        console.log('Connection established');
        
        socket.emit('player_update','{{session["nickname"]}}', "{{ session['room'] }}", 'join');
        
        socket.on('acknowledgement', function(data) {
            console.log(data)
            
        })


        socket.on('data_update', function(data) {
            console.log(data)
            var players = data.players;
            var owner = data.owner;
            generate_players_counter(players);
            generate_players(players, owner);
            toggleStyle(players,owner);

        })

        socket.emit('request_settings', "{{ session['room'] }}")

        socket.on('settings_data', function(data) {
            console.log(data)
            var points2win = data.p2w;
            var roundTime = data.rt;
            var cardsPerP = data.cpp;
            generate_settings(points2win,roundTime,cardsPerP)
        })

        $('#game-code').click(function() {
            var content = $('#game-code').text();
            copyToClipboard(content);
        });
        
        $('.arrow-button').click(function() {
            var action = $(this).data('action'); // Get the action (+ or -)
            var target = $(this).data('target'); // Get the target (e.g., round time)
            var minValue = $(this).data('min');
            var maxValue = $(this).data('max');
            var currentValue = parseFloat($('#'+target).text());
            var gamecode = "{{session['room']}}"

            if (selectedButton) {
                $(selectedButton).removeClass('disabled-button');
                $(selectedButton).removeClass('selected-button');
            }

            if (action === '+' && currentValue < maxValue) {
                socket.emit('change_settings', gamecode, action, target);
            } else if (action === '-' && currentValue > minValue) {
                socket.emit('change_settings', gamecode, action, target);
            } else {
                $(this).addClass('disabled-button');
            }
            selectedButton = this;
            $(selectedButton).addClass('selected-button');
    });

        $(window).on('beforeunload', function(){
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

    function generate_settings(p2w,rt,cpp) {
        $('#p2w').text(p2w);
        $('#rt').text(rt);
        $('#cpp').text(cpp);
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
        var changeArrows = document.getElementsByClassName('arrow-button')
        var startButton = document.getElementById('start-button');

        // Reset styles for all elements
        for (var i = 0; i < kickButtons.length; i++) {
            kickButtons[i].classList.remove('hidden');
        }
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].classList.remove('disabled-input');
        }
        for (var i = 0; i < changeArrows.length; i++) {
            changeArrows[i].classList.remove('hidden');
        }
        startButton.classList.remove('hidden', 'disabled-button');

        if (owner !== nickname){
            for (var i = 0; i < kickButtons.length; i++) {
                kickButtons[i].classList.add('hidden');
            }
            for (var i = 0; i < inputs.length; i++) {
                inputs[i].classList.add('disabled-input');
            }
            for (var i = 0; i < changeArrows.length; i++) {
                changeArrows[i].classList.add('hidden');
            }
            startButton.classList.add('hidden');

        }
        if (players.length < 3){
            startButton.classList.add('disabled-button');
        }
        //przyciski zwiekszanie zmniejszanie
    }


    $( window ).resize(function() {
        $(".content").addClass("mobile")
    });
    
    class Player {
    constructor(name) {
        this.name = name;
    }
}