import os
import requests
import pandas as pd
import time

# =========================================
# CONFIGURAÇÕES
# =========================================
API_KEY = "RGAPI-ce910ef3-1b2e-4c75-9980-e40d444085b3".strip()

headers = {
    "X-Riot-Token": API_KEY
}

arquivo_players = "players_all_elos_full.csv"
arquivo_saida = "matches_data_full_3partidas.csv"
arquivo_progresso = "progresso_puuid.txt"
arquivo_log = "log_full.csv"

# Quantas partidas buscar por player
partidas_por_player = 3

# Salvar a cada X players processados
salvar_a_cada = 100

# =========================================
# RATE LIMIT
# =========================================
request_count = 0
start_time = time.time()


def controlar_rate():
    global request_count, start_time

    request_count += 1

    if request_count >= 90:
        elapsed = time.time() - start_time

        if elapsed < 120:
            sleep_time = 120 - elapsed
            print(f"\nEsperando {sleep_time:.1f}s para respeitar o limite da API...")
            time.sleep(sleep_time)

        request_count = 0
        start_time = time.time()

    # proteção do limite por segundo
    time.sleep(0.06)


# =========================================
# FUNÇÕES AUXILIARES
# =========================================
def salvar_parcial(data_list, nome_arquivo):
    if len(data_list) == 0:
        return

    df_temp = pd.DataFrame(data_list)

    if not os.path.exists(nome_arquivo):
        df_temp.to_csv(nome_arquivo, index=False)
    else:
        df_temp.to_csv(nome_arquivo, mode="a", header=False, index=False)


def salvar_log_parcial(log_list, nome_arquivo):
    if len(log_list) == 0:
        return

    df_log = pd.DataFrame(log_list)

    if not os.path.exists(nome_arquivo):
        df_log.to_csv(nome_arquivo, index=False)
    else:
        df_log.to_csv(nome_arquivo, mode="a", header=False, index=False)


def ler_progresso():
    if os.path.exists(arquivo_progresso):
        with open(arquivo_progresso, "r", encoding="utf-8") as f:
            valor = f.read().strip()
            if valor.isdigit():
                return int(valor)
    return 0


def salvar_progresso(indice):
    with open(arquivo_progresso, "w", encoding="utf-8") as f:
        f.write(str(indice))


# =========================================
# LER PLAYERS
# =========================================
try:
    df = pd.read_csv(arquivo_players)
except FileNotFoundError:
    print(f"Erro: arquivo '{arquivo_players}' não encontrado.")
    raise SystemExit

colunas_obrigatorias = ["puuid", "tier"]
for col in colunas_obrigatorias:
    if col not in df.columns:
        print(f"Erro: coluna obrigatória '{col}' não existe.")
        raise SystemExit

df = df.dropna(subset=["puuid", "tier"])
df = df.drop_duplicates(subset=["puuid"]).reset_index(drop=True)

print(f"Total de players únicos encontrados: {len(df)}")

# =========================================
# RETOMADA
# =========================================
indice_inicial = ler_progresso()
print(f"Iniciando a partir do índice: {indice_inicial}")

# =========================================
# CACHE DE MATCHES EM MEMÓRIA
# =========================================
match_cache = {}

# =========================================
# COLETA
# =========================================
data_buffer = []
log_list = []

for idx in range(indice_inicial, len(df)):
    row = df.iloc[idx]

    puuid = row["puuid"]
    tier = row["tier"]
    division = row["division"] if "division" in df.columns else None
    rank = row["rank"] if "rank" in df.columns else None
    league_points = row["leaguePoints"] if "leaguePoints" in df.columns else None

    print(f"\n[{idx + 1}/{len(df)}] {tier} {division} | buscando até {partidas_por_player} partidas")

    # =========================================
    # 1. LISTA DE MATCH IDS DO PLAYER
    # =========================================
    url_matches = (
        f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"
        f"{puuid}/ids?start=0&count={partidas_por_player}"
    )

    r = requests.get(url_matches, headers=headers)
    controlar_rate()

    log_list.append({
        "tipo": "lista_partidas",
        "indice_player": idx,
        "puuid": puuid,
        "match_id": None,
        "status_code": r.status_code
    })

    if r.status_code != 200:
        print(f"Erro ao buscar lista de partidas: {r.status_code}")
        salvar_progresso(idx + 1)
        continue

    match_ids = r.json()
    print(f"Match IDs encontrados: {len(match_ids)}")

    if len(match_ids) == 0:
        salvar_progresso(idx + 1)
        continue

    # =========================================
    # 2. PARA CADA MATCH ID
    # =========================================
    for match_id in match_ids:
        # Se já estiver no cache, reutiliza
        if match_id in match_cache:
            match = match_cache[match_id]
            print(f"Match em cache: {match_id}")
        else:
            url_match = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"

            r = requests.get(url_match, headers=headers)
            controlar_rate()

            log_list.append({
                "tipo": "detalhe_partida",
                "indice_player": idx,
                "puuid": puuid,
                "match_id": match_id,
                "status_code": r.status_code
            })

            if r.status_code != 200:
                print(f"Erro no detalhe da partida {match_id}: {r.status_code}")
                continue

            match = r.json()
            match_cache[match_id] = match
            print(f"Match baixada: {match_id}")

        if "info" not in match or "participants" not in match["info"]:
            print(f"Partida sem participants: {match_id}")
            continue

        participants = match["info"]["participants"]
        jogador_encontrado = False

        for p in participants:
            if p.get("puuid") == puuid:
                jogador_encontrado = True

                data_buffer.append({
                    "match_id": match_id,
                    "puuid": puuid,
                    "tier": tier,
                    "division": division,
                    "rank": rank,
                    "league_points": league_points,
                    "champion": p.get("championName"),
                    "win": p.get("win"),
                    "lane": p.get("teamPosition"),
                    "kills": p.get("kills"),
                    "deaths": p.get("deaths"),
                    "assists": p.get("assists"),
                    "gold_earned": p.get("goldEarned"),
                    "total_damage_to_champions": p.get("totalDamageDealtToChampions"),
                    "vision_score": p.get("visionScore"),
                    "total_minions_killed": p.get("totalMinionsKilled"),
                    "champ_level": p.get("champLevel"),
                    "game_duration": match["info"].get("gameDuration"),
                    "game_mode": match["info"].get("gameMode"),
                    "queue_id": match["info"].get("queueId")
                })

                print(
                    f"OK | Match: {match_id} | Champ: {p.get('championName')} | "
                    f"Win: {p.get('win')} | Lane: {p.get('teamPosition')}"
                )
                break

        if not jogador_encontrado:
            print(f"Jogador não encontrado dentro da partida {match_id}")

    # =========================================
    # 3. SALVAR EM LOTES
    # =========================================
    if (idx + 1) % salvar_a_cada == 0:
        salvar_parcial(data_buffer, arquivo_saida)
        salvar_log_parcial(log_list, arquivo_log)

        data_buffer = []
        log_list = []

        salvar_progresso(idx + 1)
        print(f"\nProgresso salvo até o player {idx + 1}")

# =========================================
# SALVAR RESTANTE
# =========================================
salvar_parcial(data_buffer, arquivo_saida)
salvar_log_parcial(log_list, arquivo_log)

salvar_progresso(len(df))

print("\nFINALIZADO!")
print(f"Arquivo de dados: {arquivo_saida}")
print(f"Arquivo de log: {arquivo_log}")
print(f"Arquivo de progresso: {arquivo_progresso}")