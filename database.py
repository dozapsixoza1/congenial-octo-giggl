"""
SQLite database layer.
Stores: player profiles, economy, stats, shop items, game history.
"""
import sqlite3
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "harshmafia.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS players (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            name        TEXT,
            gender      TEXT DEFAULT '',
            lang        TEXT DEFAULT 'ru',
            money       INTEGER DEFAULT 10,
            gems        INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            games_won   INTEGER DEFAULT 0,
            kills       INTEGER DEFAULT 0,
            best_role   TEXT DEFAULT '',
            -- shop items
            shield      INTEGER DEFAULT 0,
            documents   INTEGER DEFAULT 0,
            active_role INTEGER DEFAULT 0,
            -- cosmetics
            title       TEXT DEFAULT '',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS game_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id     INTEGER,
            winner      TEXT,
            players     TEXT,
            roles       TEXT,
            played_at   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS shop_items (
            item_id     TEXT PRIMARY KEY,
            name_ru     TEXT,
            name_en     TEXT,
            desc_ru     TEXT,
            desc_en     TEXT,
            price_money INTEGER DEFAULT 0,
            price_gems  INTEGER DEFAULT 0,
            category    TEXT DEFAULT 'item'
        );
        """)

        # Seed shop items if empty
        cur = conn.execute("SELECT COUNT(*) FROM shop_items")
        if cur.fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO shop_items VALUES (?,?,?,?,?,?,?,?)",
                [
                    ("shield",      "Защита",        "Shield",
                     "Один раз спасёт тебе жизнь ночью",
                     "Saves your life once at night",
                     100, 0, "item"),
                    ("documents",   "Документы",     "Documents",
                     "Фальшивые документы — детектив увидит тебя как мирного",
                     "Fake docs — detective sees you as innocent",
                     150, 0, "item"),
                    ("active_role", "Активная роль", "Active Role",
                     "99% шанс получить активную роль в следующей игре",
                     "99% chance to get an active role next game",
                     0, 1, "item"),
                    ("title_don",   "Титул: Дон",    "Title: Don",
                     "Отображается рядом с именем в профиле",
                     "Displayed next to your name in profile",
                     500, 0, "title"),
                    ("title_sheriff","Титул: Шериф", "Title: Sheriff",
                     "Отображается рядом с именем в профиле",
                     "Displayed next to your name in profile",
                     500, 0, "title"),
                    ("title_vip",   "Титул: VIP",    "Title: VIP",
                     "Особый титул для лучших игроков",
                     "Special title for top players",
                     0, 5, "title"),
                ]
            )


# ── Player CRUD ────────────────────────────────────────────
def ensure_player(user_id: int, name: str, username: str = ""):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO players (user_id, name, username) VALUES (?,?,?)",
            (user_id, name, username or "")
        )
        conn.execute(
            "UPDATE players SET name=?, username=? WHERE user_id=?",
            (name, username or "", user_id)
        )


def get_player(user_id: int) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM players WHERE user_id=?", (user_id,)).fetchone()


def update_player(user_id: int, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE players SET {sets} WHERE user_id=?", vals)


def add_money(user_id: int, amount: int):
    with get_conn() as conn:
        conn.execute("UPDATE players SET money = MAX(0, money+?) WHERE user_id=?", (amount, user_id))


def add_gems(user_id: int, amount: int):
    with get_conn() as conn:
        conn.execute("UPDATE players SET gems = MAX(0, gems+?) WHERE user_id=?", (amount, user_id))


def spend_money(user_id: int, amount: int) -> bool:
    p = get_player(user_id)
    if not p or p["money"] < amount:
        return False
    with get_conn() as conn:
        conn.execute("UPDATE players SET money=money-? WHERE user_id=?", (amount, user_id))
    return True


def spend_gems(user_id: int, amount: int) -> bool:
    p = get_player(user_id)
    if not p or p["gems"] < amount:
        return False
    with get_conn() as conn:
        conn.execute("UPDATE players SET gems=gems-? WHERE user_id=?", (amount, user_id))
    return True


def record_game_result(chat_id: int, winner: str, player_results: list):
    """
    player_results: list of dicts {user_id, name, role, won, killed}
    Awards money/gems after game ends.
    """
    with get_conn() as conn:
        for r in player_results:
            uid = r["user_id"]
            won = r.get("won", False)
            killed = r.get("killed", 0)

            earn_money = 20 + (50 if won else 0) + (killed * 10)
            earn_gems = 1 if won else 0

            conn.execute("""
                UPDATE players SET
                    games_played = games_played + 1,
                    games_won    = games_won + ?,
                    kills        = kills + ?,
                    money        = money + ?,
                    gems         = gems + ?
                WHERE user_id = ?
            """, (1 if won else 0, killed, earn_money, earn_gems, uid))

        conn.execute(
            "INSERT INTO game_log (chat_id, winner) VALUES (?,?)",
            (chat_id, winner)
        )


def get_top(limit: int = 10) -> list:
    with get_conn() as conn:
        return conn.execute("""
            SELECT name, games_played, games_won, kills, money, gems, title
            FROM players ORDER BY games_won DESC, kills DESC LIMIT ?
        """, (limit,)).fetchall()


def get_shop_items() -> list:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM shop_items ORDER BY category, price_money").fetchall()


def buy_item(user_id: int, item_id: str) -> tuple[bool, str]:
    """Returns (success, error_key)"""
    with get_conn() as conn:
        item = conn.execute("SELECT * FROM shop_items WHERE item_id=?", (item_id,)).fetchone()
        if not item:
            return False, "item_not_found"

        p = get_player(user_id)
        if not p:
            return False, "no_profile"

        if item["price_money"] > 0:
            if p["money"] < item["price_money"]:
                return False, "not_enough_money"
            conn.execute("UPDATE players SET money=money-? WHERE user_id=?",
                         (item["price_money"], user_id))
        elif item["price_gems"] > 0:
            if p["gems"] < item["price_gems"]:
                return False, "not_enough_gems"
            conn.execute("UPDATE players SET gems=gems-? WHERE user_id=?",
                         (item["price_gems"], user_id))

        # Apply item
        if item["category"] == "item":
            col = item_id  # shield / documents / active_role
            conn.execute(f"UPDATE players SET {col}={col}+1 WHERE user_id=?", (user_id,))
        elif item["category"] == "title":
            title_name = item_id.replace("title_", "").upper()
            conn.execute("UPDATE players SET title=? WHERE user_id=?", (title_name, user_id))

    return True, ""