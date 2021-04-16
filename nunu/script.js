function dothing() {
  var myInit = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({
      "customGameLobby": {
        "configuration": {
          "gameMode": "PRACTICETOOL",
          "gameMutator": "",
          "gameServerRegion": "",
          "mapId": 11,
          "mutators": {"id": 1},
          "spectatorPolicy": "AllAllowed",
          "teamSize": 5
        },
        "lobbyName":"Name",
        "lobbyPassword":null
      },
      "isCustom":true
    })
  };

  var myRequest = new Request('https://' + document.getElementById('host').value + '/lol-lobby/v2/lobby', myInit);

  fetch(myRequest)
  .then(response => response.json())
  .then(function(response) {
    console.log(response)
    document.getElementById('resp').textContent = JSON.stringify(response, undefined, 2)
  });
}
