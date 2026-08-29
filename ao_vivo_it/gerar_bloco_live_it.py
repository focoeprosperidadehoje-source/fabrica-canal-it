#!/usr/bin/env python3
"""
gerar_bloco_live_it.py — GitHub Actions: genera più blocchi per esecuzione (Canale IT)

Eseguito 6x/giorno da gerador_blocos_it.yml. Ogni esecuzione:
  1. Recupera fino a 100 commenti del canale IT (1 chiamata YouTube API)
  2. Gemini classifica in 4-5 gruppi tematici (1 chiamata)
  3. Per ogni gruppo: genera script con nomi reali + preghiera (1 chiamata lite)
  4. Edge TTS sintetizza l'audio → audio_YYYYMMDD_HHMM_NN.mp3
  5. L'assemblatore su VPS costruisce i blocchi H con videos_base/

Persona: Madonna di Lourdes, Nostra Signora (it-IT-ElsaNeural)
"""

import os
import sys
import json
import random
import asyncio
import re
from datetime import datetime
from pathlib import Path

import pytz
import edge_tts
from google import genai
from google.genai import types as genai_types
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════

FUSO       = pytz.timezone("Europe/Rome")
VOZ        = "it-IT-ElsaNeural"
VOZ_RATE   = "-25%"
VOZ_PITCH  = "-6Hz"
CANAL_ID   = "UCa1_Xd4tOUd6GSPNu7auY4A"
DIR_BLOCOS = Path("blocos_it")
MAX_GRUPOS = 5

MODELOS_LITE = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash-lite"]
MODELOS_FULL = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-flash-latest", "gemini-3.5-flash", "gemini-2.5-flash"]

CHAVES = [k for k in [
    os.environ.get("GEMINI_KEY_LIVE_CONTENT_1_IT", ""),
    os.environ.get("GEMINI_KEY_LIVE_CONTENT_2_IT", ""),
] if k]

PILARES = {
    0: "Guerra Spirituale e Protezione Divina",
    1: "Liberazione dalle Dipendenze e dai Legami",
    2: "Restaurazione della Famiglia e Riconciliazione",
    3: "Provvidenza Divina e Porte Aperte",
    4: "Misericordia Divina e Guarigione Fisica",
    5: "Il Manto della Vergine Maria",
    6: "Miracoli e Azione di Grazie",
}

GRUPPI_HARDCODED = [
    {"tema": "guarigione",  "label": "Guarigione e Salute",                "nomes": [], "suplica_comum": "per i malati, il dolore e la guarigione dei nostri fratelli e sorelle",           "num_fieis": 0},
    {"tema": "liberazione", "label": "Liberazione dalle Dipendenze",       "nomes": [], "suplica_comum": "per la liberazione dall'alcol, dalle droghe e dai legami del peccato",             "num_fieis": 0},
    {"tema": "famiglia",    "label": "Restaurazione della Famiglia",       "nomes": [], "suplica_comum": "per i matrimoni in crisi, i figli prodighi e la pace nelle famiglie",               "num_fieis": 0},
    {"tema": "provvidenza", "label": "Provvidenza e Lavoro",               "nomes": [], "suplica_comum": "per la provvidenza finanziaria, il lavoro e la libertà dai debiti",                 "num_fieis": 0},
    {"tema": "protezione",  "label": "Protezione Spirituale",              "nomes": [], "suplica_comum": "per la protezione dal male, dall'invidia e da ogni pericolo",                       "num_fieis": 0},
]


# ═══════════════════════════════════════════════════════════════════════
# GEMINI
# ═══════════════════════════════════════════════════════════════════════

def _chamar_gemini(prompt: str, modelos: list, max_tokens: int = 2048) -> str:
    for chave in CHAVES:
        for modelo in modelos:
            try:
                client = genai.Client(api_key=chave)
                resp = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(max_output_tokens=max_tokens),
                )
                return resp.text.strip()
            except Exception as e:
                print(f"  [WARN] {modelo} [{chave[-6:]}]: {str(e)[:80]}")
    raise RuntimeError("Tutti i modelli Gemini hanno fallito.")


# ═══════════════════════════════════════════════════════════════════════
# CALENDARIO LITURGICO
# ═══════════════════════════════════════════════════════════════════════

