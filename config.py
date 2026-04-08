import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8204466219:AAFmb3IS1523JYJp6KH55Zi4sGJxs5UtVnQ")

# Game settings
MIN_PLAYERS = 4
MAX_PLAYERS = 20
JOIN_TIMEOUT = 60       # seconds to join
DAY_TIMEOUT = 120       # seconds for day discussion
VOTE_TIMEOUT = 60       # seconds for voting
NIGHT_TIMEOUT = 40      # seconds for night actions
LAST_WILL_TIMEOUT = 30  # seconds to write last will

DEFAULT_LANG = "ru"
