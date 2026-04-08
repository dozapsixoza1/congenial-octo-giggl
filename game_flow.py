"""
Game flow controller.
Handles: registration → night → day → voting → repeat → economy rewards.
"""
import asyncio
from aiogram import Bot

from config import DAY_TIMEOUT, VOTE_TIMEOUT, NIGHT_TIMEOUT, MIN_PLAYERS
from game_state import GameState, GamePhase, games, Player
from roles import RoleID, Faction, ROLES
from localization import t
from keyboards import (vote_keyboard, night_target_keyboard, mafia_vote_keyboard,
                       arsonist_keyboard, witch_keyboard, veteran_keyboard)
from night_engine import resolve_night
import database as db

# ── role locale map ────────────────────────────
ROLE_LOCALE = {
    RoleID.CITIZEN:      ("role_citizen",       "desc_citizen"),
    RoleID.DETECTIVE:    ("role_detective",     "desc_detective"),
    RoleID.SHERIFF:      ("role_sheriff",       "desc_sheriff"),
    RoleID.DOCTOR:       ("role_doctor",        "desc_doctor"),
    RoleID.BODYGUARD:    ("role_bodyguard",     "desc_bodyguard"),
    RoleID.VIGILANTE:    ("role_vigilante",     "desc_vigilante"),
    RoleID.JOURNALIST:   ("role_journalist",    "desc_journalist"),
    RoleID.MAYOR:        ("role_mayor",         "desc_mayor"),
    RoleID.LAWYER:       ("role_lawyer",        "desc_lawyer"),
    RoleID.BOMB:         ("role_bomb",          "desc_bomb"),
    RoleID.SPY:          ("role_spy",           "desc_spy"),
    RoleID.VETERAN:      ("role_veteran",       "desc_veteran"),
    RoleID.ESCORT:       ("role_escort",        "desc_escort"),
    RoleID.LOOKOUT:      ("role_lookout",       "desc_lookout"),
    RoleID.ANGEL:        ("role_angel",         "desc_angel"),
    RoleID.TERRORIST:    ("role_terrorist",     "desc_terrorist"),
    RoleID.MAFIA:        ("role_mafia",         "desc_mafia"),
    RoleID.DON:          ("role_don",           "desc_don"),
    RoleID.GODFATHER:    ("role_godfather",     "desc_godfather"),
    RoleID.CONSORT:      ("role_consort",       "desc_consort"),
    RoleID.FRAMER:       ("role_framer",        "desc_framer"),
    RoleID.BLACKMAILER:  ("role_blackmailer",   "desc_blackmailer"),
    RoleID.DISGUISER:    ("role_disguiser",     "desc_disguiser"),
    RoleID.FORGER:       ("role_forger",        "desc_forger"),
    RoleID.MANIAC:       ("role_maniac",        "desc_maniac"),
    RoleID.PROSTITUTE:   ("role_prostitute",    "desc_prostitute"),
    RoleID.WITCH:        ("role_witch",         "desc_witch"),
    RoleID.JESTER:       ("role_jester",        "desc_jester"),
    RoleID.EXECUTIONER:  ("role_executioner",   "desc_executioner"),
    RoleID.SERIAL_KILLER:("role_serial_killer", "desc_serial_killer"),
    RoleID.ARSONIST:     ("role_arsonist",      "desc_arsonist"),
    RoleID.WEREWOLF:     ("role_werewolf",      "desc_werewolf"),
    RoleID.CULT_LEADER:  ("role_cult_leader",   "desc_cult_leader"),
    RoleID.CULTIST:      ("role_citizen",       "desc_citizen"),
}


def role_name(lang: str, role_id: RoleID) -> str:
    key = ROLE_LOCALE.get(role_id, ("role_citizen", "desc_citizen"))[0]
    return t(lang, key)


def role_desc(lang: str, role_id: RoleID) -> str:
    key = ROLE_LOCALE.get(role_id, ("role_citizen", "desc_citizen"))[1]
    return t(lang, key)


