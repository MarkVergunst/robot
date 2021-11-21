var roomCode = document.getElementById("room_code").getAttribute("data-id");

var connectionString = 'ws://' + window.location.host + '/ws/' + roomCode + '/';
var gameSocket = new WebSocket(connectionString);

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function forward(pressed) {
    let message = pressed ? "start riding forward" : "stopped riding forward";
    let data = {
        "event": "ride",
        "message": message,
        "action": "forward",
        "pressed": pressed
    }
    gameSocket.send(JSON.stringify(data))
}

function backward(pressed) {
    let message = pressed ? "Start riding backwards" : "Stopped riding backwards";
    let data = {
        "event": "ride",
        "message": message,
        "action": "backward",
        "pressed": pressed
    }
    gameSocket.send(JSON.stringify(data))
}

function left(pressed) {
    let message = pressed ? "Start riding left" : "Stopped riding left";
    let data = {
        "event": "ride",
        "message": message,
        "action": "left",
        "pressed": pressed
    }
    gameSocket.send(JSON.stringify(data))
}

function right(pressed) {
    let message = pressed ? "Start riding right" : "Stopped riding right";

    let data = {
        "event": "ride",
        "message": message,
        "action": "right",
        "pressed": pressed
    }
    gameSocket.send(JSON.stringify(data))
}

// Main function which handles the connection
// of websocket.
function connect() {
    gameSocket.onopen = function open() {
        console.log('WebSockets connection created.');
        // on websocket open, send the START event.
        gameSocket.send(JSON.stringify({
            "event": "connect",
            "message": "Connection is set up."
        }));
    };

    gameSocket.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function () {
            connect();
        }, 1000);
    };
    // Sending the info about the room
    gameSocket.onmessage = function (e) {
        // On getting the message from the server
        // Do the appropriate steps on each event.
        let data = JSON.parse(e.data);
        // data = data["payload"];
        let message = data['message'];
        let event = data["event"];
        console.log(data)
        document.getElementById('channel-text').innerHTML = capitalizeFirstLetter(message);

    };

    if (gameSocket.readyState === WebSocket.OPEN) {
        gameSocket.onopen(undefined);
    }
}

//call the connect function at the start.
connect();
