import asyncio
from aiogram import Dispatcher, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import MIN_PLAYERS, MAX_PLAYERS, JOIN_TIMEOUT
from game_state import GameState, GamePhase, games, user_langs, Player
from roles import RoleID, Faction
from localization import t
from keyboards import (
    reg_keyboard, lang_keyboard, vote_keyboard,
    night_target_keyboard, mafia_vote_keyboard, veteran_keyboard,
    arsonist_keyboard, witch_keyboard,
    profile_keyboard, gender_keyboard,
    shop_main_keyboard, shop_items_keyboard, shop_titles_keyboard, buy_confirm_keyboard,
    mode_keyboard, admin_keyboard,
)
from game_flow import start_game, role_name
import database as db

ADMINS: set[int] = set()  # superadmin IDs (filled from env optionally)


# ── helpers ───────────────────────────────────
def get_lang(user_id: int, game: GameState = None) -> str:
    if game:
        return game.lang
    return user_langs.get(user_id, "ru")


def full_name(user) -> str:
    fn = user.first_name or ""
    ln = user.last_name or ""
    return (fn + " " + ln).strip() or user.username or "Player"


async def is_group_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


# ── /start ────────────────────────────────────
async def cmd_start(msg: Message):
    lang = get_lang(msg.from_user.id)
    db.ensure_player(msg.from_user.id, full_name(msg.from_user), msg.from_user.username or "")
    if msg.chat.type == "private":
        await msg.answer(
            "🤵 <b>HarshMafia</b>\n\n"
            "Добавь бота в групповой чат и используй /newgame!\n"
            "Add me to a group and use /newgame!\n\n"
            "/help — список команд / command list",
            reply_markup=lang_keyboard()
        )
    else:
        await msg.answer(t(lang, "help_text"))


# ── /help ─────────────────────────────────────
async def cmd_help(msg: Message):
    lang = get_lang(msg.from_user.id,
                    games.get(msg.chat.id if msg.chat.type != "private" else 0))
    await msg.answer(t(lang, "help_text"))


# ── /lang ─────────────────────────────────────
async def cmd_lang(msg: Message):
    lang = get_lang(msg.from_user.id)
    await msg.answer(t(lang, "choose_lang"), reply_markup=lang_keyboard())


async def cb_lang(cq: CallbackQuery):
    lang = cq.data.split("_")[1]
    user_langs[cq.from_user.id] = lang
    db.update_player(cq.from_user.id, lang=lang)
    game = games.get(cq.message.chat.id)
    if game:
        game.lang = lang
    await cq.answer(t(lang, "lang_set"))
    try:
        await cq.message.delete()
    except Exception:
        pass


# ── /newgame ──────────────────────────────────
async def cmd_newgame(msg: Message):
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

    name = full_name(msg.from_user)
    db.ensure_player(msg.from_user.id, name, msg.from_user.username or "")
    game.players[msg.from_user.id] = Player(
        user_id=msg.from_user.id, name=name, username=msg.from_user.username
    )

    reg_msg = await msg.answer(
        t(lang, "game_created", count=1, max=MAX_PLAYERS, time=JOIN_TIMEOUT),
        reply_markup=reg_keyboard(lang)
    )
    game.reg_message_id = reg_msg.message_id

    # pin registration message
    try:
        await msg.bot.pin_chat_message(chat_id, reg_msg.message_id, disable_notification=True)
    except Exception:
        pass

    async def auto_close():
        await asyncio.sleep(JOIN_TIMEOUT)
        g = games.get(chat_id)
        if g and g.phase == GamePhase.REGISTRATION:
            if len(g.players) < MIN_PLAYERS:
                await msg.bot.send_message(chat_id, t(g.lang, "not_enough", min=MIN_PLAYERS))
                del games[chat_id]

    asyncio.create_task(auto_close())