# ── SEND ROLE CARDS ───────────────────────────
async def send_role_cards(bot: Bot, game: GameState):
    lang = game.lang
    mafia_members = [p for p in game.players.values() if p.faction == Faction.MAFIA]
    mafia_names = ", ".join(p.name for p in mafia_members)

    for uid, player in game.players.items():
        rname = role_name(lang, player.role_id)
        rdesc = role_desc(lang, player.role_id)
        text = t(lang, "your_role", role=rname, desc=rdesc)

        if player.faction == Faction.MAFIA:
            text += f"\n\n🔫 <b>{'Команда мафии' if lang=='ru' else 'Mafia team'}:</b> {mafia_names}"

        if player.role_id == RoleID.EXECUTIONER and player.executioner_target:
            tgt = game.players.get(player.executioner_target)
            if tgt:
                text += f"\n\n{t(lang, 'executioner_target', name=tgt.name)}"

        if player.role_id == RoleID.ANGEL and player.angel_target:
            tgt = game.players.get(player.angel_target)
            if tgt:
                ward = "Твоя подопечная" if lang == "ru" else "Your ward"
                text += f"\n\n😇 {ward}: <b>{tgt.name}</b>"

        # Check if player has shield or documents from shop
        p_db = db.get_player(uid)
        if p_db:
            items = []
            if p_db["shield"] > 0:
                items.append(f"🛡 {'Защита' if lang=='ru' else 'Shield'} ×{p_db['shield']}")
            if p_db["documents"] > 0:
                items.append(f"📁 {'Документы' if lang=='ru' else 'Documents'} ×{p_db['documents']}")
            if items:
                text += "\n\n🎒 " + ("Твои предметы" if lang == "ru" else "Your items") + ": " + ", ".join(items)

        try:
            await bot.send_message(uid, text)
        except Exception:
            pass


# ── NIGHT PHASE ───────────────────────────────
async def run_night(bot: Bot, game: GameState):
    lang = game.lang
    game.phase = GamePhase.NIGHT
    game.night_number += 1
    game.reset_night_data()

    await bot.send_message(game.chat_id, t(lang, "night_start", night=game.night_number))
    await asyncio.sleep(1)

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
                await bot.send_message(uid, t(lang, "night_action_prompt", night=game.night_number),
                                        reply_markup=arsonist_keyboard(game, uid, lang))

            elif player.role_id == RoleID.WITCH:
                if game.mafia_kill_target:
                    mt = game.players.get(game.mafia_kill_target)
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

    # Resolve mafia vote
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
                # Check if target has documents
                t_db = db.get_player(target_uid)
                has_docs = t_db and t_db["documents"] > 0
                if framed or has_docs or ROLES[target.role_id].appears_innocent:
                    faction_str = "🟢 Мирный" if lang == "ru" else "🟢 Town"
                    if has_docs and t_db["documents"] > 0:
                        db.update_player(target_uid, documents=t_db["documents"] - 1)
                else:
                    if target.faction == Faction.MAFIA:
                        faction_str = "🔴 Мафия" if lang == "ru" else "🔴 Mafia"
                    else:
                        faction_str = "🟢 Мирный" if lang == "ru" else "🟢 Town"
                msg = f"🔍 <b>{target.name}</b>: {faction_str}"
                await bot.send_message(checker_uid, msg)

            elif checker.role_id == RoleID.DON:
                is_det = target.role_id == RoleID.DETECTIVE
                if lang == "ru":
                    res = "🔍 Детектив" if is_det else "✅ Не детектив"
                else:
                    res = "🔍 Detective" if is_det else "✅ Not detective"
                await bot.send_message(checker_uid, f"👑 <b>{target.name}</b>: {res}")
        except Exception:
            pass

    # Cult conversion notice
    for uid, p in game.players.items():
        if p.cult_converted:
            p.cult_converted = False
            try:
                await bot.send_message(uid, t(lang, "cult_converted"))
            except Exception:
                pass

    # Spy report
    spy = game.get_by_role(RoleID.SPY)
    if spy:
        lines = []
        for v in game.players.values():
            if v.night_target and v.night_target != v.user_id:
                tgt = game.players.get(v.night_target)
                if tgt:
                    lines.append(f"• {v.name} → {tgt.name}")
        msg = t(lang, "spy_report", visits="\n".join(lines)) if lines else t(lang, "spy_no_visits")
        try:
            await bot.send_message(spy.user_id, msg)
        except Exception:
            pass

    # Lookout reports
    for uid, p in game.players.items():
        if p.role_id == RoleID.LOOKOUT and p.night_target:
            tgt = game.players.get(p.night_target)
            if tgt:
                visitors = [v.name for v in game.players.values()
                            if v.night_target == p.night_target and v.user_id != uid]
                msg = (t(lang, "lookout_report", target=tgt.name, visitors=", ".join(visitors))
                       if visitors else t(lang, "lookout_nobody", target=tgt.name))
                try:
                    await bot.send_message(uid, msg)
                except Exception:
                    pass


