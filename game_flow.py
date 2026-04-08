"""
Game flow controller.
Handles the high-level game loop: registration → night → day → voting → repeat.
"""
import asyncio
from aiogram import Bot
from aiogram.types import Message

from config import (JOIN_TIMEOUT, DAY_TIMEOUT, VOTE_TIMEOUT, NIGHT_TIMEOUT,
                    MIN_PLAYERS, MAX_PLAYERS)
from game_state import GameState, GamePhase, games, Player
from roles import RoleID, Faction, ROLES
from localization import t
from keyboards import (vote_keyboard, night_target_keyboard, mafia_vote_keyboard,
                       arsonist_keyboard, witch_keyboard, veteran_keyboard)
from night_engine import resolve_night


# ──────────────────────────────────────────────
# ROLE → locale key mapping
# ──────────────────────────────────────────────
ROLE_LOCALE = {
    RoleID.CITIZEN:      ("role_citizen",      "desc_citizen"),
    RoleID.DETECTIVE:    ("role_detective",    "desc_detective"),
    RoleID.SHERIFF:      ("role_sheriff",      "desc_sheriff"),
    RoleID.DOCTOR:       ("role_doctor",       "desc_doctor"),
    RoleID.BODYGUARD:    ("role_bodyguard",    "desc_bodyguard"),
    RoleID.VIGILANTE:    ("role_vigilante",    "desc_vigilante"),
    RoleID.JOURNALIST:   ("role_journalist",   "desc_journalist"),
    RoleID.MAYOR:        ("role_mayor",        "desc_mayor"),
    RoleID.LAWYER:       ("role_lawyer",       "desc_lawyer"),
    RoleID.BOMB:         ("role_bomb",         "desc_bomb"),
    RoleID.SPY:          ("role_spy",          "desc_spy"),
    RoleID.VETERAN:      ("role_veteran",      "desc_veteran"),
    RoleID.ESCORT:       ("role_escort",       "desc_escort"),
    RoleID.LOOKOUT:      ("role_lookout",      "desc_lookout"),
    RoleID.ANGEL:        ("role_angel",        "desc_angel"),
    RoleID.TERRORIST:    ("role_terrorist",    "desc_terrorist"),
    RoleID.MAFIA:        ("role_mafia",        "desc_mafia"),
    RoleID.DON:          ("role_don",          "desc_don"),
    RoleID.GODFATHER:    ("role_godfather",    "desc_godfather"),
    RoleID.CONSORT:      ("role_consort",      "desc_consort"),
    RoleID.FRAMER:       ("role_framer",       "desc_framer"),
    RoleID.BLACKMAILER:  ("role_blackmailer",  "desc_blackmailer"),
    RoleID.DISGUISER:    ("role_disguiser",    "desc_disguiser"),
    RoleID.FORGER:       ("role_forger",       "desc_forger"),
    RoleID.MANIAC:       ("role_maniac",       "desc_maniac"),
    RoleID.PROSTITUTE:   ("role_prostitute",   "desc_prostitute"),
    RoleID.WITCH:        ("role_witch",        "desc_witch"),
    RoleID.JESTER:       ("role_jester",       "desc_jester"),
    RoleID.EXECUTIONER:  ("role_executioner",  "desc_executioner"),
    RoleID.SERIAL_KILLER:("role_serial_killer","desc_serial_killer"),
    RoleID.ARSONIST:     ("role_arsonist",     "desc_arsonist"),
    RoleID.WEREWOLF:     ("role_werewolf",     "desc_werewolf"),
    RoleID.CULT_LEADER:  ("role_cult_leader",  "desc_cult_leader"),
    RoleID.CULTIST:      ("role_citizen",      "desc_citizen"),
}


def role_name(lang: str, role_id: RoleID) -> str:
    key = ROLE_LOCALE.get(role_id, ("role_citizen", "desc_citizen"))[0]
    return t(lang, key)


def role_desc(lang: str, role_id: RoleID) -> str:
    key = ROLE_LOCALE.get(role_id, ("role_citizen", "desc_citizen"))[1]
    return t(lang, key)


