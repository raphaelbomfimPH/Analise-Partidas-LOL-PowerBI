import requests
import pandas as pd
import time

API_KEY = "RGAPI-8302d1e5-9e68-4f0c-aa37-f897e1d37465"

headers = {
    "X-Riot-Token": API_KEY
}

tiers = [
    "IRON",
    "BRONZE",
    "SILVER",
    "GOLD",
    "PLATINUM",
    "EMERALD",
    "DIAMOND"
]

divisions = ["IV", "III", "II", "I"]

all_data = []

for tier in tiers:
    for division in divisions:
        url = f"https://br1.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            for player in data:
                player["tier"] = tier
                player["division"] = division
                all_data.append(player)

            print(f"OK: {tier} {division}")
        else:
            print(f"ERRO: {tier} {division} - {response.status_code}")

        time.sleep(1)

df = pd.DataFrame(all_data)
df.to_csv("players_all_elos.csv", index=False)

print("FINALIZADO!")

# ===== ELOS ALTOS =====
high_tiers_urls = [
    "https://br1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5",
    "https://br1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5",
    "https://br1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
]

for url in high_tiers_urls:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        for player in data["entries"]:
            player["tier"] = data["tier"]
            player["division"] = "I"
            all_data.append(player)

        print(f"OK HIGH: {data['tier']}")
    else:
        print("Erro HIGH:", response.status_code)

    time.sleep(1)

# ===== SALVAR TUDO =====
df = pd.DataFrame(all_data)
df.to_csv("players_all_elos_full.csv", index=False)

print("AGORA COMPLETO!")