import os, sys, json, time, re, datetime
from google.genai import Client
from google.oauth2.service_account import Credentials
import gspread

CHAVE_API = os.environ.get("GEMINI_API_KEY")
GOOGLE_JSON = os.environ.get("GOOGLE_CREDENTIALS_IT")

print("🔐 Autenticazione Google Sheets (SHORTS IT)...")
credenciais_dict = json.loads(GOOGLE_JSON)
escopos = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credenciais = Credentials.from_service_account_info(credenciais_dict, scopes=escopos)
gc = gspread.authorize(credenciais)

client = Client(api_key=CHAVE_API, http_options={'api_version': 'v1'})

def obter_modelo_lite():
    try:
        modelos = client.models.list()
        lite_models = [m.name for m in modelos if 'generateContent' in m.supported_generation_methods and ('flash-lite' in m.name or '8b' in m.name)]
        return sorted(lite_models, reverse=True)[0] if lite_models else 'gemini-2.5-flash-lite'
    except:
        return 'gemini-2.5-flash-lite'

modelo_usina = obter_modelo_lite()

ID_PLANILHA = "1KgIjWrLUVlllhlZB1R9fkHGxxZlLsax1aOVGZrYwgnU"
PILARES = {
    0: "Guerra spirituale e protezione divina",
    1: "Liberazione dalle dipendenze e dai legami",
    2: "Restaurazione della famiglia e del matrimonio",
    3: "Provvidenza divina e porte aperte",
    4: "Misericordia divina e guarigione fisica",
    5: "Il manto della Madonna",
    6: "Miracoli e gratitudine"
}
GRADE_SHORTS = [
    {"horario": "06:00", "personagem": "Maria", "idioma": "IT",
     "foco": "Mattino: Sotto il manto della Madonna, inizia la tua giornata con un miracolo.", "ref": "18:00"},
    {"horario": "14:00", "personagem": "Maria", "idioma": "IT",
     "foco": "Pomeriggio: Intercessione, guarigione e miracoli.", "ref": "18:00"}
]

aba_shorts = gc.open_by_key(ID_PLANILHA).worksheet("IT_SHORTS")
aba_longos = gc.open_by_key(ID_PLANILHA).worksheet("IT")

todas_linhas = aba_shorts.get_all_values()
if len(todas_linhas) > 500:
    aba_shorts.delete_rows(2, 100)
    todas_linhas = aba_shorts.get_all_values()

proxima_linha_vazia = len(todas_linhas) + 1
valores_coluna_a = [linha[0].strip() for linha in todas_linhas[1:] if len(linha) > 0]
valores_coluna_b = [linha[1].strip() for linha in todas_linhas[1:] if len(linha) > 1]

dias_existentes = {}
hoje = datetime.date.today()
limite_passado = hoje - datetime.timedelta(days=2)

for d_str, h_str in zip(valores_coluna_a, valores_coluna_b):
    if d_str and h_str:
        try:
            d_obj = datetime.datetime.strptime(d_str, '%Y-%m-%d').date()
            if d_obj >= limite_passado:
                if d_obj not in dias_existentes: dias_existentes[d_obj] = []
                dias_existentes[d_obj].append(h_str)
        except: pass

meta_estoque = hoje + datetime.timedelta(days=5)

gaps = []
data_check = limite_passado
while data_check <= meta_estoque:
    horarios_presentes = dias_existentes.get(data_check, [])
    horarios_faltando = [v for v in GRADE_SHORTS if v["horario"] not in horarios_presentes]
    if horarios_faltando:
        gaps.append((data_check, horarios_faltando))
    data_check += datetime.timedelta(days=1)

if not gaps:
    print(f"✅ STOCK SHORTS RAGGIUNTO fino al {meta_estoque}. Uscita.")
    sys.exit(0)

dados_longos = aba_longos.get_all_values()

