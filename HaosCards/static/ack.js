function send_data(function_name, data, acknowledgements) {
    var attempts = 0;
    var attemptsLimit = 50;
    var acknowledgement_id = Math.random().toString(36).substr(2, 9);
    data['acknowledgement_id'] = acknowledgement_id;
    acknowledgements[acknowledgement_id] = 'false';
    
    var intervalId = setInterval(function() {
    if (attempts >= attemptsLimit) {
        console.log('Max attempts reached');
        clearInterval(intervalId);
        return;
    }
    if (acknowledgements[acknowledgement_id] === 'true') {
        console.log('Acknowledgement received');
        clearInterval(intervalId);
        return;
    }
    socket.emit(function_name, data);
    attempts++;
    if (acknowledgements[acknowledgement_id] === 'true') {
        console.log('Acknowledgement received');
        clearInterval(intervalId);
        return;
    }
}, 150);
}

function client_response(data) {
    var acknowledgement_id = data.acknowledgement_id
    console.log('client_response: ',acknowledgement_id)
    socket.emit('client_response', acknowledgement_id)
}

function server_response(data) {
    var acknowledgement_id = data.acknowledgement_id;
    console.log('Received server response: ', acknowledgement_id);
    return acknowledgements[acknowledgement_id] = "true";
};