# ──────────────────────────────────────────────
# SEND ROLE CARDS
# ──────────────────────────────────────────────
async def send_role_cards(bot: Bot, game: GameState):
    lang = game.lang
    mafia_members = [p for p in game.players.values() if p.faction == Faction.MAFIA]
    mafia_names = ", ".join(p.name for p in mafia_members)

    for uid, player in game.players.items():
        role_text = t(lang, "your_role",
                      role=role_name(lang, player.role_id),
                      desc=role_desc(lang, player.role_id))

        if player.faction == Faction.MAFIA:
            role_text += f"\n\n🔫 {t(lang, 'mafia_chat', members=mafia_names, target='?')}"

        if player.role_id == RoleID.EXECUTIONER and player.executioner_target:
            target = game.players.get(player.executioner_target)
            if target:
                role_text += f"\n\n{t(lang, 'executioner_target', name=target.name)}"

        if player.role_id == RoleID.ANGEL and player.angel_target:
            target = game.players.get(player.angel_target)
            if target:
                role_text += f"\n\n😇 {'Твоя подопечная' if lang == 'ru' else 'Your ward'}: <b>{target.name}</b>"

        try:
            await bot.send_message(uid, role_text)
        except Exception:
            pass  # User may not have started the bot


# ──────────────────────────────────────────────
# NIGHT PHASE
# ──────────────────────────────────────────────
async def run_night(bot: Bot, game: GameState):
    lang = game.lang
    game.phase = GamePhase.NIGHT
    game.night_number += 1
    game.reset_night_data()

    await bot.send_message(game.chat_id, t(lang, "night_start", night=game.night_number))

    # Send action prompts via PM
    for uid, player in game.players.items():
        if not player.is_alive:
            continue

        try:
            if player.role_id in (RoleID.MAFIA, RoleID.DON, RoleID.GODFATHER,
                                   RoleID.CONSORT, RoleID.FRAMER, RoleID.BLACKMAILER,
                                   RoleID.DISGUISER, RoleID.FORGER):
                kb = mafia_vote_keyboard(game, uid)
                await bot.send_message(uid, t(lang, "night_action_prompt", night=game.night_number), reply_markup=kb)

            elif player.role_id == RoleID.VETERAN:
                await bot.send_message(uid, t(lang, "night_action_prompt", night=game.night_number),
                                        reply_markup=veteran_keyboard(lang))

            elif player.role_id == RoleID.ARSONIST:
                kb = night_target_keyboard(game, uid, lang,
                    extra_buttons=[[{"text": t(lang, "arsonist_ignite"), "callback_data": "ntarget_-1"}]])
                await bot.send_message(uid, t(lang, "night_action_prompt", night=game.night_number),
                                        reply_markup=arsonist_keyboard(lang))

            elif player.role_id == RoleID.WITCH:
                mafia_target = game.mafia_kill_target
                if mafia_target:
                    mt = game.players.get(mafia_target)
                    if mt:
                        await bot.send_message(uid, t(lang, "witch_see_target", name=mt.name))
                await bot.send_message(uid, t(lang, "night_action_prompt", night=game.night_number),
                                        reply_markup=witch_keyboard(lang, player.witch_heal_used, player.witch_kill_used))

            elif ROLES[player.role_id].has_night_action:
                kb = night_target_keyboard(game, uid, lang)
                await bot.send_message(uid, t(lang, "night_action_prompt", night=game.night_number), reply_markup=kb)

        except Exception:
            pass

    await asyncio.sleep(NIGHT_TIMEOUT)

    # Resolve mafia kill target from votes
    if game.mafia_votes:
        from collections import Counter
        counts = Counter(game.mafia_votes.values())
        game.mafia_kill_target = counts.most_common(1)[0][0]

    events = resolve_night(game)
    game.night_events = events

    # Send check results via PM
    for checker_uid, target_uid in game.night_checks.items():
        checker = game.players.get(checker_uid)
        target = game.players.get(target_uid)
        if not checker or not target:
            continue
        try:
            if checker.role_id == RoleID.DETECTIVE:
                framed = target_uid in game.night_frames
                if framed:
                    result = t(lang, "role_mafia")
                elif ROLES[target.role_id].appears_innocent:
                    result = t(lang, "role_citizen")
                else:
                    faction_str = "🔴 Мафия" if target.faction == Faction.MAFIA else "🟢 Мирный"
                    if lang == "en":
                        faction_str = "🔴 Mafia" if target.faction == Faction.MAFIA else "🟢 Town"
                    result = faction_str
                msg = f"🔍 {target.name}: {result}"
                await bot.send_message(checker_uid, msg)

            elif checker.role_id == RoleID.DON:
                is_det = target.role_id == RoleID.DETECTIVE
                msg = f"👑 {target.name}: {'🔍 Детектив' if is_det else '✅ Не детектив'}"
                if lang == "en":
                    msg = f"👑 {target.name}: {'🔍 Detective' if is_det else '✅ Not detective'}"
                await bot.send_message(checker_uid, msg)

        except Exception:
            pass

    # Send cult conversion notice
    for uid, p in game.players.items():
        if p.cult_converted:
            p.cult_converted = False
            try:
                await bot.send_message(uid, t(lang, "cult_converted"))
            except Exception:
                pass

    # Send spy report
    spy = game.get_by_role(RoleID.SPY)
    if spy:
        visit_lines = []
        for visitor_uid, visitor in game.players.items():
            if visitor.night_target and visitor.night_target != visitor_uid:
                target = game.players.get(visitor.night_target)
                if target:
                    visit_lines.append(f"• {visitor.name} → {target.name}")
        msg = t(lang, "spy_report", visits="\n".join(visit_lines)) if visit_lines else t(lang, "spy_no_visits")
        try:
            await bot.send_message(spy.user_id, msg)
        except Exception:
            pass

    # Send lookout report
    for uid, p in game.players.items():
        if p.role_id == RoleID.LOOKOUT and p.night_target:
            target = game.players.get(p.night_target)
            if target:
                visitors = [v.name for v in game.players.values()
                            if v.night_target == p.night_target and v.user_id != uid]
                if visitors:
                    msg = t(lang, "lookout_report", target=target.name, visitors=", ".join(visitors))
                else:
                    msg = t(lang, "lookout_nobody", target=target.name)
                try:
                    await bot.send_message(uid, msg)
                except Exception:
                    pass


