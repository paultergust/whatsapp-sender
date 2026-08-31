from pathlib import Path

MESSAGE = """
Boa tarde! Tudo bem? 

Sou o Paulo da Unidade Popular. 
Estou chamando todos os nossos contatos para participar da *Plenária Regional de lançamento da nossa candidata ao senado e organização da nossa campanha* 
E também para a marcha de divulgação do socialismo, que vai acontecer amanhã na Ocupação Menino Ryan Vive.

1️⃣ *Plenária Regional!*
📣_Organização da Campanha + Marcha do Socialismo!_

📆 SÁBADO (08)
🕐 14h
📍Ocupação Menino Ryan - Rua João Pessoa, 497. Centro, Santos - SP.
""".strip()

CONTACTS_FILE = Path("contacts.txt")

USER_DATA_DIR = "whatsapp_profile"

ERROR_DIR = Path("errors")

SENT_LOG = Path("sent.log")
FAILED_LOG = Path("failed.log")

MIN_DELAY = 8
MAX_DELAY = 20

BREAK_EVERY_MIN = 8
BREAK_EVERY_MAX = 12

LONG_BREAK_MIN = 60
LONG_BREAK_MAX = 180

RETRY_DELAY = 20
