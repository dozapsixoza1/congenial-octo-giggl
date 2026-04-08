import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8204466219:AAFmb3IS1523JYJp6KH55Zi4sGJxs5UtVnQ")

# Game settings
MIN_PLAYERS = 4
MAX_PLAYERS = 20
JOIN_TIMEOUT = 90       # seconds to join
DAY_TIMEOUT = 120       # seconds for day discussion
VOTE_TIMEOUT = 60       # seconds for voting
NIGHT_TIMEOUT = 45      # seconds for night actions

DEFAULT_LANG = "ru"

# Economy rewards
REWARD_PARTICIPATION = 20
REWARD_WIN           = 50
REWARD_PER_KILL      = 10
REWARD_WIN_GEMS      = 1