for data_alvo, grade_para_processar in gaps:
    pilar_do_dia = PILARES[data_alvo.weekday()]
    print(f"\n📅 DATA OBIETTIVO SHORTS: {data_alvo} | Pilastro: {pilar_do_dia}")
    for video in grade_para_processar:
        horario, persona, idioma, foco_teologico = video["horario"], video["personagem"].upper(), video["idioma"], video["foco"]
        print(f"🎬 PRODUZIONE SHORT: {horario} | {persona}")

        horario_longo_ref = video["ref"]
        titulo_referencia = ""
        for linha in dados_longos[1:]:
            if len(linha) > 6 and linha[0].strip() == str(data_alvo) and linha[1].strip() == horario_longo_ref:
                titulo_referencia = linha[6].strip()
                break

        contexto_eco = f"Il video lungo corrispondente di oggi ha il titolo: '{titulo_referencia}'. Lo Short DEVE essere un'eco di questo tema." if titulo_referencia else ""

        persona_prompt = "la Madonna di Lourdes, Nostra Signora"

        oracao_padrao = "Ave Maria, piena di grazia... il Signore è con te... tu sei benedetta fra le donne... e benedetto è il frutto del tuo seno, Gesù... Santa Maria, Madre di Dio... prega per noi peccatori... adesso e nell'ora della nostra morte... Amen."

        prompt_principal = f"""
        Agisci come una guida spirituale cattolica. Crea uno script per un video YouTube SHORT (massimo 35 secondi di parlato).
        Tema del giorno: {pilar_do_dia}. Focus: {foco_teologico}. Rivolto a: {persona_prompt}.
        {contexto_eco}

        STRUTTURA OBBLIGATORIA DELLO SCRIPT (LOOP PERFETTO):
        1. HOOK (Inizio): La prima frase del video. OBBLIGATORIO iniziare con puntini di sospensione in minuscolo ("..."). È il COMPLEMENTO SINTATTICO della frase finale — insieme formano una frase unica, continua e completa.
        2. PREGHIERA: Scrivi ESATTAMENTE questa preghiera: "{oracao_padrao}"
        3. FRASE DEL LOOP (Fine): L'ultima frase del video. OBBLIGATORIO terminare con puntini di sospensione ("..."). Deve essere SINTATTICAMENTE INCOMPLETA — una proposizione aperta il cui complemento naturale è esattamente la frase di apertura.

        REGOLE DI FLUIDITÀ:
        - Scrivi frasi fluide e naturali. Usa i puntini di sospensione (...) per le pause respiratorie.
        - Il titolo deve iniziare con "Preghiera rapida: " seguito dal tema, e terminare con l'hashtag #Shorts.
        - NESSUN marcatore temporale, NESSUN asterisco, NESSUNA emoji nello script.

        FORMATO ESATTO:
        TITOLO: [Preghiera rapida: Tema - #Shorts]
        SCRIPT: [Script completo con l'effetto loop]
        DESC: [Breve descrizione che invita gli spettatori a visitare il canale e le playlist]
        TAGS: [Tag separati da virgole]
        """

        texto_ia = None
        for tentativa in range(3):
            try:
                texto_ia = client.models.generate_content(model=modelo_usina, contents=prompt_principal).text
                break
            except Exception as gemini_err: print(f"   ⚠️ Errore Gemini (tentativo {tentativa+1}/3): {gemini_err}"); time.sleep(10)

        if not texto_ia: continue

        try:
            t_match = re.search(r'TITOLO:\s*(.*?)(?=SCRIPT:|DESC:|TAGS:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
            g_match = re.search(r'SCRIPT:\s*(.*?)(?=DESC:|TAGS:|TITOLO:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
            d_match = re.search(r'DESC:\s*(.*?)(?=TAGS:|TITOLO:|SCRIPT:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
            tg_match = re.search(r'TAGS:\s*(.*?)(?=TITOLO:|SCRIPT:|DESC:|$)', texto_ia, re.IGNORECASE | re.DOTALL)

            titulo_final = re.sub(r'[*"\[\]]', '', t_match.group(1)).strip() if t_match else "Preghiera rapida #Shorts"
            roteiro_final = g_match.group(1).strip() if g_match else texto_ia
            desc_final = d_match.group(1).strip() if d_match else "Guarda la preghiera completa sul nostro canale!"
            tags_final = re.sub(r'[*\[\]]', '', tg_match.group(1)).strip() if tg_match else "shorts, preghiera, fede"

            nova_linha = [str(data_alvo), horario, "Ready for Audio", persona, idioma, pilar_do_dia, titulo_final, roteiro_final, tags_final, desc_final, "N/A", "N/A"]
            aba_shorts.update(values=[nova_linha], range_name=f"A{proxima_linha_vazia}:L{proxima_linha_vazia}")
            print(f"   ✅ SUCCESSO! Riga Short {proxima_linha_vazia} riempita.")
            proxima_linha_vazia += 1
            time.sleep(3)
        except Exception as e: print(f"   ❌ Errore nel salvataggio: {e}")