# ── JOIN ──────────────────────────────────────
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

    name = full_name(cq.from_user)
    db.ensure_player(cq.from_user.id, name, cq.from_user.username or "")
    game.players[cq.from_user.id] = Player(
        user_id=cq.from_user.id, name=name, username=cq.from_user.username
    )

    count = len(game.players)
    await cq.answer(t(game.lang, "joined", name=name, count=count, max=MAX_PLAYERS))
    try:
        await cq.message.edit_text(
            t(game.lang, "game_created", count=count, max=MAX_PLAYERS, time=JOIN_TIMEOUT),
            reply_markup=reg_keyboard(game.lang)
        )
    except Exception:
        pass


# ── LEAVE ─────────────────────────────────────
async def cb_leave(cq: CallbackQuery):
    chat_id = cq.message.chat.id
    game = games.get(chat_id)
    if not game or game.phase != GamePhase.REGISTRATION:
        await cq.answer()
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
            reply_markup=reg_keyboard(game.lang)
        )
    except Exception:
        pass


# ── START GAME callback ───────────────────────
async def cb_startgame(cq: CallbackQuery):
    chat_id = cq.message.chat.id
    game = games.get(chat_id)
    if not game:
        await cq.answer(t(get_lang(cq.from_user.id), "no_game"))
        return
    if cq.from_user.id != game.creator_id:
        await cq.answer(t(game.lang, "not_creator"))
        return
    if len(game.players) < MIN_PLAYERS:
        await cq.answer(t(game.lang, "not_enough", min=MIN_PLAYERS))
        return

    await cq.answer()
    try:
        await cq.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    asyncio.create_task(start_game(cq.bot, game))


# ── /endgame ──────────────────────────────────
async def cmd_endgame(msg: Message):
    if msg.chat.type == "private":
        return
    chat_id = msg.chat.id
    game = games.get(chat_id)
    if not game:
        return
    lang = game.lang
    is_admin = await is_group_admin(msg.bot, chat_id, msg.from_user.id)
    if msg.from_user.id != game.creator_id and not is_admin:
        await msg.answer(t(lang, "no_permission"))
        return
    del games[chat_id]
    await msg.answer(t(lang, "game_cancelled"))


# ── /mode ─────────────────────────────────────
async def cmd_mode(msg: Message):
    if msg.chat.type == "private":
        return
    chat_id = msg.chat.id
    game = games.get(chat_id)
    if game and game.phase != GamePhase.REGISTRATION:
        return
    lang = get_lang(msg.from_user.id, game)
    current = game.game_mode if game else "classic"
    await msg.answer(t(lang, "mode_title", current=current), reply_markup=mode_keyboard(lang))


async def cb_mode(cq: CallbackQuery):
    chat_id = cq.message.chat.id
    game = games.get(chat_id)
    mode = cq.data.split("_")[1]
    lang = get_lang(cq.from_user.id, game)
    if game:
        game.game_mode = mode
        if mode == "fast":
            game.lang = game.lang  # could adjust timeouts here
    await cq.answer(t(lang, "mode_set", mode=mode))
    try:
        await cq.message.delete()
    except Exception:
        pass


# ── /vote (force vote early) ──────────────────
async def cmd_vote(msg: Message):
    if msg.chat.type == "private":
        return
    chat_id = msg.chat.id
    game = games.get(chat_id)
    if not game or game.phase != GamePhase.DAY:
        return
    lang = game.lang
    is_admin = await is_group_admin(msg.bot, chat_id, msg.from_user.id)
    if msg.from_user.id != game.creator_id and not is_admin:
        return
    # Trigger voting by changing phase (the day loop will pick it up next cycle)
    # For simplicity: send vote keyboard immediately
    for p in game.players.values():
        p.has_voted = False
        p.votes_received = 0
    vote_msg = await msg.answer(t(lang, "vote_start"), reply_markup=vote_keyboard(game))
    game.vote_message_id = vote_msg.message_id
    game.phase = GamePhase.VOTING


