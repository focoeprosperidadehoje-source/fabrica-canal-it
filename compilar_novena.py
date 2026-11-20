"""
Bloco 2 — Compilatore di Novene (IT)
Rileva serie complete (9 giorni pubblici) nel canale IT, scarica con yt-dlp,
concatena senza re-encode e carica come unlisted.
"""

import os, sys, json, re, time, datetime, subprocess
from collections import defaultdict
from zoneinfo import ZoneInfo

from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as YTCredentials
from google.auth.transport.requests import Request
import gspread
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==============================================================================
# 1. CONFIG
# ==============================================================================
GOOGLE_JSON   = os.environ.get("GOOGLE_CREDENTIALS")
YT_TOKEN_JSON = os.environ.get("YOUTUBE_TOKEN_JSON")
SHEET_ID      = "1KgIjWrLUVlllhlZB1R9fkHGxxZlLsax1aOVGZrYwgnU"
PASTA_TEMP    = "/tmp/novena_comp_it"
PUBLISH_DELAY_BASE_H = 48

CFG = {
    "channel_id":    "UCa1_Xd4tOUd6GSPNu7auY4A",
    "aba_sheet":     "IT_NOVENAS_COMPILADAS",
    "playlist_nome": "Novene Complete — Madonna",
    "idioma":        "it-IT",
    "descricao_tpl": (
        "🙏 {serie} — Novena completa in 9 giorni\n\n"
        "Tutti i 9 giorni insieme per pregare senza interruzione.\n\n"
        "▶ Preghiera in diretta 24H → https://youtube.com/channel/UCa1_Xd4tOUd6GSPNu7auY4A/live\n\n"
        "#Novena #Madonna #PreghieraCattolica #MadonnaLourdes #Fede #Miracoli"
    ),
    "titulo_tpl": "Novena completa in 9 giorni — {serie} 🙏",
    "tags": ["novena completa", "9 giorni", "madonna", "preghiera", "madonna di lourdes",
             "fede", "miracoli", "rosario", "cattolico"],
}

os.makedirs(PASTA_TEMP, exist_ok=True)

# ==============================================================================
# 2. AUTH
# ==============================================================================
creds_sheets = Credentials.from_service_account_info(
    json.loads(GOOGLE_JSON),
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
gc = gspread.authorize(creds_sheets)

creds_yt = YTCredentials.from_authorized_user_info(json.loads(YT_TOKEN_JSON.lstrip('﻿')))
if creds_yt.expired and creds_yt.refresh_token:
    creds_yt.refresh(Request())
youtube = build('youtube', 'v3', credentials=creds_yt)

# ==============================================================================
# 3. SHEET HELPER
# ==============================================================================
HEADERS_COMP = ['canal', 'video_id', 'serie', 'titulo', 'dias',
                'data_geracao', 'publish_at', 'status']

def obter_aba_compiladas():
    sheet = gc.open_by_key(SHEET_ID)
    try:
        return sheet.worksheet(CFG['aba_sheet'])
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title=CFG['aba_sheet'], rows=500, cols=10)
        ws.append_row(HEADERS_COMP)
        time.sleep(2)
        return ws

def series_ja_compiladas(ws):
    registros = ws.get_all_records()
    return {str(r.get('serie', '')).strip() for r in registros if r.get('serie')}

# ==============================================================================
# 4. DESCOBRIR VÍDEOS DE NOVENA
# IT usa "Giorno N" no título
# ==============================================================================
PADRAO_DIA_IT = re.compile(r'\bGiorno\s+(\d{1,2})\b', re.IGNORECASE)

def extrair_dia(titulo):
    m = PADRAO_DIA_IT.search(titulo)
    return int(m.group(1)) if m else None

def calcular_serie(titulo):
    s = PADRAO_DIA_IT.sub('', titulo)
    s = re.sub(r'\s*🙏.*', '', s)
    s = re.sub(r'\s*[-—–|]+\s*$', '', s).strip()
    return re.sub(r'\s{2,}', ' ', s)

