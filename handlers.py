import asyncio
from aiogram import Dispatcher, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import MIN_PLAYERS, MAX_PLAYERS, JOIN_TIMEOUT
from game_state import GameState, GamePhase, games, user_langs, Player
from roles import RoleID, Faction
from localization import t
from keyboards import reg_keyboard, lang_keyboard
from game_flow import start_game, role_name


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def get_lang(user_id: int, game: GameState = None) -> str:
    if game:
        return game.lang
    return user_langs.get(user_id, "ru")


def player_name(msg: Message) -> str:
    fn = msg.from_user.first_name or ""
    ln = msg.from_user.last_name or ""
    return (fn + " " + ln).strip() or msg.from_user.username or "Player"


# ──────────────────────────────────────────────
# /start — PM welcome
# ──────────────────────────────────────────────
async def cmd_start(msg: Message):
    if msg.chat.type == "private":
        lang = get_lang(msg.from_user.id)
        await msg.answer(
            "🤵 <b>HarshMafia Bot</b>\n\n"
            "Добавь меня в групповой чат и используй /game чтобы начать!\n"
            "Add me to a group chat and use /game to start!\n\n"
            "/lang — выбор языка / language",
            reply_markup=lang_keyboard()
        )


# ──────────────────────────────────────────────
# /lang — language selection
# ──────────────────────────────────────────────
async def cmd_lang(msg: Message):
    await msg.answer(t(get_lang(msg.from_user.id), "choose_lang"), reply_markup=lang_keyboard())


async def cb_lang(cq: CallbackQuery):
    lang = cq.data.split("_")[1]
    user_langs[cq.from_user.id] = lang
    game = games.get(cq.message.chat.id)
    if game:
        game.lang = lang
    await cq.answer(t(lang, "lang_set"))
    await cq.message.delete()


# ──────────────────────────────────────────────
# /game — create lobby
# ──────────────────────────────────────────────
async def cmd_game(msg: Message):
    if msg.chat.type == "private":
        await msg.answer(t(get_lang(msg.from_user.id), "only_group"))
        return

    chat_id = msg.chat.id
    if chat_id in games:
        lang = games[chat_id].lang
        await msg.answer(t(lang, "game_exists"))
        return

    lang = get_lang(msg.from_user.id)
    game = GameState(chat_id=chat_id, creator_id=msg.from_user.id, lang=lang)
    games[chat_id] = game

    first_player = Player(
        user_id=msg.from_user.id,
        name=player_name(msg),
        username=msg.from_user.username
    )
    game.players[msg.from_user.id] = first_player

    reg_msg = await msg.answer(
        t(lang, "game_created", count=1, max=MAX_PLAYERS, time=JOIN_TIMEOUT),
        reply_markup=reg_keyboard(lang, 1, MAX_PLAYERS)
    )
    game.reg_message_id = reg_msg.message_id

    # Auto-close registration after timeout
    async def close_reg():
        await asyncio.sleep(JOIN_TIMEOUT)
        g = games.get(chat_id)
        if g and g.phase == GamePhase.REGISTRATION:
            if len(g.players) < MIN_PLAYERS:
                await msg.bot.send_message(chat_id, t(g.lang, "not_enough", min=MIN_PLAYERS))
                del games[chat_id]

    asyncio.create_task(close_reg())


# ──────────────────────────────────────────────
# JOIN callback
# ──────────────────────────────────────────────
async def cb_join(cq: CallbackQuery):
    chat_id = cq.message.chat.id
    game = games.get(chat_id)
    lang = get_lang(cq.from_user.id)

    if not game or game.phase != GamePhase.REGISTRATION:
        await cq.answer(t(lang, "no_game"))
        return
    if cq.from_user.id in game.players:
        await cq.answer(t(game.lang, "already_joined"))
        return
    if len(game.players) >= MAX_PLAYERS:
        await cq.answer(t(game.lang, "game_full", max=MAX_PLAYERS))
        return

    fn = cq.from_user.first_name or ""
    ln = cq.from_user.last_name or ""
    name = (fn + " " + ln).strip() or cq.from_user.username or "Player"

    game.players[cq.from_user.id] = Player(
        user_id=cq.from_user.id,
        name=name,
        username=cq.from_user.username
    )

    count = len(game.players)
    await cq.answer(t(game.lang, "joined", name=name, count=count, max=MAX_PLAYERS))

    try:
        await cq.message.edit_text(
            t(game.lang, "game_created", count=count, max=MAX_PLAYERS, time=JOIN_TIMEOUT),
            reply_markup=reg_keyboard(game.lang, count, MAX_PLAYERS)
        )
    except Exception:
        pass