# ── DAY PHASE ─────────────────────────────────
async def run_day(bot: Bot, game: GameState):
    lang = game.lang
    game.phase = GamePhase.DAY
    game.day_number += 1

    lines = []
    if not game.night_events:
        lines.append(t(lang, "nobody_died"))
    else:
        for ev_key, ev_args in game.night_events:
            lines.append(t(lang, ev_key, **ev_args) if ev_args else t(lang, ev_key))

    await bot.send_message(
        game.chat_id,
        t(lang, "day_start", day=game.day_number,
          events="\n".join(lines), time=DAY_TIMEOUT)
    )
    await asyncio.sleep(DAY_TIMEOUT)

    win = game.check_win()
    if win:
        await announce_win(bot, game, win)
        return
    await run_voting(bot, game)


# ── VOTING PHASE ──────────────────────────────
async def run_voting(bot: Bot, game: GameState):
    lang = game.lang
    game.phase = GamePhase.VOTING

    for p in game.players.values():
        p.has_voted = False
        p.votes_received = 0
        p.night_target = None

    msg = await bot.send_message(game.chat_id, t(lang, "vote_start"),
                                  reply_markup=vote_keyboard(game))
    game.vote_message_id = msg.message_id

    await asyncio.sleep(VOTE_TIMEOUT)

    # Count votes
    vote_counts: dict[int, int] = {}
    skip_count = 0
    for p in game.players.values():
        if not p.is_alive:
            continue
        weight = 3 if (p.role_id == RoleID.MAYOR and p.is_revealed_mayor) else 1
        if p.night_target == -999:
            skip_count += weight
        elif p.night_target:
            vote_counts[p.night_target] = vote_counts.get(p.night_target, 0) + weight

    lynched_uid = None
    if vote_counts:
        max_v = max(vote_counts.values())
        if skip_count >= max_v:
            await bot.send_message(game.chat_id, t(lang, "no_lynch"))
        else:
            top = [uid for uid, v in vote_counts.items() if v == max_v]
            if len(top) > 1:
                await bot.send_message(game.chat_id, t(lang, "no_lynch"))
            else:
                lynched_uid = top[0]
                lynched = game.players[lynched_uid]
                if lynched.is_immune_to_lynch:
                    await bot.send_message(game.chat_id, t(lang, "no_lynch"))
                    lynched_uid = None
                else:
                    lynched.is_alive = False
                    display_role = role_name(lang, lynched.role_id)

                    # Bomb explosion
                    if lynched.role_id == RoleID.BOMB:
                        voters = [game.players[uid] for uid in vote_counts
                                  if game.players.get(uid) and game.players[uid].is_alive]
                        for vp in voters:
                            vp.is_alive = False
                        killed = ", ".join(vp.name for vp in voters) or "—"
                        await bot.send_message(game.chat_id, t(lang, "bomb_exploded", name=lynched.name, killed=killed))

                    await bot.send_message(game.chat_id, t(lang, "lynched", name=lynched.name, role=display_role))

                    if lynched.last_will:
                        await bot.send_message(game.chat_id, t(lang, "last_will", name=lynched.name, will=lynched.last_will))
                    else:
                        await bot.send_message(game.chat_id, t(lang, "no_last_will", name=lynched.name))

                    # Jester win
                    if lynched.role_id == RoleID.JESTER:
                        game.jester_winner = lynched_uid
                        await bot.send_message(game.chat_id, t(lang, "jester_win", name=lynched.name))

                    # Executioner win
                    for uid, p in game.players.items():
                        if p.role_id == RoleID.EXECUTIONER and p.executioner_target == lynched_uid and p.is_alive:
                            await bot.send_message(game.chat_id, t(lang, "executioner_win", name=p.name))
                            game.executioner_winner = uid
                            break
    else:
        await bot.send_message(game.chat_id, t(lang, "no_lynch"))

    win = game.check_win()
    if win:
        await announce_win(bot, game, win)
        return

    await run_night(bot, game)
    win = game.check_win()
    if win:
        await announce_win(bot, game, win)
        return
    await run_day(bot, game)


