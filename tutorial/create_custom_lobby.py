import asyncio
import willump

# ---------------------------------------------
# Get Summoner Data
# ---------------------------------------------
async def get_summoner_data():
    summoner = await (await wllp.request("GET", "/lol-summoner/v1/current-summoner")).json()
    print(f"summonerName:    {summoner['displayName']}")
    print(f"summonerLevel:   {summoner['summonerLevel']}")
    print(f"profileIconId:   {summoner['profileIconId']}")
    print(f"summonerId:      {summoner['summonerId']}")
    print(f"puuid:           {summoner['puuid']}")
    print(f"---")


# ---------------------------------------------
# Create Lobby
# ---------------------------------------------
async def create_lobby():
    custom = {
        "customGameLobby": {
            "configuration": {
                "gameMode": "PRACTICETOOL",
                "gameMutator": "",
                "gameServerRegion": "",
                "mapId": 11,
                "mutators": {"id": 1},
                "spectatorPolicy": "AllAllowed",
                "teamSize": 5,
            },
            "lobbyName": "PRACTICETOOL",
            "lobbyPassword": "",
        },
        "isCustom": True,
    }
    await wllp.request("POST", "/lol-lobby/v2/lobby", data=custom)


# ---------------------------------------------
# Add Team1 Bots By Champion ID
# ---------------------------------------------
async def add_bots_team1():
    soraka = {"championId": 16, "botDifficulty": "EASY", "teamId": "100"}
    await wllp.request("POST", "/lol-lobby/v1/lobby/custom/bots", data=soraka)


# ---------------------------------------------
# Add Team2 Bots By Champion Name
# ---------------------------------------------
async def add_bots_team2():
    available_bots = await wllp.request("GET", "/lol-lobby/v2/lobby/custom/available-bots")
    champions = {bot["name"]: bot["id"] for bot in await available_bots.json()}

    team2 = ["Caitlyn", "Blitzcrank", "Darius", "Morgana", "Lux"]

    for name in team2:
        bot = {
            "championId": champions[name],
            "botDifficulty": "MEDIUM",
            "teamId": "200",
        }
        await wllp.request("POST", "/lol-lobby/v1/lobby/custom/bots", data=bot)


#---------------------------------------------
# Websocket Listening
#---------------------------------------------

async def subscription_lobby_created():
    event_lobby_created = await wllp.subscribe('OnJsonApiEvent')
    wllp.subscription_filter_endpoint(event_lobby_created, '/lol-lobby/v2/lobby', handler=lobby_created)

async def lobby_created(event):
    print(f"The summoner {event['data']['localMember']['summonerName']} created a lobby.")

# ---------------------------------------------
# main
# ---------------------------------------------

async def main():
    global wllp
    wllp = await willump.start()
    await get_summoner_data()
    await subscription_lobby_created()
    await create_lobby()
    await add_bots_team1()
    await wllp.close()

if __name__ == "__main__":
    # uncomment this line if you want to see willump complain (debug log)
	# logging.getLogger().setLevel(level=logging.DEBUG)
    try:
      asyncio.run(main())
    except KeyboardInterrupt:
      asyncio.run(wllp.close())
      print()
