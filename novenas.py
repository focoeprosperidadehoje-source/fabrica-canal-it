# -*- coding: utf-8 -*-
"""novenas.py — Slot 06:00 (Novenas) — gerado a partir do padrão do PT (aprovado por Leandro em 2026-09-25). Somente personas marianas do canal."""
import datetime

CFG = {
 "canal": "IT", "tz": "Europe/Rome", "lang_name": "Italian (italiano)",
 "ativacao": datetime.date(2026, 9, 30), "epoca_pedidos": datetime.date(2026, 9, 30),
 "status_pronto": "Ready for Audio", "invocacao_padrao": "Madonna di Lourdes",
 "promessa_regra": 'MUST start with "Madonna" or "La Madonna". Ex: "La Madonna Guarisce la Tua Casa", "La Madonna Apre le Porte".',
 "festas": [
   {"id": "lourdes", "inicio": (2, 2), "nome": "Novena alla Madonna di Lourdes", "invocacao": "Madonna di Lourdes",
    "festa": "Festa della Beata Vergine Maria di Lourdes (11 febbraio)"},
   {"id": "assunta", "inicio": (8, 6), "nome": "Novena dell'Assunta", "invocacao": "Vergine Maria Assunta in Cielo",
    "festa": "Solennità dell'Assunzione della Beata Vergine Maria (15 agosto)"},
   {"id": "immacolata", "inicio": (11, 29), "nome": "Novena all'Immacolata", "invocacao": "Maria Immacolata",
    "festa": "Solennità dell'Immacolata Concezione (8 dicembre)"},
   {"id": "natale", "inicio": (12, 16), "nome": "Novena di Natale con Maria", "invocacao": "Vergine Maria",
    "festa": "Natale (25 dicembre) — Maria, la Madre che attende il Bambino Gesù"},
 ],
 "intencoes_festa": ["la guarigione dalle malattie e la salute di chi ami", "l'unità e la restaurazione della tua famiglia",
   "la riconciliazione, il perdono e la pace", "la liberazione dalle dipendenze e da ogni catena", "la protezione e il futuro dei tuoi figli",
   "il lavoro, il sostentamento e le porte aperte", "la protezione spirituale della tua casa contro ogni male",
   "le cause impossibili e disperate", "la gratitudine per le grazie ricevute e la consacrazione a Maria"],
 "categorias": {
   "saude": ("Novena per la Guarigione e la Salute", "malattie, salute fisica, cure e interventi"),
   "familia": ("Novena per la Famiglia", "litigi, lontananza e restaurazione della famiglia e del matrimonio"),
   "emprego": ("Novena per Trovare Lavoro", "disoccupazione, lavoro, sostentamento e porte aperte"),
   "dividas": ("Novena per Uscire dai Debiti", "debiti, difficoltà economiche e provvidenza divina"),
   "filhos": ("Novena per i Figli", "protezione, cammino e conversione dei figli"),
   "vicios": ("Novena di Liberazione dalle Dipendenze", "dipendenze e catene delle persone che amiamo"),
   "ansiedade": ("Novena per Vincere l'Ansia", "ansia, angoscia, tristezza profonda e pace interiore"),
   "protecao": ("Novena di Protezione Spirituale", "protezione dal male, dall'invidia e dagli attacchi spirituali"),
   "causas": ("Novena per le Cause Impossibili", "cause impossibili, urgenti e disperate"),
   "luto": ("Novena di Consolazione nel Lutto", "lutto, nostalgia e consolazione per la perdita di una persona cara")},
 "meses": ["Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno","Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"],
 "completa": "(Completa)", "dia_label": "Giorno {n}", "thumb_fmt": "NOVENA GIORNO {n}",
 "data_no_titulo_festa": False, "data_fmt": "",
 "periodo": "questa mattina",
 "desc_link": "📿 Prega la novena completa, giorno per giorno: {url}",
 "cap_titulo": "⏱️ Capitoli della novena:",
 "cap": ["Apertura e intenzione del giorno", "Meditazione della Parola", "Preghiera della novena", "Supplica del giorno", "Padre Nostro, Ave Maria e Gloria", "Conclusione e benedizione"],
 "sinal_da_cruz": "Nel nome del Padre... e del Figlio... e dello Spirito Santo... Amen...",
 "ato_contricao": ("Preghiamo insieme l'atto di dolore... Mio Dio... mi pento e mi dolgo con tutto il cuore dei miei peccati... "
   "perché peccando ho meritato i tuoi castighi... e molto più perché ho offeso te, infinitamente buono e degno di essere amato sopra ogni cosa... "
   "Propongo con il tuo santo aiuto di non offenderti mai più... e di fuggire le occasioni prossime di peccato... Signore, misericordia, perdonami... Amen..."),
 "pai_nosso": ("Padre nostro, che sei nei cieli... sia santificato il tuo nome... venga il tuo regno... sia fatta la tua volontà, come in cielo così in terra... "
   "Dacci oggi il nostro pane quotidiano... e rimetti a noi i nostri debiti... come anche noi li rimettiamo ai nostri debitori... "
   "e non abbandonarci alla tentazione... ma liberaci dal male... Amen..."),
 "ave_maria": ("Ave, o Maria, piena di grazia... il Signore è con te... Tu sei benedetta fra le donne... "
   "e benedetto è il frutto del tuo seno Gesù... Santa Maria, Madre di Dio... prega per noi peccatori... adesso e nell'ora della nostra morte... Amen..."),
 "gloria": "Gloria al Padre... e al Figlio... e allo Spirito Santo... Come era nel principio, e ora e sempre, nei secoli dei secoli... Amen...",
 "oracoes_festa": {
   "lourdes": ("Preghiamo ora la preghiera di questa novena... O Madonna di Lourdes... che sei apparsa a Bernadette nella grotta di Massabielle... "
     "e hai detto: Io sono l'Immacolata Concezione... vieni oggi nella mia vita... Guarda i miei dolori... i bisogni della mia famiglia... "
     "e tutto ciò che non riesco a portare da solo... In questo giorno della tua novena ti affido la mia intenzione... "
     "Coprimi con il tuo manto... proteggi la mia casa... guarisci ciò che è ferito... e conducimi sempre più vicino a Gesù... Amen..."),
   "natale": ("Preghiamo ora la preghiera di questa novena... O Maria... Madre della speranza... "
     "tu che custodivi nel cuore il Bambino che stava per nascere... prepara anche il mio cuore ad accogliere Gesù in questo Natale... "
     "In questo giorno della novena ti affido la mia intenzione e la mia famiglia... che la luce di Betlemme entri nella nostra casa... e porti pace... guarigione... e unità... Amen...")},
 "oracao_festa_generica": ("Preghiamo ora la preghiera di questa novena... O {inv}... guarda il mio cuore stanco... "
   "Tu che hai detto sì al disegno di Dio... insegnami a fidarmi come tu ti sei fidata... "
   "In questo giorno della tua novena ti affido la mia intenzione... Purifica la mia vita... allontana da me ogni male... e presenta la mia preghiera a tuo Figlio Gesù... Amen..."),
 "oracao_pedido": ("Preghiamo ora la preghiera di questa novena... O Madonna di Lourdes... Madre di Dio e Madre nostra... "
   "in questa novena vengo ai tuoi piedi con una richiesta che pesa sul mio cuore... Tu conosci il mio dolore... prima ancora che io lo dica... "
   "In questo giorno della novena ti affido la mia intenzione... e ti chiedo di portarla a tuo Figlio Gesù... come hai portato il bisogno degli sposi a Cana... "
   "Sia fatta la volontà di Dio... e dammi la forza di attendere con fede... Amen..."),
 "jaculatoria": "{inv}... prega per noi...",
 "cta_pista": "invite them to write in the comments their intention or the name of the person they entrust to the Madonna, because these intentions are prayed in our 24-hour live stream",
}