# ── VOTE callback ─────────────────────────────
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
    data = cq.data

    if data == "vote_skip":
        voter.night_target = -999
        await cq.answer(t(game.lang, "vote_skip", voter=voter.name))
    else:
        target_uid = int(data.split("_")[1])
        target = game.players.get(target_uid)
        if not target or not target.is_alive:
            voter.has_voted = False
            await cq.answer(t(game.lang, "target_dead"))
            return
        voter.night_target = target_uid
        target.votes_received += 1
        await cq.answer(t(game.lang, "voted", voter=voter.name, target=target.name))

    try:
        await cq.message.edit_reply_markup(reply_markup=vote_keyboard(game))
    except Exception:
        pass


# ── NIGHT TARGET (PM) ─────────────────────────
def _find_game(user_id: int) -> GameState | None:
    for g in games.values():
        if user_id in g.players:
            return g
    return None


async def cb_night_target(cq: CallbackQuery):
    game = _find_game(cq.from_user.id)
    if not game or game.phase != GamePhase.NIGHT:
        await cq.answer()
        return

    player = game.players.get(cq.from_user.id)
    if not player or not player.is_alive:
        await cq.answer()
        return

    lang = game.lang
    data = cq.data

    if data == "ntarget_skip":
        player.night_target = None
    elif data == "ntarget_-1":
        player.night_target = -1  # arsonist ignite
    else:
        target_uid = int(data.split("_")[1])
        if not game.players.get(target_uid) or not game.players[target_uid].is_alive:
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


# ── MAFIA VOTE (PM) ───────────────────────────
async def cb_mafia_vote(cq: CallbackQuery):
    game = _find_game(cq.from_user.id)
    if not game or game.phase != GamePhase.NIGHT:
        await cq.answer()
        return
    player = game.players.get(cq.from_user.id)
    if not player or not player.is_alive:
        await cq.answer()
        return
    lang = game.lang
    if cq.data == "mafvote_skip":
        await cq.answer(t(lang, "night_action_done"))
        return
    target_uid = int(cq.data.split("_")[1])
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


# ── VETERAN ALERT ─────────────────────────────
async def cb_veteran_alert(cq: CallbackQuery):
    game = _find_game(cq.from_user.id)
    if not game:
        await cq.answer()
        return
    player = game.players.get(cq.from_user.id)
    if not player or player.role_id != RoleID.VETERAN:
        await cq.answer()
        return
    lang = game.lang
    if player.veteran_alerts_left <= 0:
        await cq.answer("❌ Нет зарядов!" if lang == "ru" else "❌ No alerts left!")
        return
    player.on_alert = True
    player.veteran_alerts_left -= 1
    await cq.answer(t(lang, "veteran_alert_on"))
    try:
        await cq.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass


# ── /players ──────────────────────────────────
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


# ── /reveal (Mayor) ───────────────────────────
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


# ── /lastwill ─────────────────────────────────
async def cmd_lastwill(msg: Message):
    if msg.chat.type != "private":
        return
    game = _find_game(msg.from_user.id)
    lang = get_lang(msg.from_user.id)
    if not game:
        await msg.answer(t(lang, "no_game"))
        return
    player = game.players.get(msg.from_user.id)
    if not player:
        return
    will_text = msg.text.replace("/lastwill", "").strip()
    if not will_text:
        await msg.answer(t(lang, "write_lastwill"))
        return
    if len(will_text) > 200:
        await msg.answer(t(lang, "lastwill_toolong"))
        return
    player.last_will = will_text
    await msg.answer(t(lang, "lastwill_saved"))


# ── /cancel ───────────────────────────────────
async def cmd_cancel(msg: Message):
    if msg.chat.type == "private":
        return
    chat_id = msg.chat.id
    game = games.get(chat_id)
    if not game:
        return
    is_admin = await is_group_admin(msg.bot, chat_id, msg.from_user.id)
    if msg.from_user.id != game.creator_id and not is_admin:
        return
    del games[chat_id]
    await msg.answer(t(game.lang, "game_cancelled"))


