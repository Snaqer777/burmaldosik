from mcstatus import JavaServer

def get_server_status(host: str, port: int = 25565, bedrock: bool = False):
    try:
        print(f"Подключаюсь к {host}:{port}")
        server = JavaServer(host, port, timeout=10)
        status = server.status()
        print(f"Успех! Игроков: {status.players.online}")
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
        print(f"Ошибка подключения: {e}")
        return {"online": False, "error": str(e)}