# ─────────────────────── MOTOR (idêntico em todos os canais) ───────────────────────
import datetime

CANAL = CFG["canal"]
TZ = CFG["tz"]
ATIVACAO_06H = CFG["ativacao"]
EPOCA_PEDIDOS = CFG["epoca_pedidos"]
FESTAS = CFG["festas"]
INTENCOES_FESTA = CFG["intencoes_festa"]
CATEGORIAS = CFG["categorias"]
ROTACAO_FALLBACK = ["saude", "familia", "emprego", "ansiedade", "filhos", "protecao", "vicios", "dividas", "causas", "luto"]
JANELA_ANTI_REPETICAO = 3
MIN_COMENTARIOS_RANKING = 5
STATUS_PRONTO = CFG["status_pronto"]
LANG_NAME = CFG["lang_name"]
PROGRESSAO_PEDIDO = {
    1: "Day of SURRENDER: present the pain honestly and open the heart.",
    2: "Day of SURRENDER: admit what we cannot carry alone.",
    3: "Day of SURRENDER: forgive and let go of what weighs, to receive grace.",
    4: "Day of PERSEVERANCE: keep faith even when nothing seems to change.",
    5: "Day of PERSEVERANCE: the strength of Mary at the foot of the cross.",
    6: "Day of PERSEVERANCE: fight discouragement and the voice of fear.",
    7: "Day of TRUST: signs that grace is already on its way.",
    8: "Day of TRUST: give thanks in advance for what God will do.",
    9: "Day of GRATITUDE and CONSECRATION: entrust life and the cause to Our Lady.",
}
ABA_NOVENAS = "NOVENAS"
ABA_TEMAS = "TEMAS_COMENTARIOS"


