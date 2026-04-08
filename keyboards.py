from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_state import GameState, Player

from localization import t


def reg_keyboard(lang: str, count: int, max_count: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(lang, "join_btn"), callback_data="join"),
            InlineKeyboardButton(text=t(lang, "leave_btn"), callback_data="leave"),
        ],
        [
            InlineKeyboardButton(text=t(lang, "start_btn"), callback_data="startgame"),
        ]
    ])


def vote_keyboard(game: "GameState") -> InlineKeyboardMarkup:
    lang = game.lang
    buttons = []
    row = []
    alive = game.get_alive()
    for i, p in enumerate(alive):
        votes = p.votes_received
        btn = InlineKeyboardButton(
            text=t(lang, "vote_btn", name=p.name, votes=votes),
            callback_data=f"vote_{p.user_id}"
        )
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    skip_votes = sum(1 for p in game.players.values() if p.has_voted and p.night_target == -999)
    buttons.append([
        InlineKeyboardButton(
            text=t(lang, "skip_btn", votes=skip_votes),
            callback_data="vote_skip"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def night_target_keyboard(game: "GameState", exclude_uid: int, lang: str, extra_buttons: list = None) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for p in game.get_alive():
        if p.user_id == exclude_uid:
            continue
        btn = InlineKeyboardButton(
            text=p.name,
            callback_data=f"ntarget_{p.user_id}"
        )
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(text=t(lang, "night_skip_btn"), callback_data="ntarget_skip")
    ])

    if extra_buttons:
        for eb in extra_buttons:
            buttons.append(eb)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def mafia_vote_keyboard(game: "GameState", exclude_uid: int) -> InlineKeyboardMarkup:
    lang = game.lang
    buttons = []
    row = []
    for p in game.get_alive():
        if p.user_id == exclude_uid:
            continue
        from roles import Faction
        if p.faction == Faction.MAFIA:
            continue
        btn = InlineKeyboardButton(
            text=p.name,
            callback_data=f"mafvote_{p.user_id}"
        )
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(text=t(lang, "night_skip_btn"), callback_data="mafvote_skip")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ]
    ])


def arsonist_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "arsonist_ignite"), callback_data="ntarget_-1")]
    ])


def witch_keyboard(lang: str, used_heal: bool, used_kill: bool) -> InlineKeyboardMarkup:
    btns = []
    if not used_heal:
        btns.append(InlineKeyboardButton(text=t(lang, "witch_heal_btn"), callback_data="witch_heal"))
    if not used_kill:
        btns.append(InlineKeyboardButton(text=t(lang, "witch_kill_btn"), callback_data="witch_kill"))
    return InlineKeyboardMarkup(inline_keyboard=[btns] if btns else [])


def veteran_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎖 На боевую готовность!" if lang == "ru" else "🎖 Go on alert!", callback_data="veteran_alert"),
            InlineKeyboardButton(text=t(lang, "night_skip_btn"), callback_data="ntarget_skip"),
        ]
    ])
