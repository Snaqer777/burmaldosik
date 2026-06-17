from mcstatus import JavaServer, BedrockServer

def get_server_status(host: str, port: int = 25565, bedrock: bool = False):
    try:
        if bedrock:
            server = BedrockServer.lookup(f"{host}:{port}")
            status = server.status()
            return {
                "online": True,
                "players_online": status.players_online,
                "players_max": status.players_max,
                "motd": status.motd,
                "version": status.version.name,
                "players": []
            }
        else:
            server = JavaServer.lookup(f"{host}:{port}")
            status = server.status()
            players = []
            if status.players.sample:
                players = [p.name for p in status.players.sample]
            return {
                "online": True,
                "players_online": status.players.online,
                "players_max": status.players.max,
                "motd": status.description,
                "version": status.version.name,
                "players": players
            }
    except Exception as e:
        return {
            "online": False,
            "error": str(e)
        }