# ── WIN + ECONOMY REWARDS ─────────────────────
async def announce_win(bot: Bot, game: GameState, result: str):
    lang = game.lang
    game.phase = GamePhase.ENDED

    # Determine winners
    winner_faction = result
    if result == "mafia":
        win_members = [p for p in game.players.values() if p.faction == Faction.MAFIA]
        members_str = ", ".join(p.name for p in win_members)
        win_msg = t(lang, "mafia_win", members=members_str)
    elif result == "town":
        win_members = game.get_alive()
        members_str = ", ".join(p.name for p in win_members) or "—"
        win_msg = t(lang, "town_win", members=members_str)
    elif result in ("maniac", "serial_killer", "arsonist"):
        win_msg = t(lang, "maniac_win")
        win_members = [p for p in game.get_alive()]
    elif result == "werewolf":
        win_msg = t(lang, "werewolf_win")
        win_members = [p for p in game.get_alive()]
    elif result == "cult":
        win_members = [p for p in game.players.values() if p.faction.value == "cult"]
        win_msg = t(lang, "cult_win", members=", ".join(p.name for p in win_members))
    else:
        win_msg = t(lang, "draw")
        win_members = []

    winner_ids = {p.user_id for p in win_members}

    # Reveal all roles
    reveal = "\n".join(
        f"{'💚' if p.is_alive else '💀'} {p.name} — {role_name(lang, p.role_id)}"
        for p in game.players.values()
    )
    await bot.send_message(game.chat_id, win_msg + "\n\n" + reveal)

    # Economy rewards
    reward_lines = [t(lang, "reward_header")]
    places = ["🥇", "🥈", "🥉"] + ["🏅"] * 20
    player_results = []

    for i, p in enumerate(game.players.values()):
        won = p.user_id in winner_ids
        # Count kills from night events (simplified)
        killed_count = 0
        for ev_key, ev_args in getattr(game, "all_kills", {}).items():
            pass  # simplified — tracked in game.player_kills
        killed_count = game.player_kills.get(p.user_id, 0)

        earn_money = 20 + (50 if won else 0) + (killed_count * 10)
        earn_gems  = 1 if won else 0

        extra = ""
        if won:
            extra += t(lang, "reward_won_bonus")
        if killed_count:
            extra += t(lang, "reward_kills_bonus", n=killed_count)

        place = places[i] if i < len(places) else "🏅"
        reward_lines.append(
            t(lang, "reward_line",
              place=place, name=p.name,
              role=role_name(lang, p.role_id),
              money=earn_money, extra=extra)
        )

        # Update DB
        db.ensure_player(p.user_id, p.name, p.username or "")
        db.add_money(p.user_id, earn_money)
        if earn_gems:
            db.add_gems(p.user_id, earn_gems)
        player_results.append({
            "user_id": p.user_id, "name": p.name,
            "role": p.role_id.value, "won": won, "killed": killed_count
        })

    await bot.send_message(game.chat_id, "".join(reward_lines))

    # Notify winners in PM
    for p in win_members:
        if p.user_id in game.players:
            try:
                msg = (
                    f"🏆 {'Поздравляем с победой!' if lang=='ru' else 'Congratulations on your win!'}\n"
                    f"💵 +{50} | 💎 +1"
                )
                await bot.send_message(p.user_id, msg)
            except Exception:
                pass

    # Record to DB
    db.record_game_result(game.chat_id, result, player_results)

    if game.chat_id in games:
        del games[game.chat_id]


# ── START GAME ────────────────────────────────
async def start_game(bot: Bot, game: GameState):
    game.assign_roles()
    # Apply active_role boost from shop
    for uid, player in game.players.items():
        p_db = db.get_player(uid)
        if p_db and p_db["active_role"] > 0:
            from roles import RoleID as RID
            from roles import get_role_pool, ROLES, Faction
            import random
            active_roles = [r for r in RID if ROLES[r].has_night_action and r != RID.CULTIST]
            if active_roles and player.role_id == RID.CITIZEN:
                if random.random() < 0.99:
                    player.role_id = random.choice(active_roles)
            db.update_player(uid, active_role=max(0, p_db["active_role"] - 1))

    await send_role_cards(bot, game)
    await asyncio.sleep(3)
    await run_night(bot, game)
    win = game.check_win()
    if win:
        await announce_win(bot, game, win)
        return
    await run_day(bot, game)