# ──────────────────────────────────────────────
# DAY PHASE
# ──────────────────────────────────────────────
async def run_day(bot: Bot, game: GameState):
    lang = game.lang
    game.phase = GamePhase.DAY
    game.day_number += 1

    # Build events text
    event_lines = []
    if not game.night_events:
        event_lines.append(t(lang, "nobody_died"))
    else:
        for ev_key, ev_args in game.night_events:
            line = t(lang, ev_key, **ev_args) if ev_args else t(lang, ev_key)
            event_lines.append(line)

    events_text = "\n".join(event_lines)
    await bot.send_message(game.chat_id,
                           t(lang, "day_start", day=game.day_number,
                             events=events_text, time=DAY_TIMEOUT))

    await asyncio.sleep(DAY_TIMEOUT)

    # Check win before voting
    win = game.check_win()
    if win:
        await announce_win(bot, game, win)
        return

    await run_voting(bot, game)


# ──────────────────────────────────────────────
# VOTING PHASE
# ──────────────────────────────────────────────
async def run_voting(bot: Bot, game: GameState):
    lang = game.lang
    game.phase = GamePhase.VOTING

    for p in game.players.values():
        p.has_voted = False
        p.votes_received = 0

    msg = await bot.send_message(game.chat_id, t(lang, "vote_start"),
                                  reply_markup=vote_keyboard(game))
    game.vote_message_id = msg.message_id

    await asyncio.sleep(VOTE_TIMEOUT)

    # Tally votes
    vote_counts: dict[int, int] = {}
    skip_count = 0

    for p in game.players.values():
        if not p.is_alive:
            continue
        vote_weight = 3 if (p.role_id.value == "mayor" and p.is_revealed_mayor) else 1
        if p.night_target == -999:
            skip_count += vote_weight
        elif p.night_target:
            vote_counts[p.night_target] = vote_counts.get(p.night_target, 0) + vote_weight

    if not vote_counts or skip_count >= max(vote_counts.values(), default=0):
        await bot.send_message(game.chat_id, t(lang, "no_lynch"))
    else:
        max_votes = max(vote_counts.values())
        # Tie = no lynch
        top = [uid for uid, v in vote_counts.items() if v == max_votes]
        if len(top) > 1:
            await bot.send_message(game.chat_id, t(lang, "no_lynch"))
        else:
            lynched_uid = top[0]
            lynched = game.players[lynched_uid]

            # Check lynch immunity (Lawyer)
            if lynched.is_immune_to_lynch:
                await bot.send_message(game.chat_id, t(lang, "no_lynch"))
            else:
                lynched.is_alive = False
                display_role = role_name(lang, lynched.role_id)

                # Bomb explosion
                if lynched.role_id == RoleID.BOMB:
                    voters = [game.players[uid] for uid in vote_counts
                              if vote_counts[uid] > 0 and uid != lynched_uid
                              and game.players.get(uid) and game.players[uid].is_alive]
                    for voter in voters:
                        voter.is_alive = False
                    killed_names = ", ".join(v.name for v in voters)
                    await bot.send_message(game.chat_id,
                        t(lang, "bomb_exploded", name=lynched.name, killed=killed_names or "—"))

                await bot.send_message(game.chat_id,
                    t(lang, "lynched", name=lynched.name, role=display_role))

                # Show last will
                if lynched.last_will:
                    await bot.send_message(game.chat_id,
                        t(lang, "last_will", name=lynched.name, will=lynched.last_will))
                else:
                    await bot.send_message(game.chat_id, t(lang, "no_last_will", name=lynched.name))

                # Jester win
                if lynched.role_id == RoleID.JESTER:
                    game.jester_winner = lynched_uid
                    await bot.send_message(game.chat_id, t(lang, "jester_win", name=lynched.name))

                # Executioner win
                for uid, p in game.players.items():
                    if p.role_id == RoleID.EXECUTIONER and p.executioner_target == lynched_uid:
                        game.executioner_winner = uid
                        await bot.send_message(game.chat_id, t(lang, "executioner_win", name=p.name))
                        break

    # Check win
    win = game.check_win()
    if win or game.jester_winner:
        if win:
            await announce_win(bot, game, win)
        return

    # Continue to night
    await run_night(bot, game)
    win = game.check_win()
    if win:
        await announce_win(bot, game, win)
        return
    await run_day(bot, game)


