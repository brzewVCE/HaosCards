var acknowledgements = {};
var attemptsLimit = 50;

function send_data(function_name, data, gamecode) {
    var attempts = 0;
    var player_room = "{{ session['player_room'] }}";
    var acknowledgement_id = Math.random().toString(36).substr(2, 9);
    var sendAndAwaitAcknowledgement = function() {
    return new Promise(function(resolve, reject) {
        socket.emit(function_name, data, gamecode, acknowledgement_id);
        
        var interval = setInterval(function() {
            if (acknowledgements[acknowledgement_id]) {
                resolve(acknowledgements[acknowledgement_id]);
                clearInterval(interval);
            } else if (attempts >= attemptsLimit) {
                reject('No acknowledgement received');
                clearInterval(interval);
            }
            attempts++;
        }, 100);
    });
};

sendAndAwaitAcknowledgement().then(function(acknowledgement) {
    console.log('Acknowledgement received:', acknowledgement);
}).catch(function(error) {
    console.log('Error:', error);
    if (attempts < attemptsLimit) {
        sendAndAwaitAcknowledgement();
    }
});
}