# ── /profile ──────────────────────────────────
async def cmd_profile(msg: Message):
    uid = msg.from_user.id
    name = full_name(msg.from_user)
    db.ensure_player(uid, name, msg.from_user.username or "")
    await _send_profile(msg, uid)


async def _send_profile(msg_or_cq, uid: int, edit=False):
    p = db.get_player(uid)
    if not p:
        return
    lang = user_langs.get(uid, "ru")
    title = f"[{p['title']}] " if p["title"] else ""
    text = (t(lang, "profile_title", title=title, name=p["name"])
            + t(lang, "profile_body",
                money=p["money"], gems=p["gems"],
                shield=p["shield"], documents=p["documents"],
                active_role=p["active_role"],
                games_played=p["games_played"], games_won=p["games_won"],
                kills=p["kills"]))
    if not p["gender"]:
        text += t(lang, "profile_no_gender")
    kb = profile_keyboard(lang)
    if isinstance(msg_or_cq, Message):
        await msg_or_cq.answer(text, reply_markup=kb)
    else:
        if edit:
            try:
                await msg_or_cq.message.edit_text(text, reply_markup=kb)
            except Exception:
                await msg_or_cq.message.answer(text, reply_markup=kb)
        else:
            await msg_or_cq.message.answer(text, reply_markup=kb)


async def cb_open_profile(cq: CallbackQuery):
    uid = cq.from_user.id
    db.ensure_player(uid, full_name(cq.from_user), cq.from_user.username or "")
    await _send_profile(cq, uid, edit=True)
    await cq.answer()


# ── /gender ───────────────────────────────────
async def cmd_gender(msg: Message):
    uid = msg.from_user.id
    lang = get_lang(uid)
    db.ensure_player(uid, full_name(msg.from_user), msg.from_user.username or "")
    p = db.get_player(uid)
    if p and p["gender"]:
        await msg.answer(t(lang, "gender_already"))
        return
    await msg.answer(t(lang, "gender_prompt"), reply_markup=gender_keyboard(lang))


async def cb_gender(cq: CallbackQuery):
    uid = cq.from_user.id
    lang = get_lang(uid)
    p = db.get_player(uid)
    if p and p["gender"]:
        await cq.answer(t(lang, "gender_already"))
        return
    gender = "male" if cq.data == "gender_male" else "female"
    db.update_player(uid, gender=gender)
    p2 = db.get_player(uid)
    new_ar = (p2["active_role"] if p2 else 0) + 1
    db.update_player(uid, active_role=new_ar)
    await cq.answer(t(lang, "gender_set"))
    try:
        await cq.message.delete()
    except Exception:
        pass
    await _send_profile(cq, uid)


# ── /shop ─────────────────────────────────────
async def cmd_shop(msg: Message):
    uid = msg.from_user.id
    lang = get_lang(uid)
    db.ensure_player(uid, full_name(msg.from_user), msg.from_user.username or "")
    p = db.get_player(uid)
    await msg.answer(
        t(lang, "shop_title", money=p["money"] if p else 0, gems=p["gems"] if p else 0),
        reply_markup=shop_main_keyboard(lang)
    )


async def cb_open_shop(cq: CallbackQuery):
    uid = cq.from_user.id
    lang = get_lang(uid)
    p = db.get_player(uid)
    text = t(lang, "shop_title", money=p["money"] if p else 0, gems=p["gems"] if p else 0)
    try:
        await cq.message.edit_text(text, reply_markup=shop_main_keyboard(lang))
    except Exception:
        await cq.message.answer(text, reply_markup=shop_main_keyboard(lang))
    await cq.answer()


async def cb_shop_items(cq: CallbackQuery):
    lang = get_lang(cq.from_user.id)
    p = db.get_player(cq.from_user.id)
    try:
        await cq.message.edit_text(
            t(lang, "shop_items_list"),
            reply_markup=shop_items_keyboard(lang)
        )
    except Exception:
        pass
    await cq.answer()