# ──────────────────────────────────────────────
# WIN ANNOUNCEMENT
# ──────────────────────────────────────────────
async def announce_win(bot: Bot, game: GameState, result: str):
    lang = game.lang
    game.phase = GamePhase.ENDED

    if result == "mafia":
        members = ", ".join(p.name for p in game.players.values() if p.faction == Faction.MAFIA)
        msg = t(lang, "mafia_win", members=members)
    elif result == "town":
        survivors = ", ".join(p.name for p in game.get_alive())
        msg = t(lang, "town_win", members=survivors or "—")
    elif result == "maniac":
        msg = t(lang, "maniac_win")
    elif result == "serial_killer":
        msg = t(lang, "maniac_win")
    elif result == "arsonist":
        msg = t(lang, "maniac_win")
    elif result == "werewolf":
        msg = t(lang, "werewolf_win")
    elif result == "cult":
        members = ", ".join(p.name for p in game.players.values() if p.faction.value == "cult")
        msg = t(lang, "cult_win", members=members)
    elif result == "draw":
        msg = t(lang, "draw")
    else:
        msg = "Game over."

    # Reveal all roles
    reveal_lines = []
    for p in game.players.values():
        status = "💚" if p.is_alive else "💀"
        reveal_lines.append(f"{status} {p.name} — {role_name(lang, p.role_id)}")

    full_msg = msg + "\n\n" + "\n".join(reveal_lines)
    await bot.send_message(game.chat_id, full_msg)

    # Clean up
    if game.chat_id in games:
        del games[game.chat_id]


# ──────────────────────────────────────────────
# START GAME
# ──────────────────────────────────────────────
async def start_game(bot: Bot, game: GameState):
    game.assign_roles()
    await send_role_cards(bot, game)
    await asyncio.sleep(3)
    await run_night(bot, game)
    win = game.check_win()
    if win:
        await announce_win(bot, game, win)
        return
    await run_day(bot, game)
