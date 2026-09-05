import os, sys, json, time, re, datetime
from google.genai import Client
from google.oauth2.service_account import Credentials
import gspread

CHAVE_API = os.environ.get("GEMINI_API_KEY")
CHAVE_API_2 = os.environ.get("GEMINI_API_KEY_2", "")
CHAVES_GEMINI = [k for k in [CHAVE_API, CHAVE_API_2] if k]
GOOGLE_JSON = os.environ.get("GOOGLE_CREDENTIALS_IT")

print("🔐 Autenticazione Google Sheets (Service Account IT)...")
credenciais_dict = json.loads(GOOGLE_JSON)
escopos = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credenciais = Credentials.from_service_account_info(credenciais_dict, scopes=escopos)
gc = gspread.authorize(credenciais)

client = Client(api_key=CHAVE_API, http_options={'api_version': 'v1'})

def obter_cascata_de_modelos():
    try:
        modelos_disponiveis = client.models.list()
        lite_models = [m.name for m in modelos_disponiveis if 'generateContent' in m.supported_generation_methods and 'flash' in m.name and ('lite' in m.name or '8b' in m.name)]
        flash_models = [m.name for m in modelos_disponiveis if 'generateContent' in m.supported_generation_methods and 'flash' in m.name and 'lite' not in m.name and '8b' not in m.name]
        melhor_lite = sorted(lite_models, reverse=True)[0] if lite_models else 'gemini-3.5-flash-lite'
        melhor_flash = sorted(flash_models, reverse=True)[0] if flash_models else 'gemini-2.5-flash'
        return [melhor_lite, melhor_lite, melhor_lite, melhor_lite, melhor_flash]
    except:
        return ['gemini-3.5-flash-lite', 'gemini-3.5-flash-lite', 'gemini-3.5-flash-lite', 'gemini-3.5-flash-lite', 'gemini-2.5-flash']

modelos_cascata = obter_cascata_de_modelos()

def _gerar(modelo, prompt):
    for chave in CHAVES_GEMINI:
        try:
            c = Client(api_key=chave, http_options={'api_version': 'v1'})
            return c.models.generate_content(model=modelo, contents=prompt).text
        except Exception as e:
            if "429" in str(e) and chave != CHAVES_GEMINI[-1]:
                print(f"[WARN] 429 sulla chiave ...{chave[-6:]}. Tentativo con chiave 2...")
                continue
            raise
    raise RuntimeError("Tutte le chiavi Gemini hanno fallito.")

def calcular_contexto_sazonal(data_alvo):
    ano = data_alvo.year
    a = ano % 19; b = ano // 100; c = ano % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; mes = (h + l - 7 * m + 114) // 31; dia = ((h + l - 7 * m + 114) % 31) + 1
    easter = datetime.date(ano, mes, dia)

    ash_wednesday = easter - datetime.timedelta(days=46)
    good_friday = easter - datetime.timedelta(days=2)
    pentecost = easter + datetime.timedelta(days=49)
    corpus_christi = easter + datetime.timedelta(days=60)

    may_1 = datetime.date(ano, 5, 1)
    mothers_day = may_1 + datetime.timedelta(days=(6 - may_1.weekday() + 7) % 7 + 7)

    if data_alvo == easter: return "OGGI È LA DOMENICA DI PASQUA."
    if data_alvo == ash_wednesday: return "OGGI È IL MERCOLEDÌ DELLE CENERI."
    if data_alvo == good_friday: return "OGGI È IL VENERDÌ SANTO."
    if data_alvo == pentecost: return "OGGI È LA DOMENICA DI PENTECOSTE."
    if data_alvo == corpus_christi: return "OGGI È LA FESTA DEL CORPUS DOMINI."
    if data_alvo == mothers_day: return "OGGI È LA FESTA DELLA MAMMA."
    if data_alvo.month == 8 and data_alvo.day == 15: return "OGGI È LA FESTA DELL'ASSUNZIONE DI MARIA."
    if data_alvo.month == 11 and data_alvo.day == 1: return "OGGI È OGNISSANTI."
    if data_alvo.month == 11 and data_alvo.day == 2: return "OGGI È LA COMMEMORAZIONE DEI FEDELI DEFUNTI."
    if data_alvo.month == 12 and data_alvo.day == 8: return "OGGI È LA FESTA DELL'IMMACOLATA CONCEZIONE."
    if data_alvo.month == 12 and data_alvo.day == 25: return "OGGI È NATALE."
    if data_alvo.month == 12 and data_alvo.day == 31: return "OGGI È IL CAPODANNO."
    if data_alvo.month == 1 and data_alvo.day == 1: return "OGGI È IL PRIMO DELL'ANNO."
    return ""

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
GRADE_DIARIA = [
    {"horario": "18:00", "personagem": "Maria", "idioma": "IT",
     "foco": "Sera: Preghiera mariana di protezione, guarigione, liberazione e riposo notturno.",
     "periodo": "questa sera"}
]