async def cb_shop_titles(cq: CallbackQuery):
    lang = get_lang(cq.from_user.id)
    try:
        await cq.message.edit_text(
            t(lang, "shop_titles_list"),
            reply_markup=shop_titles_keyboard(lang)
        )
    except Exception:
        pass
    await cq.answer()


# buy_ callbacks — show confirm
async def cb_buy_item(cq: CallbackQuery):
    uid = cq.from_user.id
    lang = get_lang(uid)
    item_id = cq.data.replace("buy_", "")

    items_info = {
        "shield":      ("🛡 " + ("Защита" if lang == "ru" else "Shield"),          "💵100"),
        "documents":   ("📁 " + ("Документы" if lang == "ru" else "Documents"),    "💵150"),
        "active_role": ("🎭 " + ("Активная роль" if lang == "ru" else "Active Role"),"💎1"),
        "title_don":   ("👑 " + ("Дон" if lang == "ru" else "Don"),               "💵500"),
        "title_sheriff":("⭐ " + ("Шериф" if lang == "ru" else "Sheriff"),         "💵500"),
        "title_vip":   ("💎 VIP",                                                  "💎5"),
    }
    info = items_info.get(item_id)
    if not info:
        await cq.answer(t(lang, "item_not_found"))
        return
    name, price = info
    try:
        await cq.message.edit_text(
            t(lang, "buy_confirm", name=name, price=price),
            reply_markup=buy_confirm_keyboard(lang, item_id)
        )
    except Exception:
        pass
    await cq.answer()


# buyconfirm_ callback — actual purchase
async def cb_buy_confirm(cq: CallbackQuery):
    uid = cq.from_user.id
    lang = get_lang(uid)
    item_id = cq.data.replace("buyconfirm_", "")

    success, err = db.buy_item(uid, item_id)
    if success:
        items_info = {
            "shield":       "🛡 " + ("Защита" if lang == "ru" else "Shield"),
            "documents":    "📁 " + ("Документы" if lang == "ru" else "Documents"),
            "active_role":  "🎭 " + ("Активная роль" if lang == "ru" else "Active Role"),
            "title_don":    "👑 " + ("Дон" if lang == "ru" else "Don"),
            "title_sheriff":"⭐ " + ("Шериф" if lang == "ru" else "Sheriff"),
            "title_vip":    "💎 VIP",
        }
        name = items_info.get(item_id, item_id)
        await cq.answer(t(lang, "buy_success", name=name), show_alert=True)
        # Refresh profile
        p = db.get_player(uid)
        try:
            await cq.message.edit_text(
                t(lang, "shop_title", money=p["money"] if p else 0, gems=p["gems"] if p else 0),
                reply_markup=shop_main_keyboard(lang)
            )
        except Exception:
            pass
    else:
        p = db.get_player(uid)
        if err == "not_enough_money":
            item = next((i for i in db.get_shop_items() if i["item_id"] == item_id), None)
            need = item["price_money"] if item else "?"
            await cq.answer(t(lang, "buy_no_money", need=need, have=p["money"] if p else 0), show_alert=True)
        elif err == "not_enough_gems":
            item = next((i for i in db.get_shop_items() if i["item_id"] == item_id), None)
            need = item["price_gems"] if item else "?"
            await cq.answer(t(lang, "buy_no_gems", need=need, have=p["gems"] if p else 0), show_alert=True)
        else:
            await cq.answer(t(lang, "item_not_found"), show_alert=True)


# ── /stats ────────────────────────────────────
async def cmd_stats(msg: Message):
    uid = msg.from_user.id
    lang = get_lang(uid)
    db.ensure_player(uid, full_name(msg.from_user), msg.from_user.username or "")
    await _send_stats(msg, uid, lang)