# ──────────────────────────────────────────────
# LEAVE callback
# ──────────────────────────────────────────────
async def cb_leave(cq: CallbackQuery):
    chat_id = cq.message.chat.id
    game = games.get(chat_id)
    lang = get_lang(cq.from_user.id)

    if not game or game.phase != GamePhase.REGISTRATION:
        await cq.answer(t(lang, "no_game"))
        return
    if cq.from_user.id not in game.players:
        await cq.answer(t(game.lang, "not_in_game"))
        return

    name = game.players[cq.from_user.id].name
    del game.players[cq.from_user.id]
    count = len(game.players)

    await cq.answer(t(game.lang, "left_game", name=name, count=count, max=MAX_PLAYERS))
    try:
        await cq.message.edit_text(
            t(game.lang, "game_created", count=count, max=MAX_PLAYERS, time=JOIN_TIMEOUT),
            reply_markup=reg_keyboard(game.lang, count, MAX_PLAYERS)
        )
    except Exception:
        pass


# ──────────────────────────────────────────────
# START GAME callback
# ──────────────────────────────────────────────
async def cb_startgame(cq: CallbackQuery):
    chat_id = cq.message.chat.id
    game = games.get(chat_id)
    lang = get_lang(cq.from_user.id)

    if not game:
        await cq.answer(t(lang, "no_game"))
        return
    if cq.from_user.id != game.creator_id:
        await cq.answer(t(game.lang, "not_creator"))
        return
    if len(game.players) < MIN_PLAYERS:
        await cq.answer(t(game.lang, "not_enough", min=MIN_PLAYERS))
        return

    await cq.answer()
    await cq.message.edit_reply_markup(reply_markup=None)
    asyncio.create_task(start_game(cq.bot, game))


# ──────────────────────────────────────────────
# VOTE callback (day lynching)
# ──────────────────────────────────────────────
async def cb_vote(cq: CallbackQuery):
    chat_id = cq.message.chat.id
    game = games.get(chat_id)
    lang = get_lang(cq.from_user.id)

    if not game or game.phase != GamePhase.VOTING:
        await cq.answer(t(lang, "no_game"))
        return

    voter = game.players.get(cq.from_user.id)
    if not voter:
        await cq.answer(t(game.lang, "not_in_game"))
        return
    if not voter.is_alive:
        await cq.answer(t(game.lang, "you_are_dead"))
        return
    if voter.has_voted:
        await cq.answer(t(game.lang, "already_voted"))
        return

    voter.has_voted = True
    data = cq.data  # vote_{uid} or vote_skip

    if data == "vote_skip":
        voter.night_target = -999
        await cq.answer(t(game.lang, "vote_skip", voter=voter.name))
    else:
        target_uid = int(data.split("_")[1])
        target = game.players.get(target_uid)
        if not target or not target.is_alive:
            await cq.answer(t(game.lang, "target_dead"))
            voter.has_voted = False
            return
        voter.night_target = target_uid
        target.votes_received += 1
        await cq.answer(t(game.lang, "voted", voter=voter.name, target=target.name))

    # Update vote keyboard
    try:
        from keyboards import vote_keyboard
        await cq.message.edit_reply_markup(reply_markup=vote_keyboard(game))
    except Exception:
        pass


# ──────────────────────────────────────────────
# NIGHT TARGET callback (PM)
# ──────────────────────────────────────────────
async def cb_night_target(cq: CallbackQuery):
    game = None
    # Find game where this player is
    for g in games.values():
        if cq.from_user.id in g.players:
            game = g
            break

    if not game or game.phase != GamePhase.NIGHT:
        await cq.answer()
        return

    player = game.players.get(cq.from_user.id)
    if not player or not player.is_alive:
        await cq.answer()
        return

    lang = game.lang
    data = cq.data  # ntarget_{uid} or ntarget_skip or ntarget_-1

    if data == "ntarget_skip":
        player.night_target = None
        await cq.answer(t(lang, "night_action_done"))
    elif data == "ntarget_-1":
        player.night_target = -1  # Arsonist ignite
        await cq.answer(t(lang, "night_action_done"))
    else:
        target_uid = int(data.split("_")[1])
        target = game.players.get(target_uid)
        if not target or not target.is_alive:
            await cq.answer(t(lang, "target_dead"))
            return
        if target_uid == cq.from_user.id:
            await cq.answer(t(lang, "target_self"))
            return
        player.night_target = target_uid
        await cq.answer(t(lang, "night_action_done"))

    try:
        await cq.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass


# ──────────────────────────────────────────────
# MAFIA VOTE callback (PM)
# ──────────────────────────────────────────────
async def cb_mafia_vote(cq: CallbackQuery):
    game = None
    for g in games.values():
        if cq.from_user.id in g.players:
            game = g
            break

    if not game or game.phase != GamePhase.NIGHT:
        await cq.answer()
        return

    player = game.players.get(cq.from_user.id)
    if not player or not player.is_alive:
        await cq.answer()
        return

    lang = game.lang
    data = cq.data

    if data == "mafvote_skip":
        await cq.answer(t(lang, "night_action_done"))
        return

    target_uid = int(data.split("_")[1])
    target = game.players.get(target_uid)
    if not target or not target.is_alive:
        await cq.answer(t(lang, "target_dead"))
        return

    game.mafia_votes[cq.from_user.id] = target_uid
    await cq.answer(t(lang, "night_action_done"))

    try:
        await cq.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass


# ──────────────────────────────────────────────
# VETERAN ALERT callback
# ──────────────────────────────────────────────
async def cb_veteran_alert(cq: CallbackQuery):
    game = None
    for g in games.values():
        if cq.from_user.id in g.players:
            game = g
            break

    if not game:
        await cq.answer()
        return

    player = game.players.get(cq.from_user.id)
    if not player or player.role_id != RoleID.VETERAN:
        await cq.answer()
        return

    lang = game.lang
    if player.veteran_alerts_left <= 0:
        await cq.answer("❌ Нет больше зарядов!" if lang == "ru" else "❌ No alerts left!")
        return

    player.on_alert = True
    player.veteran_alerts_left -= 1
    await cq.answer(t(lang, "veteran_alert_on"))

    try:
        await cq.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass


# ──────────────────────────────────────────────
# /lastwill — set last will
# ──────────────────────────────────────────────
async def cmd_lastwill(msg: Message):
    if msg.chat.type != "private":
        return

    game = None
    for g in games.values():
        if msg.from_user.id in g.players:
            game = g
            break

    if not game:
        await msg.answer(t(get_lang(msg.from_user.id), "no_game"))
        return

    player = game.players.get(msg.from_user.id)
    if not player:
        return

    lang = game.lang
    will_text = msg.text.replace("/lastwill", "").strip()
    if not will_text:
        await msg.answer(t(lang, "write_lastwill"))
        return

    if len(will_text) > 200:
        await msg.answer(t(lang, "lastwill_toolong"))
        return

    player.last_will = will_text
    await msg.answer(t(lang, "lastwill_saved"))


# ──────────────────────────────────────────────
# /players — list alive players
# ──────────────────────────────────────────────
async def cmd_players(msg: Message):
    if msg.chat.type == "private":
        return
    game = games.get(msg.chat.id)
    if not game:
        await msg.answer(t(get_lang(msg.from_user.id), "no_game"))
        return

    lang = game.lang
    alive = game.get_alive()
    dead = game.get_dead()

    lines = [t(lang, "alive_list", count=len(alive),
               players="\n".join(f"• {p.name}" for p in alive))]
    if dead:
        lines.append(t(lang, "dead_list", count=len(dead),
                       players="\n".join(f"• {p.name} ({role_name(lang, p.role_id)})" for p in dead)))
    await msg.answer("\n\n".join(lines))


# ──────────────────────────────────────────────
# /cancel — admin cancel
# ──────────────────────────────────────────────
async def cmd_cancel(msg: Message):
    if msg.chat.type == "private":
        return
    chat_id = msg.chat.id
    game = games.get(chat_id)
    if not game:
        return

    lang = game.lang
    # Check admin
    member = await msg.bot.get_chat_member(chat_id, msg.from_user.id)
    if member.status not in ("administrator", "creator") and msg.from_user.id != game.creator_id:
        return

    del games[chat_id]
    await msg.answer(t(lang, "game_cancelled"))


# ──────────────────────────────────────────────
# BLACKMAIL message filter
# ──────────────────────────────────────────────
async def filter_blackmailed(msg: Message):
    if msg.chat.type == "private":
        return
    game = games.get(msg.chat.id)
    if not game or game.phase != GamePhase.DAY:
        return

    player = game.players.get(msg.from_user.id)
    if player and player.is_blackmailed and player.is_alive:
        try:
            await msg.delete()
        except Exception:
            pass


# ──────────────────────────────────────────────
# MAYOR REVEAL callback (from /reveal command)
# ──────────────────────────────────────────────
async def cmd_reveal(msg: Message):
    if msg.chat.type == "private":
        return
    game = games.get(msg.chat.id)
    if not game:
        return

    player = game.players.get(msg.from_user.id)
    if not player or player.role_id != RoleID.MAYOR or not player.is_alive:
        return

    player.is_revealed_mayor = True
    await msg.answer(t(game.lang, "mayor_reveal", name=player.name))


# ──────────────────────────────────────────────
# REGISTER ALL HANDLERS
# ──────────────────────────────────────────────
def register_all_handlers(dp: Dispatcher):
    dp.message.register(cmd_start,    Command("start"))
    dp.message.register(cmd_game,     Command("game"))
    dp.message.register(cmd_lang,     Command("lang"))
    dp.message.register(cmd_lastwill, Command("lastwill"))
    dp.message.register(cmd_players,  Command("players"))
    dp.message.register(cmd_cancel,   Command("cancel"))
    dp.message.register(cmd_reveal,   Command("reveal"))
    dp.message.register(filter_blackmailed)

    dp.callback_query.register(cb_lang,          F.data.startswith("lang_"))
    dp.callback_query.register(cb_join,          F.data == "join")
    dp.callback_query.register(cb_leave,         F.data == "leave")
    dp.callback_query.register(cb_startgame,     F.data == "startgame")
    dp.callback_query.register(cb_vote,          F.data.startswith("vote_"))
    dp.callback_query.register(cb_night_target,  F.data.startswith("ntarget_"))
    dp.callback_query.register(cb_mafia_vote,    F.data.startswith("mafvote_"))
    dp.callback_query.register(cb_veteran_alert, F.data == "veteran_alert")