def _festas_do_ano(ano):
    out = []
    for f in FESTAS:
        ini = datetime.date(ano, f["inicio"][0], f["inicio"][1])
        out.append((ini, ini + datetime.timedelta(days=8), ini + datetime.timedelta(days=9), f))
    return sorted(out, key=lambda x: x[0])


def _festa_em(d):
    for ano in (d.year - 1, d.year):
        for ini, fim, dia_festa, f in _festas_do_ano(ano):
            if ini <= d <= fim:
                return ("festa", f, (d - ini).days + 1, ini)
            if d == dia_festa:
                return ("dia_festa", f, None, ini)
    return None


def _proxima_festa_inicio(d):
    for ano in (d.year, d.year + 1):
        for ini, _, _, _ in _festas_do_ano(ano):
            if ini >= d:
                return ini
    return None


def plano_do_dia(d):
    if d < ATIVACAO_06H:
        return None
    fe = _festa_em(d)
    if fe:
        tipo, f, n, ini = fe
        if tipo == "festa":
            return {"tipo": "festa", "dia": n, "festa": f, "ciclo_inicio": ini}
        return {"tipo": "avulsa", "motivo": f"dia da festa ({f['id']})"}
    if d < EPOCA_PEDIDOS:
        return {"tipo": "avulsa", "motivo": "antes da época de pedidos"}
    cursor = EPOCA_PEDIDOS
    guard = 0
    while cursor <= d and guard < 2000:
        guard += 1
        fe_c = _festa_em(cursor)
        if fe_c:
            cursor = fe_c[3] + datetime.timedelta(days=10)
            continue
        prox = _proxima_festa_inicio(cursor)
        fim_ciclo = cursor + datetime.timedelta(days=8)
        if prox is None or fim_ciclo < prox:
            if cursor <= d <= fim_ciclo:
                return {"tipo": "pedido", "dia": (d - cursor).days + 1, "ciclo_inicio": cursor}
            cursor = fim_ciclo + datetime.timedelta(days=1)
        else:
            if cursor <= d < prox:
                return {"tipo": "avulsa", "motivo": "intervalo antes de novena de festa"}
            cursor = prox
    return {"tipo": "avulsa", "motivo": "fallback"}


def nome_mes(d):
    return f"{CFG['meses'][d.month - 1]} {d.year}"


def nome_playlist(plano, categoria=None):
    if plano["tipo"] == "festa":
        return f"{plano['festa']['nome']} {plano['ciclo_inicio'].year} {CFG['completa']}"
    if plano["tipo"] == "pedido":
        return f"{CATEGORIAS[categoria][0]} — {nome_mes(plano['ciclo_inicio'])}"
    return None


def montar_titulo(plano, promessa, categoria=None, data=None):
    """[Palavra-chave de busca] + [Dia N] + 🙏 + [Dor/Promessa]."""
    promessa = (promessa or "").strip().strip(".").strip()
    n = plano["dia"]
    dia_lbl = CFG["dia_label"].format(n=n)
    if plano["tipo"] == "festa":
        base = f"{plano['festa']['nome']} {dia_lbl} 🙏"
        if CFG.get("data_no_titulo_festa") and data is not None:
            base += " " + CFG["data_fmt"].format(d=data.day, m=CFG["meses"][data.month - 1])
            base += " |"
    else:
        base = f"{CATEGORIAS[categoria][0]} – {dia_lbl} 🙏"
    titulo = f"{base} {promessa}".strip()
    if len(titulo) > 100:
        titulo = base.rstrip(" |")
    return titulo


