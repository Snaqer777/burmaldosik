import urllib.request
import json

def get_server_status(host: str, port: int = 25565, bedrock: bool = False):
    try:
        url = f"https://api.mcsrvstat.us/2/{host}:{port}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read().decode()
            print(f"API ответ: {raw[:500]}")  # выводим первые 500 символов
            data = json.loads(raw)

        if not data.get("online"):
            return {"online": False, "error": f"API говорит оффлайн: {raw[:200]}"}

        players = []
        if data.get("players", {}).get("list"):
            players = data["players"]["list"]

        return {
            "online": True,
            "players_online": data.get("players", {}).get("online", 0),
            "players_max": data.get("players", {}).get("max", 0),
            "motd": data.get("motd", {}).get("clean", [""])[0] if isinstance(data.get("motd", {}).get("clean"), list) else data.get("motd", {}).get("clean", ""),
            "version": data.get("version", "неизвестно"),
            "players": players
        }
    except Exception as e:
        return {"online": False, "error": str(e)}