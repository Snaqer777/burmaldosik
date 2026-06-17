import urllib.request
import json

def get_server_status(host: str, port: int = 25565, bedrock: bool = False):
    try:
        url = f"https://api.mcstatus.io/v2/status/java/{host}:{port}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())

        if not data.get("online"):
            return {"online": False, "error": "Сервер недоступен"}

        players = []
        if data.get("players", {}).get("list"):
            players = [p.get("name_clean", p.get("name", "")) for p in data["players"]["list"]]

        return {
            "online": True,
            "players_online": data.get("players", {}).get("online", 0),
            "players_max": data.get("players", {}).get("max", 0),
            "motd": data.get("motd", {}).get("clean", ""),
            "version": data.get("version", {}).get("name_clean", "неизвестно"),
            "players": players
        }
    except Exception as e:
        return {"online": False, "error": str(e)}