def listar_videos_canal():
    from googleapiclient.errors import HttpError
    uploads_id = "UU" + CFG['channel_id'][2:]
    videos = []
    page_token = None
    print("  📺 Recupero video del canale IT...")
    while True:
        try:
            resp = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_id,
                maxResults=50,
                pageToken=page_token
            ).execute()
        except HttpError as e:
            if e.resp.status == 403 and "quotaExceeded" in str(e):
                print("[WARN] quotaExceeded — quota esaurita. Nessuna compilazione.")
                return []
            raise
        for item in resp.get("items", []):
            sn = item["snippet"]
            vid = sn["resourceId"]["videoId"]
            videos.append({
                "video_id": vid,
                "titulo": sn.get("title", ""),
                "published_at": sn.get("publishedAt", ""),
            })
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.5)
    print(f"  → {len(videos)} video trovati")
    return videos

def agrupar_novenas(videos):
    grupos = defaultdict(dict)
    for v in videos:
        dia = extrair_dia(v['titulo'])
        if dia is None or dia < 1 or dia > 9:
            continue
        serie = calcular_serie(v['titulo'])
        if not serie:
            continue
        if dia not in grupos[serie] or v['published_at'] > grupos[serie][dia]['published_at']:
            grupos[serie][dia] = v

    completas = []
    for serie, dias in grupos.items():
        if all(d in dias for d in range(1, 10)):
            completas.append({
                'serie': serie,
                'videos': [dias[d] for d in range(1, 10)],
            })
    return completas

# ==============================================================================
# 5. PLAYLIST
# ==============================================================================
def obter_ou_criar_playlist():
    nome = CFG['playlist_nome']
    page_token = None
    while True:
        resp = youtube.playlists().list(
            part="snippet", mine=True, maxResults=50, pageToken=page_token
        ).execute()
        for p in resp.get("items", []):
            if p["snippet"]["title"] == nome:
                pid = p["id"]
                print(f"  📂 Playlist trovata: {nome} → {pid}")
                return pid
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    r = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": nome, "defaultLanguage": CFG['idioma']},
            "status": {"privacyStatus": "public"},
        }
    ).execute()
    pid = r["id"]
    print(f"  📂 Playlist CREATA: {nome} → {pid}")
    return pid

# ==============================================================================
# 6. DOWNLOAD + COMPILE
# ==============================================================================
COOKIES_PATH = os.path.join(PASTA_TEMP, "yt_cookies.txt")

def _preparar_cookies():
    conteudo = os.environ.get("YT_COOKIES", "").lstrip('﻿')
    if conteudo.strip():
        with open(COOKIES_PATH, "w", encoding="utf-8") as f:
            f.write(conteudo)
        print("  🍪 Cookie caricati per yt-dlp")
        return True
    return False

def baixar_video(video_id, destino_dir):
    url = f"https://www.youtube.com/watch?v={video_id}"
    saida = os.path.join(destino_dir, f"{video_id}.mp4")
    if os.path.exists(saida):
        return saida
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best[ext=mp4]",
        "--merge-output-format", "mp4",
        "--sleep-interval", "3",
        "--max-sleep-interval", "7",
        "--extractor-retries", "3",
        "--fragment-retries", "3",
        "-o", saida,
    ]
    if os.path.exists(COOKIES_PATH):
        cmd += ["--cookies", COOKIES_PATH]
    cmd.append(url)
    for tentativa in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(saida):
            mb = os.path.getsize(saida) / (1024 * 1024)
            print(f"    ✅ {video_id} scaricato ({mb:.0f} MB)")
            return saida
        stderr = r.stderr
        if "Only images are available" in stderr or "Requested format is not available" in stderr:
            print(f"    ⏭️  {video_id} è un Short — serie ignorata.")
            return "SHORT"
        print(f"    ⚠️  Tentativo {tentativa+1}: {stderr[-200:]}")
        time.sleep(10)
    return None

def compilar_videos(video_paths, saida):
    concat_txt = os.path.join(PASTA_TEMP, "concat_novena.txt")
    with open(concat_txt, "w") as f:
        for p in video_paths:
            f.write(f"file '{p}'\n")
    r = subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-c", "copy", saida
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ❌ Errore concat: {r.stderr[-500:]}")
        return None
    mb = os.path.getsize(saida) / (1024 * 1024)
    print(f"  ✅ Compilazione: {mb:.0f} MB")
    return saida