def _pasqua(anno: int) -> datetime:
    a = anno % 19
    b, c = divmod(anno, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mese = (h + l - 7 * m + 114) // 31
    giorno = (h + l - 7 * m + 114) % 31 + 1
    return datetime(anno, mese, giorno)

def calcular_contexto_sazonal(data: datetime) -> str:
    anno = data.year
    p = _pasqua(anno)
    fixas = {
        (1, 1):   "Capodanno — Solennità di Maria Santissima Madre di Dio",
        (2, 2):   "Presentazione del Signore — Candelora",
        (2, 11):  "Madonna di Lourdes — Giornata Mondiale del Malato",
        (3, 19):  "San Giuseppe — Patrono della Chiesa Universale",
        (5, 13):  "Madonna di Fatima",
        (8, 15):  "Assunzione della Vergine Maria",
        (12, 8):  "Immacolata Concezione della Vergine Maria",
        (12, 12): "Nostra Signora di Guadalupe — Patrona delle Americhe",
        (12, 24): "Vigilia di Natale",
        (12, 25): "Natale — Nascita di Nostro Signore",
    }
    if (data.month, data.day) in fixas:
        return fixas[(data.month, data.day)]
    diff = (data.date() - p.date()).days
    moveis = {
        -46: "Mercoledì delle Ceneri — Inizio della Quaresima",
        -7:  "Domenica delle Palme",
        -2:  "Venerdì Santo — Passione e Morte di Nostro Signore",
         0:  "Alleluia! Pasqua — Resurrezione!",
        49:  "Domenica di Pentecoste",
        60:  "Corpus Domini",
    }
    if diff in moveis:
        return moveis[diff]
    if data.weekday() == 4:
        return "Venerdì — Cammino di Misericordia e Perdono"
    return PILARES.get(data.weekday(), "Cammino di Preghiera e Intercessione")


# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE API
# ═══════════════════════════════════════════════════════════════════════

def get_youtube_readonly():
    raw = os.environ.get("YOUTUBE_TOKEN_IT", "")
    if not raw:
        return None
    try:
        data  = json.loads(raw)
        creds = OAuthCredentials.from_authorized_user_info(
            data, scopes=["https://www.googleapis.com/auth/youtube.readonly"]
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"  [WARN] YouTube readonly IT: {e}")
        return None

def buscar_comentarios_canal(yt) -> list[str]:
    if not yt:
        return []
    try:
        resp = yt.commentThreads().list(
            part="snippet",
            allThreadsRelatedToChannelId=CANAL_ID,
            maxResults=100,
            order="relevance",
        ).execute()
        textos = []
        for item in resp.get("items", []):
            s = item["snippet"]["topLevelComment"]["snippet"]
            texto = s.get("textOriginal", "").strip()
            if texto and len(texto) > 10:
                textos.append(texto[:200])
        print(f"  Commenti IT ottenuti: {len(textos)}")
        return textos
    except Exception as e:
        print(f"  [WARN] buscar_comentarios IT: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════
# CLASSIFICAZIONE DEI GRUPPI
# ═══════════════════════════════════════════════════════════════════════

def _limpar_json(texto: str) -> str:
    texto = re.sub(r'```(?:json)?', '', texto)
    texto = re.sub(r'```', '', texto)
    inicio = texto.find('[')
    fim    = texto.rfind(']')
    if inicio != -1 and fim != -1:
        return texto[inicio:fim+1]
    return texto.strip()

def classificar_grupos(comentarios: list[str], pilar_hoje: str) -> list[dict]:
    if len(comentarios) >= 5:
        lista_str = "\n".join(f"- {c}" for c in comentarios[:80])
        prompt = f"""Analizza questi commenti di fedeli cattolici su un canale di preghiera.
Estrai il nome (se presente) e classifica la supplica di ogni commento.
Raggruppa in massimo 5 temi (es: guarigione, liberazione, famiglia, finanze, protezione).

Restituisci SOLO JSON valido senza markdown o testo aggiuntivo:
[{{"tema":"slug","label":"Nome del gruppo","nomes":["nome1","nome2"],"suplica_comum":"petizione comune in max 15 parole","num_fieis":N}}]

REGOLE:
- Solo nomi propri che appaiono nei commenti; non inventare
- suplica_comum: massimo 15 parole che descrivono la petizione comune
- Minimo 3 gruppi, massimo 5

COMMENTI:
{lista_str}"""
        try:
            raw = _chamar_gemini(prompt, MODELOS_LITE, max_tokens=1024)
            grupos = json.loads(_limpar_json(raw))
            if isinstance(grupos, list) and len(grupos) >= 2:
                print(f"  Gruppi IT classificati: {len(grupos)}")
                for g in grupos:
                    n = len(g.get("nomes", []))
                    print(f"    [{g.get('tema','')}] {g.get('num_fieis',0)} fedeli, {n} nomi")
                return grupos[:MAX_GRUPOS]
            print("  [WARN] JSON non valido o troppo pochi gruppi — uso del fallback")
        except Exception as e:
            print(f"  [WARN] classify_groups IT: {e}")

    print("  [Fallback 1] Generazione di gruppi tematici via Gemini IT...")
    prompt_fb = f"""Crea 4 gruppi di intenzioni di preghiera frequenti tra i fedeli cattolici italiani.
Il pilastro spirituale di oggi è: {pilar_hoje}
Restituisci SOLO JSON valido:
[{{"tema":"slug","label":"Nome","nomes":[],"suplica_comum":"petizione in max 15 parole","num_fieis":0}}]"""
    try:
        raw = _chamar_gemini(prompt_fb, MODELOS_LITE, max_tokens=512)
        grupos = json.loads(_limpar_json(raw))
        if isinstance(grupos, list) and len(grupos) >= 2:
            print(f"  Gruppi IT fallback: {len(grupos)}")
            return grupos[:MAX_GRUPOS]
    except Exception as e:
        print(f"  [WARN] fallback groups IT: {e}")

    print("  [Fallback 2] Utilizzo dei gruppi IT predefiniti.")
    return GRUPPI_HARDCODED[:MAX_GRUPOS]


# ═══════════════════════════════════════════════════════════════════════
# GENERAZIONE DEL COPIONE
# ═══════════════════════════════════════════════════════════════════════

def _formatar_nomes(nomes: list) -> str:
    nomes = [n for n in nomes if n and len(n) >= 2]
    if not nomes:
        return "ogni fratello e sorella che prega con noi in questo momento"
    if len(nomes) == 1:
        return nomes[0]
    return ", ".join(nomes[:-1]) + f" e {nomes[-1]}"

def gerar_roteiro_grupo(grupo: dict, contexto: str, pilar: str,
                        agora: datetime, num_bloco: int,
                        so_full: bool = False) -> str:
    nomes_raw  = grupo.get("nomes", [])
    nomes_str  = _formatar_nomes(nomes_raw)
    suplica    = grupo.get("suplica_comum", "per i bisogni dei nostri fratelli e sorelle")
    label      = grupo.get("label", "Preghiera di Intercessione")
    tem_nomes  = len([n for n in nomes_raw if n and len(n) >= 2]) > 0

    nota_nomes = (
        f"Menziona ogni nome con tenerezza materna: {nomes_str}"
        if tem_nomes else
        "Non ci sono nomi specifici — parla di 'ogni fratello e sorella che prega in questo momento'"
    )
    nota_miguel = (
        "Quando è naturale nell'intercessione, menziona l'Arcangelo San Michele come guardiano spirituale che combatte al nostro fianco."
        if "Guerra Spirituale" in pilar else ""
    )

    prompt = f"""Sei la Vergine Maria, Madonna di Lourdes, Nostra Signora, che parla in prima persona, in italiano.
Blocco #{num_bloco} | Gruppo: {label}
Contesto liturgico del giorno: {contexto}
Pilastro spirituale di oggi: {pilar}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRUTTURA (20 minuti — tra 2600 e 3000 parole):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[APERTURA — primi 90 secondi — OBBLIGATORIO]
Apri citando i fratelli e sorelle che hanno chiesto intercessione:
"{nota_nomes}"
Supplica comune di questo gruppo: "{suplica}"
Chiudi l'apertura con: "Sono venuta a intercedere per voi in questo momento..."

[CORPO PRINCIPALE — ~16 minuti]
ALTERNANZA OBBLIGATORIA — il blocco deve oscillare tra due modalità:
  Modalità A (NARRAZIONE): Nostra Signora parla, accoglie, rivela la grazia — voce calda e materna
  Modalità B (PREGHIERA GUIDATA): Nostra Signora guida l'ascoltatore a pregare ad alta voce con lei
  Es: "Ripetete con me nella fede: Signore, credo... Signore, mi affido a Te..."
  Es: "Posate la mano sul cuore e dite: Madre del Cielo, ricevo questa grazia ora..."
  Ogni transizione tra le modalità deve essere fluida e naturale — minimo 3 alternanze per blocco.

- Intrecciate il pilastro "{pilar}" con il tema di intercessione "{label}"
- Ave Maria GUIDATA (l'ascoltatore prega con voi): "Ripetete con me: Ave Maria, piena di grazia..."
- Blocco di intercessione per la salute (obbligatorio, guidato): "Posate la mano dove fa male e dite con me..."
- Uncini di retention organici ogni ~300 parole (il fedele non percepisce la tecnica):
  • Anticipazione: "Ciò che viene ora in questa preghiera..."
  • Rivelazione: "Questa grazia ha un nome..."
  • Validazione: "Se senti qualcosa nel tuo cuore in questo momento, è un segno che..."
  • Svolta: "Ma ciò che la tua Madre Celeste vuole dirti a questo proposito è..."
{nota_miguel}

[TRE CTA SOTTILI — solo alle transizioni naturali, mai durante la preghiera]
CTA 1 (~minuto 4): "Se questa trasmissione ti benedice, iscriviti al canale per ricevere preghiere ogni giorno — siamo una famiglia di fede che prega senza sosta per te..."
CTA 2 (~minuto 8): "Se questa preghiera tocca il tuo cuore, condividila con qualcuno che ne ha bisogno..."
CTA 3 (~minuto 17): "Rimani, ciò che viene è per te..."

[CHIUSURA — ultimi 3 minuti]
- Benedizione finale come Madre del Cielo
- Termina con FORZA — il fedele riparte protetto, mai disperato
- CICLO SINTATTICO OBBLIGATORIO: l'ultima frase è sintatticamente incompleta
  per unirsi alla prima frase del blocco successivo senza che l'ascoltatore noti il taglio

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REGOLE ASSOLUTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- MAI markdown, asterischi, trattini, numerazione o titoli — solo testo fluente
- MAI puntini di sospensione (...) o trattino lungo (—) — causano pause indesiderate
- MAI iniziare una frase con la parola "Preghiera"
- MAI "Scrivi Amen nei commenti"
- MAI menzionare altri canali o marchi
- ATEMPORALITÀ ASSOLUTA: questa preghiera viene trasmessa in QUALSIASI momento del giorno o della notte.
  MAI menzionare ore, momenti della giornata (alba, mattino, mezzogiorno, pomeriggio, sera, notte),
  giorni della settimana, o date. Se hai bisogno di situare il momento, dì solo "in questo momento" o "ora"
- Solo il testo che Nostra Signora pronuncia ad alta voce — nessuna istruzione di produzione
- Tra 2600 e 3000 parole
"""

    modelos = MODELOS_FULL
    texto   = _chamar_gemini(prompt, modelos, max_tokens=8192)
    texto   = re.sub(r'\*+', '', texto)
    texto   = re.sub(r'#{1,6}\s+', '', texto)
    texto   = re.sub(r'^\s*[-•]\s+', '', texto, flags=re.MULTILINE)
    texto   = re.sub(r'\.{2,}', '', texto)
    texto   = re.sub(r'\s*[—–]\s*', ', ', texto)
    texto   = re.sub(r'(?<!\n)\n(?!\n)', ' ', texto)
    texto   = re.sub(r'\n{3,}', '\n\n', texto)
    texto   = re.sub(r'  +', ' ', texto)
    return texto.strip()


# ═══════════════════════════════════════════════════════════════════════
# CONTROLLO QUALITÀ
# ═══════════════════════════════════════════════════════════════════════

def motivo_degeneracao(texto: str) -> str | None:
    palavras = texto.split()
    n = len(palavras)
    if n < 1400:
        return f"troppo corto ({n} parole)"
    if n > 4500:
        return f"troppo lungo ({n} parole — probabilmente un ciclo)"
    tri = {}
    for i in range(n - 2):
        t = (palavras[i].lower(), palavras[i + 1].lower(), palavras[i + 2].lower())
        tri[t] = tri.get(t, 0) + 1
    max_tri = max(tri.values()) if tri else 0
    if max_tri > 25:
        return f"trigramma ripetuto {max_tri}x (ciclo)"
    if texto.count(",") / max(n, 1) > 0.14:
        return "densità di virgole tipica di una lista di nomi"
    frases = {}
    for f in re.split(r"[.!?…]+", texto):
        f = f.strip().lower()
        if len(f.split()) > 5:
            frases[f] = frases.get(f, 0) + 1
    max_frase = max(frases.values()) if frases else 0
    if max_frase >= 4:
        return f"frase identica ripetuta {max_frase}x"
    return None


# ═══════════════════════════════════════════════════════════════════════
# TTS
# ═══════════════════════════════════════════════════════════════════════

async def _tts_async(texto: str, saida: Path):
    comm = edge_tts.Communicate(texto, voice=VOZ, rate=VOZ_RATE, pitch=VOZ_PITCH)
    await comm.save(str(saida))

def gerar_audio(texto: str, saida: Path):
    asyncio.run(_tts_async(texto, saida))
    print(f"  TTS IT: {saida.name} ({saida.stat().st_size // 1024} KB)")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def _gh_error(msg: str):
    linha = msg.replace("\n", " | ").replace("\r", "")[:500]
    print(f"::error::{linha}", flush=True)


def main():
    print("=" * 60)
    print("gerar_bloco_live_it.py — Canale IT — Madonna di Lourdes")
    print("=" * 60)

    DIR_BLOCOS.mkdir(parents=True, exist_ok=True)
    agora    = datetime.now(FUSO)
    contexto = calcular_contexto_sazonal(agora)
    pilar    = PILARES.get(agora.weekday(), "Preghiera e Intercessione")
    ts_base  = agora.strftime("%Y%m%d_%H%M")

    print(f"Ora locale: {agora.strftime('%Y-%m-%d %H:%M')} (Roma)")
    print(f"Contesto liturgico: {contexto}")
    print(f"Pilastro del giorno: {pilar}")

    print("\n[1/3] Recupero commenti del canale IT...")
    yt = get_youtube_readonly()
    comentarios = buscar_comentarios_canal(yt)

    print("\n[2/3] Classificazione in gruppi tematici...")
    grupos = classificar_grupos(comentarios, pilar)
    print(f"  Blocchi totali da generare: {len(grupos)}")

    print(f"\n[3/3] Generazione blocchi IT...")
    gerados = 0
    for i, grupo in enumerate(grupos):
        label = grupo.get("label", f"Gruppo {i+1}")
        print(f"\n  ── Blocco {i+1}/{len(grupos)}: {label} ──")
        try:
            num_bloco = int(agora.strftime("%j")) * MAX_GRUPOS + i + 1
            roteiro   = gerar_roteiro_grupo(grupo, contexto, pilar, agora, num_bloco)
            palavras  = len(roteiro.split())
            print(f"  Copione IT: {palavras} parole")

            motivo = motivo_degeneracao(roteiro)
            if motivo:
                print(f"  [WARN] Copione rifiutato ({motivo}) — nuovo tentativo con il modello completo...")
                roteiro  = gerar_roteiro_grupo(grupo, contexto, pilar, agora, num_bloco, so_full=True)
                palavras = len(roteiro.split())
                motivo   = motivo_degeneracao(roteiro)
                if motivo:
                    print(f"  [ERROR] Rifiutato di nuovo ({motivo}) — blocco scartato")
                    continue
                print(f"  Copione IT (completo): {palavras} parole — approvato")

            ts      = f"{ts_base}_{i+1:02d}"
            destino = DIR_BLOCOS / f"audio_{ts}.mp3"
            gerar_audio(roteiro, destino)
            gerados += 1
            print(f"  ✅ {destino.name}")

        except Exception as e:
            print(f"  [ERROR] Blocco {i+1} ({label}): {e}")
            continue

    print(f"\n{'='*60}")
    print(f"Completato IT: {gerados}/{len(grupos)} blocchi in {DIR_BLOCOS}/")
    print(f"VPS assembla i .mp4 con videos_base/ automaticamente.")

    if gerados == 0:
        _gh_error("Nessun blocco IT generato — tutti i gruppi hanno fallito.")
        sys.exit(1)


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception as exc:
        _gh_error(f"FALLIMENTO IT: {exc}")
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
