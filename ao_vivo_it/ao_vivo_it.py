# TODO: Script principal da live 24h para o canal IT.
# Implementar quando SSH_KEY_VPS_IT e STREAM_KEY_H_IT estiverem configurados.
# Baseado em: fabrica-canal-en/ao_vivo_en/ao_vivo_en.py
# Adaptar:
#   CANAL_ID = "UCa1_Xd4tOUd6GSPNu7auY4A"
#   PLAYLIST_LIVES = "PLACEHOLDER_LIVE_IT"  <- atualizar após criar playlist
#   FUSO = pytz.timezone("Europe/Rome")
#   STREAM_KEY_H = os.environ.get("STREAM_KEY_H_IT", "")
#   BASE_DIR = Path("/root/ao_vivo_it")
#   VOZ = "it-IT-ElsaNeural"
#   CHAVES_CONTEUDO: GEMINI_KEY_LIVE_CONTENT_1_IT, GEMINI_KEY_LIVE_CONTENT_2_IT
#   CHAVES_CHAT: GEMINI_KEY_LIVE_CHAT_1_IT, _2_IT, _3_IT
#   Timer offset: ciclo_start - 1800 (IT dispara 30min antes do EN para não colidir no VPS2)
#   Persona: Madonna di Lourdes, Nostra Signora
#   TITULOS_LIVE e DESCRICAO_LIVE em italiano
print("ao_vivo_it.py: aguardando SSH key e stream key para implementação completa.")
