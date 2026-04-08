from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from localization import t


# ── REGISTRATION ──────────────────────────────
def reg_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(lang, "join_btn"),  callback_data="join"),
            InlineKeyboardButton(text=t(lang, "leave_btn"), callback_data="leave"),
        ],
        [InlineKeyboardButton(text=t(lang, "start_btn"), callback_data="startgame")],
    ])


# ── VOTE (day lynching) ───────────────────────
def vote_keyboard(game) -> InlineKeyboardMarkup:
    lang = game.lang
    buttons = []
    row = []
    for p in game.get_alive():
        v = p.votes_received
        btn = InlineKeyboardButton(
            text=t(lang, "vote_btn", name=p.name, votes=v),
            callback_data=f"vote_{p.user_id}"
        )
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    skip_v = sum(1 for p in game.players.values() if p.has_voted and p.night_target == -999)
    buttons.append([
        InlineKeyboardButton(text=t(lang, "skip_btn", votes=skip_v), callback_data="vote_skip")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── NIGHT target (PM) ─────────────────────────
def night_target_keyboard(game, exclude_uid: int, lang: str, extra_rows=None) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for p in game.get_alive():
        if p.user_id == exclude_uid:
            continue
        row.append(InlineKeyboardButton(text=p.name, callback_data=f"ntarget_{p.user_id}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text=t(lang, "night_skip_btn"), callback_data="ntarget_skip")])
    if extra_rows:
        buttons.extend(extra_rows)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def mafia_vote_keyboard(game, exclude_uid: int) -> InlineKeyboardMarkup:
    from roles import Faction
    lang = game.lang
    buttons = []
    row = []
    for p in game.get_alive():
        if p.user_id == exclude_uid or p.faction == Faction.MAFIA:
            continue
        row.append(InlineKeyboardButton(text=p.name, callback_data=f"mafvote_{p.user_id}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text=t(lang, "night_skip_btn"), callback_data="mafvote_skip")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def veteran_keyboard(lang: str) -> InlineKeyboardMarkup:
    alert_text = "🎖 На боевую готовность!" if lang == "ru" else "🎖 Go on alert!"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=alert_text, callback_data="veteran_alert"),
            InlineKeyboardButton(text=t(lang, "night_skip_btn"), callback_data="ntarget_skip"),
        ]
    ])


def arsonist_keyboard(game, exclude_uid: int, lang: str) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for p in game.get_alive():
        if p.user_id == exclude_uid:
            continue
        label = f"🛢 {p.name}" if not p.doused else f"🔥 {p.name}"
        row.append(InlineKeyboardButton(text=label, callback_data=f"ntarget_{p.user_id}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text=t(lang, "arsonist_ignite"), callback_data="ntarget_-1")])
    buttons.append([InlineKeyboardButton(text=t(lang, "night_skip_btn"), callback_data="ntarget_skip")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def witch_keyboard(lang: str, used_heal: bool, used_kill: bool) -> InlineKeyboardMarkup:
    btns = []
    if not used_heal:
        btns.append(InlineKeyboardButton(text=t(lang, "witch_heal_btn"), callback_data="witch_heal"))
    if not used_kill:
        btns.append(InlineKeyboardButton(text=t(lang, "witch_kill_btn"), callback_data="witch_kill"))
    rows = [btns] if btns else []
    rows.append([InlineKeyboardButton(text=t(lang, "night_skip_btn"), callback_data="ntarget_skip")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── LANGUAGE ──────────────────────────────────
def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
    ]])


# ── PROFILE ───────────────────────────────────
def profile_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(lang, "profile_btn_shop"),  callback_data="open_shop"),
            InlineKeyboardButton(text=t(lang, "profile_btn_stats"), callback_data="open_stats"),
        ],
        [
            InlineKeyboardButton(text=t(lang, "profile_btn_top"),  callback_data="open_top"),
            InlineKeyboardButton(text=t(lang, "profile_btn_lang"), callback_data="open_lang"),
        ],
    ])


# ── GENDER ────────────────────────────────────
def gender_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, "gender_male_btn"),   callback_data="gender_male"),
        InlineKeyboardButton(text=t(lang, "gender_female_btn"), callback_data="gender_female"),
    ]])


# ── SHOP ──────────────────────────────────────
def shop_main_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "shop_btn_items"),  callback_data="shop_items")],
        [InlineKeyboardButton(text=t(lang, "shop_btn_titles"), callback_data="shop_titles")],
        [InlineKeyboardButton(text=t(lang, "shop_btn_back"),   callback_data="open_profile")],
    ])


def shop_items_keyboard(lang: str) -> InlineKeyboardMarkup:
    is_ru = lang == "ru"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"🛡 {'Защита' if is_ru else 'Shield'} — 💵100",
            callback_data="buy_shield")],
        [InlineKeyboardButton(
            text=f"📁 {'Документы' if is_ru else 'Documents'} — 💵150",
            callback_data="buy_documents")],
        [InlineKeyboardButton(
            text=f"🎭 {'Активная роль' if is_ru else 'Active Role'} — 💎1",
            callback_data="buy_active_role")],
        [InlineKeyboardButton(text=t(lang, "shop_btn_back"), callback_data="open_shop")],
    ])


def shop_titles_keyboard(lang: str) -> InlineKeyboardMarkup:
    is_ru = lang == "ru"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"👑 {'Дон' if is_ru else 'Don'} — 💵500",
            callback_data="buy_title_don")],
        [InlineKeyboardButton(
            text=f"⭐ {'Шериф' if is_ru else 'Sheriff'} — 💵500",
            callback_data="buy_title_sheriff")],
        [InlineKeyboardButton(
            text=f"💎 VIP — 💎5",
            callback_data="buy_title_vip")],
        [InlineKeyboardButton(text=t(lang, "shop_btn_back"), callback_data="open_shop")],
    ])


def buy_confirm_keyboard(lang: str, item_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, "buy_yes_btn"), callback_data=f"buyconfirm_{item_id}"),
        InlineKeyboardButton(text=t(lang, "buy_no_btn"),  callback_data="open_shop"),
    ]])


# ── MODE ──────────────────────────────────────
def mode_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "mode_classic_btn"), callback_data="mode_classic")],
        [InlineKeyboardButton(text=t(lang, "mode_fast_btn"),    callback_data="mode_fast")],
        [InlineKeyboardButton(text=t(lang, "mode_random_btn"),  callback_data="mode_random")],
    ])


# ── ADMIN ─────────────────────────────────────
def admin_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "admin_give_money"), callback_data="admin_givemoney")],
        [InlineKeyboardButton(text=t(lang, "admin_give_gems"),  callback_data="admin_givegems")],
        [InlineKeyboardButton(text=t(lang, "admin_end_game"),   callback_data="admin_endgame")],
    ])