# ==============================================================================
# 7. UPLOAD
# ==============================================================================
def upload_compilacao(video_path, titulo, descricao, tags):
    body = {
        "snippet": {
            "title": titulo[:100],
            "description": descricao,
            "tags": tags[:15],
            "categoryId": "22",
            "defaultLanguage": CFG['idioma'],
            "defaultAudioLanguage": CFG['idioma'],
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False,
            "selfDeclaredMadeWithAlteredContent": True,
        }
    }
    for tentativa in range(3):
        try:
            resp = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
            ).execute()
            vid = resp.get("id")
            print(f"  ✅ Upload OK! ID: {vid}")
            return vid
        except Exception as e:
            print(f"  ❌ Tentativo {tentativa+1}: {e}")
            time.sleep(15)
    return None

def adicionar_a_playlist(video_id, playlist_id):
    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={"snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id}
            }}
        ).execute()
        print(f"  📂 Aggiunto alla playlist.")
    except Exception as e:
        print(f"  ⚠️  Playlist insert: {e}")

# ==============================================================================
# 8. MAIN
# ==============================================================================
def main():
    print(f"\n📿 Bloco 2 — Compilatore di Novene — Canale IT\n")

    _preparar_cookies()
    aba = obter_aba_compiladas()
    ja_compiladas = series_ja_compiladas(aba)
    print(f"Serie già compilate: {len(ja_compiladas)}")

    todos_videos = listar_videos_canal()
    grupos_completos = agrupar_novenas(todos_videos)
    print(f"Serie complete (9 giorni) trovate: {len(grupos_completos)}")

    pendentes = [g for g in grupos_completos if g['serie'] not in ja_compiladas]
    print(f"In attesa di compilazione: {len(pendentes)}")

    if not pendentes:
        print("✅ Niente da compilare.")
        return

    pendentes.sort(key=lambda g: g['videos'][0]['published_at'])

    playlist_id = obter_ou_criar_playlist()
    agora = datetime.datetime.now(ZoneInfo("America/Sao_Paulo"))

    for i, grupo in enumerate(pendentes):
        serie = grupo['serie']
        print(f"\n{'='*60}")
        print(f"📿 Serie {i+1}/{len(pendentes)}: {serie}")

        publish_at = agora + datetime.timedelta(hours=PUBLISH_DELAY_BASE_H + i * 24)

        pasta_serie = os.path.join(PASTA_TEMP, f"serie_{i}")
        os.makedirs(pasta_serie, exist_ok=True)
        paths = []
        falhou = False
        for v in grupo['videos']:
            p = baixar_video(v['video_id'], pasta_serie)
            if p == "SHORT":
                print(f"  ⏭️  Serie ignorata (contiene uno Short).")
                falhou = True
                break
            if not p:
                print(f"  ❌ Download fallito {v['video_id']} — serie ignorata.")
                falhou = True
                break
            paths.append(p)

        if falhou:
            continue

        saida = os.path.join(PASTA_TEMP, f"novena_compiled_{i}.mp4")
        if os.path.exists(saida):
            os.remove(saida)
        video_comp = compilar_videos(paths, saida)
        if not video_comp:
            continue

        titulo = CFG['titulo_tpl'].format(serie=serie)
        descricao = CFG['descricao_tpl'].format(serie=serie)
        video_id = upload_compilacao(video_comp, titulo, descricao, CFG['tags'])
        if not video_id:
            continue

        adicionar_a_playlist(video_id, playlist_id)

        try:
            dias_str = ",".join(v['video_id'] for v in grupo['videos'])
            aba.append_row([
                "IT", video_id, serie, titulo, dias_str,
                agora.strftime('%Y-%m-%d %H:%M'),
                publish_at.strftime('%Y-%m-%d %H:%M'),
                'unlisted'
            ])
            print(f"  📋 Registrato → pubblica {publish_at.strftime('%d/%m %H:%M')} BRT")
        except Exception as e:
            print(f"  ⚠️  Foglio: {e}")

        for p in paths:
            try: os.remove(p)
            except: pass
        try: os.remove(video_comp)
        except: pass

    print(f"\n📿 Compilatore terminato — {len(pendentes)} serie elaborate.")

if __name__ == "__main__":
    main()