async def cb_open_stats(cq: CallbackQuery):
    uid = cq.from_user.id
    lang = get_lang(uid)
    await _send_stats(cq.message, uid, lang)
    await cq.answer()


async def _send_stats(msg: Message, uid: int, lang: str):
    p = db.get_player(uid)
    if not p:
        return
    gp = p["games_played"]
    gw = p["games_won"]
    wr = round(gw / gp * 100) if gp > 0 else 0
    text = (t(lang, "stats_title", name=p["name"])
            + t(lang, "stats_body",
                games_played=gp, games_won=gw, winrate=wr,
                kills=p["kills"], money=p["money"], gems=p["gems"]))
    await msg.answer(text)


# ── /top ──────────────────────────────────────
async def cmd_top(msg: Message):
    lang = get_lang(msg.from_user.id)
    await _send_top(msg, lang)


async def cb_open_top(cq: CallbackQuery):
    lang = get_lang(cq.from_user.id)
    await _send_top(cq.message, lang)
    await cq.answer()


async def _send_top(msg: Message, lang: str):
    rows = db.get_top(10)
    if not rows:
        await msg.answer(t(lang, "top_title") + t(lang, "top_empty"))
        return
    places = ["🥇", "🥈", "🥉"] + [f"{i}." for i in range(4, 11)]
    lines = [t(lang, "top_title")]
    for i, row in enumerate(rows):
        place = places[i] if i < len(places) else f"{i+1}."
        lines.append(t(lang, "top_line",
                       place=place, name=row["name"],
                       wins=row["games_won"], kills=row["kills"]))
    await msg.answer("".join(lines))


# ── /admin ────────────────────────────────────
async def cmd_admin(msg: Message):
    uid = msg.from_user.id
    if msg.chat.type != "private":
        is_admin = await is_group_admin(msg.bot, msg.chat.id, uid)
        if not is_admin and uid not in ADMINS:
            await msg.answer(t(get_lang(uid), "admin_not_admin"))
            return

    lang = get_lang(uid)
    await msg.answer(t(lang, "admin_title"), reply_markup=admin_keyboard(lang))


async def cb_admin_givemoney(cq: CallbackQuery):
    lang = get_lang(cq.from_user.id)
    await cq.answer()
    await cq.message.answer(t(lang, "admin_give_prompt") if lang == "ru" else
                             "Reply:\n/givemoney @username amount")


async def cb_admin_givegems(cq: CallbackQuery):
    lang = get_lang(cq.from_user.id)
    await cq.answer()
    await cq.message.answer(t(lang, "admin_give_prompt"))


async def cb_admin_endgame(cq: CallbackQuery):
    lang = get_lang(cq.from_user.id)
    # Find a game associated with this admin (simplified: end any game)
    await cq.answer("Use /endgame in the group chat.", show_alert=True)


# ── /givemoney & /givegems ────────────────────
async def cmd_givemoney(msg: Message):
    uid = msg.from_user.id
    lang = get_lang(uid)
    is_superadmin = uid in ADMINS
    if not is_superadmin:
        is_admin = await is_group_admin(msg.bot, msg.chat.id, uid) if msg.chat.type != "private" else False
        if not is_admin:
            return

    parts = msg.text.split()
    if len(parts) < 3:
        return
    target_username = parts[1].lstrip("@")
    try:
        amount = int(parts[2])
    except ValueError:
        return

    with db.get_conn() as conn:
        row = conn.execute("SELECT user_id, name FROM players WHERE username=?",
                           (target_username,)).fetchone()
    if not row:
        await msg.answer("❌ Player not found.")
        return
    db.add_money(row["user_id"], amount)
    await msg.answer(t(lang, "admin_give_ok", amount=amount, currency="💵", name=row["name"]))