def texto_thumb(plano):
    return CFG["thumb_fmt"].format(n=plano["dia"])


def tema_codificado(plano, categoria=None):
    chave = plano["festa"]["id"] if plano["tipo"] == "festa" else categoria
    return f"NOVENA|{nome_playlist(plano, categoria)}|{plano['dia']}|{plano['tipo']}|{chave}"


def montar_roteiro(plano, gancho, reflexao, suplica, encerramento):
    if plano["tipo"] == "festa":
        f = plano["festa"]
        oracao = CFG["oracoes_festa"].get(f["id"], CFG["oracao_festa_generica"]).format(inv=f["invocacao"])
        jac = CFG["jaculatoria"].format(inv=f["invocacao"])
    else:
        oracao = CFG["oracao_pedido"]
        jac = CFG["jaculatoria"].format(inv=CFG["invocacao_padrao"])
    partes = [gancho.strip(), CFG["sinal_da_cruz"], CFG["ato_contricao"], reflexao.strip(), oracao,
              suplica.strip(), CFG["pai_nosso"], CFG["ave_maria"], CFG["gloria"], jac,
              encerramento.strip(), CFG["sinal_da_cruz"]]
    return "\n\n".join(p for p in partes if p)


def _aba(planilha, nome, cabecalho):
    try:
        return planilha.worksheet(nome)
    except Exception:
        ws = planilha.add_worksheet(title=nome, rows=1000, cols=len(cabecalho))
        ws.update(values=[cabecalho], range_name="A1")
        return ws


def escolher_tema_pedido(planilha, ciclo_inicio):
    ws_nov = _aba(planilha, ABA_NOVENAS, ["Canal", "Inicio", "Tipo", "Categoria", "Fonte", "Criado_em"])
    linhas = ws_nov.get_all_values()[1:]
    ciclo_str = str(ciclo_inicio)
    do_canal = [l for l in linhas if len(l) >= 4 and l[0] == CANAL and l[2] == "pedido"]
    for l in do_canal:
        if l[1] == ciclo_str and l[3] in CATEGORIAS:
            return l[3]
    usados = [l[3] for l in sorted(do_canal, key=lambda x: x[1]) if l[1] < ciclo_str][-JANELA_ANTI_REPETICAO:]
    escolha, fonte = None, "fallback"
    try:
        ws_t = _aba(planilha, ABA_TEMAS, ["Canal", "Data", "Categoria", "Contagem"])
        rows = [r for r in ws_t.get_all_values()[1:] if len(r) >= 4 and r[0] == CANAL]
        if rows:
            ultima = max(r[1] for r in rows)
            dt_ult = datetime.datetime.strptime(ultima, "%Y-%m-%d").date()
            if (ciclo_inicio - dt_ult).days <= 30:
                lote = []
                for r in rows:
                    if r[1] == ultima and r[2] in CATEGORIAS:
                        try: lote.append((r[2], int(r[3])))
                        except ValueError: pass
                if sum(c for _, c in lote) >= MIN_COMENTARIOS_RANKING:
                    for cat, cnt in sorted(lote, key=lambda x: -x[1]):
                        if cnt > 0 and cat not in usados:
                            escolha, fonte = cat, f"comentarios {ultima}"
                            break
    except Exception as e:
        print(f"[WARN] Ranking de comentários indisponível: {e}")
    if not escolha:
        idx = len(do_canal)
        for i in range(len(ROTACAO_FALLBACK)):
            cand = ROTACAO_FALLBACK[(idx + i) % len(ROTACAO_FALLBACK)]
            if cand not in usados:
                escolha = cand
                break
    ws_nov.append_row([CANAL, ciclo_str, "pedido", escolha, fonte,
                       datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")])
    print(f"📿 Novo ciclo de pedido {ciclo_str}: '{escolha}' ({fonte})")
    return escolha