aba = gc.open_by_key(ID_PLANILHA).worksheet("IT")

todas_linhas = aba.get_all_values()
if len(todas_linhas) > 500:
    aba.delete_rows(2, 100)
    todas_linhas = aba.get_all_values()

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
data_alvo = None
grade_para_processar = []

data_check = limite_passado
while data_check <= meta_estoque:
    horarios_presentes = dias_existentes.get(data_check, [])
    if len(horarios_presentes) < len(GRADE_DIARIA):
        data_alvo = data_check
        grade_para_processar = [v for v in GRADE_DIARIA if v["horario"] not in horarios_presentes]
        break
    data_check += datetime.timedelta(days=1)

if not data_alvo:
    print(f"✅ STOCK RAGGIUNTO fino al {meta_estoque}. Uscita.")
    sys.exit(0)

pilar_do_dia = PILARES[data_alvo.weekday()]
contexto_sazonal = calcular_contexto_sazonal(data_alvo)
print(f"\n📅 DATA OBIETTIVO: {data_alvo} | Pilastro: {pilar_do_dia}")

esperas_exponenciais = [10, 20, 40, 80, 120]

for video in grade_para_processar:
    horario, persona, idioma, foco_teologico, periodo = video["horario"], video["personagem"].upper(), video["idioma"], video["foco"], video["periodo"]
    print(f"🎬 PRODUZIONE: {horario} | {persona}")

    persona_prompt = "la Madonna di Lourdes, Nostra Signora"

    prompt_tema = f"Agisci come Teologo. Crea un tema breve (max 8 parole) per una preghiera. Pilastro: '{pilar_do_dia}', rivolto a '{persona_prompt}', momento: '{foco_teologico}'. Stagionalità: '{contexto_sazonal}'. SOLO il tema, senza virgolette né asterischi."
    tema_gerado = None
    for i in range(5):
        try:
            tema_gerado = _gerar(modelos_cascata[i], prompt_tema).replace('*', '').replace('"', '').replace('[', '').replace(']', '').strip()
            break
        except Exception as gemini_err: print(f"   ⚠️ Errore Gemini (tentativo {i+1}/5): {gemini_err}"); time.sleep(esperas_exponenciais[i])

    if not tema_gerado: continue
    time.sleep(5)

    regra_meditacao = "OBBLIGATORIO: Nella descrizione (DESC), aggiungi un avviso che alla fine del video ci sono 5 minuti di musica celestiale per dormire/meditare."
    cta_comentarios = "Alla fine, chiedi all'ascoltatore di scrivere un motivo di gratitudine nei commenti."

    instrucao_titulo = "TITOLO:[Titolo magnetico. OBBLIGATORIO iniziare con 'Madonna' o 'Nostra Signora'. FORMATO: 'Madonna [dolore del credente] [promessa urgente]'. Es: 'Madonna guarisce la tua famiglia stasera'. NESSUNA DATA. NESSUN ASTERISCO O PARENTESI]"

    prompt_principal = f"""
    Agisci come una guida spirituale empatica e sorella nella fede. Scrivi una preghiera estesa di 1500-1800 parole su "{tema_gerado}" rivolta a {persona_prompt}.
    CONTESTO: Momento della giornata: "{periodo}". Focus: "{foco_teologico}". Stagionalità: "{contexto_sazonal}".

    REGOLE DI RITENZIONE E COPYWRITING (MOLTO IMPORTANTI):
    1. FORMULA DEL TITOLO: Segui ESATTAMENTE il formato indicato. Per la Madonna: OBBLIGATORIO iniziare con 'Madonna' o 'Nostra Signora'. È STRETTAMENTE VIETATO iniziare con la parola 'Preghiera'.
    2. FORMULA THUMB: Massimo 4 parole. DEVE essere un trigger di urgenza connesso al tema (Es: "MIRACOLO URGENTE OGGI", "SALVA LA TUA FAMIGLIA", "FINE DELL'ANSIA").
    3. LA REGOLA DEI 15 SECONDI (HOOK 3A): L'inizio dello script DEVE avere 3 blocchi rapidi:
       - Attenzione (0-5s): Un'AFFERMAZIONE EMPATICA sul dolore del credente. (VIETATO usare domande dirette).
       - Ambientazione sensoriale (5-10s): Connetti il dolore con la scena di {periodo}.
       - Autorità/Agenda (10-15s): Di' che {persona_prompt} ha una parola di liberazione e chiedi di restare fino alla fine.
    4. CTA IMMEDIATO: {cta_comentarios}
    5. RESET DELL'ATTENZIONE (A METÀ VIDEO): Esattamente a metà dello script, inserisci una frase parlata per riconnettere l'ascoltatore.
    6. GANCI DI RITENZIONE INVISIBILI: Ogni 300-400 parole, incorpora organicamente uno di questi: (a) ANTICIPAZIONE; (b) RIVELAZIONE PARZIALE; (c) VALIDAZIONE EMOTIVA; (d) CAMBIO DI BLOCCO.

    REGOLE GENERALI:
    7. VIETATO MENZIONARE ORE ESATTE: Usa solo "{periodo}".
    8. PAUSE: OBBLIGATORIO usare abbondanti puntini di sospensione (...) per forzare pause nella voce IA.
    9. ANTI-JSON: Scrivi in TESTO SEMPLICE. VIETATO JSON, parentesi graffe {{ }} o asterischi (*).
    OBBLIGATORIO: Poiché ti stai rivolgendo alla Madonna, DEVI usare le invocazioni 'Madonna di Lourdes', 'Vergine Maria' o 'Nostra Signora'.
    {regra_meditacao}

    FORMATO ESATTO:
    {instrucao_titulo}
    THUMB: [Trigger di urgenza — Max 4 parole]
    SCRIPT: [Preghiera completa di 1500-1800 parole]
    DESC: [Descrizione di 3 paragrafi con forte SEO. PRIMO paragrafo: invita alla LIVE 24h del canale ('Presto: prega in diretta 24h/24 con noi — attiva la campana per non perdere nessuna preghiera'). SECONDO paragrafo: descrizione emotiva di questa preghiera. TERZO paragrafo: parole chiave e hashtag.]
    TAGS: [Tag separati da virgole]
    """

    texto_ia = None
    for i in range(5):
        try:
            texto_ia = _gerar(modelos_cascata[i], prompt_principal)
            break
        except Exception as gemini_err: print(f"   ⚠️ Errore Gemini (tentativo {i+1}/5): {gemini_err}"); time.sleep(esperas_exponenciais[i])

    if not texto_ia: continue

    try:
        t_match = re.search(r'TITOLO:\s*(.*?)(?=THUMB:|SCRIPT:|DESC:|TAGS:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        th_match = re.search(r'THUMB:\s*(.*?)(?=SCRIPT:|DESC:|TAGS:|TITOLO:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        g_match = re.search(r'SCRIPT:\s*(.*?)(?=DESC:|TAGS:|TITOLO:|THUMB:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        d_match = re.search(r'DESC:\s*(.*?)(?=TAGS:|TITOLO:|THUMB:|SCRIPT:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        tg_match = re.search(r'TAGS:\s*(.*?)(?=TITOLO:|THUMB:|SCRIPT:|DESC:|$)', texto_ia, re.IGNORECASE | re.DOTALL)

        titulo_final = re.sub(r'[*"\[\]]', '', t_match.group(1)).strip() if t_match else "Preghiera potente"
        thumb_final = re.sub(r'[*"\[\]]', '', th_match.group(1)).strip() if th_match else "MIRACOLO OGGI"
        roteiro_final = g_match.group(1).strip() if g_match else texto_ia
        desc_final = d_match.group(1).strip() if d_match else "Preghiera quotidiana."
        tags_final = re.sub(r'[*\[\]]', '', tg_match.group(1)).strip() if tg_match else "preghiera, fede, protezione"

        nova_linha = [str(data_alvo), horario, "Ready for Audio", persona, idioma, tema_gerado, titulo_final, roteiro_final, tags_final, desc_final, "Pending", thumb_final]
        aba.update(values=[nova_linha], range_name=f"A{proxima_linha_vazia}:L{proxima_linha_vazia}")
        print(f"   ✅ SUCCESSO! Riga {proxima_linha_vazia} riempita.")
        proxima_linha_vazia += 1
        time.sleep(5)
    except Exception as e: print(f"   ❌ Errore nel salvataggio: {e}")