async def cmd_givegems(msg: Message):
    uid = msg.from_user.id
    lang = get_lang(uid)
    parts = msg.text.split()
    if len(parts) < 3:
        return
    target_username = parts[1].lstrip("@")
    try:
        amount = int(parts[2])
    except ValueError:
        return
    with db.get_conn() as conn:
        row = conn.execute("SELECT user_id, name FROM players WHERE username=?",
                           (target_username,)).fetchone()
    if not row:
        await msg.answer("❌ Player not found.")
        return
    db.add_gems(row["user_id"], amount)
    await msg.answer(t(lang, "admin_give_ok", amount=amount, currency="💎", name=row["name"]))


# ── BLACKMAIL message filter ───────────────────
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


# ── REGISTER ─────────────────────────────────
def register_all_handlers(dp: Dispatcher):
    dp.message.register(cmd_start,     Command("start"))
    dp.message.register(cmd_help,      Command("help"))
    dp.message.register(cmd_newgame,   Command("newgame", "game"))
    dp.message.register(cmd_endgame,   Command("endgame"))
    dp.message.register(cmd_mode,      Command("mode"))
    dp.message.register(cmd_vote,      Command("vote"))
    dp.message.register(cmd_players,   Command("players"))
    dp.message.register(cmd_reveal,    Command("reveal"))
    dp.message.register(cmd_cancel,    Command("cancel"))
    dp.message.register(cmd_lastwill,  Command("lastwill"))
    dp.message.register(cmd_lang,      Command("lang"))
    dp.message.register(cmd_profile,   Command("profile"))
    dp.message.register(cmd_gender,    Command("gender"))
    dp.message.register(cmd_shop,      Command("shop"))
    dp.message.register(cmd_stats,     Command("stats"))
    dp.message.register(cmd_top,       Command("top"))
    dp.message.register(cmd_admin,     Command("admin"))
    dp.message.register(cmd_givemoney, Command("givemoney"))
    dp.message.register(cmd_givegems,  Command("givegems"))
    dp.message.register(filter_blackmailed)

    dp.callback_query.register(cb_lang,           F.data.startswith("lang_"))
    dp.callback_query.register(cb_join,            F.data == "join")
    dp.callback_query.register(cb_leave,           F.data == "leave")
    dp.callback_query.register(cb_startgame,       F.data == "startgame")
    dp.callback_query.register(cb_vote,            F.data.startswith("vote_"))
    dp.callback_query.register(cb_night_target,    F.data.startswith("ntarget_"))
    dp.callback_query.register(cb_mafia_vote,      F.data.startswith("mafvote_"))
    dp.callback_query.register(cb_veteran_alert,   F.data == "veteran_alert")
    dp.callback_query.register(cb_mode,            F.data.startswith("mode_"))
    dp.callback_query.register(cb_open_profile,    F.data == "open_profile")
    dp.callback_query.register(cb_gender,          F.data.startswith("gender_"))
    dp.callback_query.register(cb_open_shop,       F.data == "open_shop")
    dp.callback_query.register(cb_shop_items,      F.data == "shop_items")
    dp.callback_query.register(cb_shop_titles,     F.data == "shop_titles")
    dp.callback_query.register(cb_buy_item,        F.data.startswith("buy_") & ~F.data.startswith("buyconfirm_"))
    dp.callback_query.register(cb_buy_confirm,     F.data.startswith("buyconfirm_"))
    dp.callback_query.register(cb_open_stats,      F.data == "open_stats")
    dp.callback_query.register(cb_open_top,        F.data == "open_top")
    dp.callback_query.register(cb_open_lang,       F.data == "open_lang")
    dp.callback_query.register(cb_admin_givemoney, F.data == "admin_givemoney")
    dp.callback_query.register(cb_admin_givegems,  F.data == "admin_givegems")
    dp.callback_query.register(cb_admin_endgame,   F.data == "admin_endgame")


async def cb_open_lang(cq: CallbackQuery):
    lang = get_lang(cq.from_user.id)
    await cq.message.answer(t(lang, "choose_lang"), reply_markup=lang_keyboard())
    await cq.answer()