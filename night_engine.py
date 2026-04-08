"""
Night resolution engine.
Processes all night actions in correct priority order and returns events list.
"""
from typing import TYPE_CHECKING
from roles import RoleID, Faction, ROLES

if TYPE_CHECKING:
    from game_state import GameState, Player


def resolve_night(game: "GameState") -> list[str]:
    """
    Resolves all night actions. Returns list of event strings (localized keys + args).
    Modifies game state in-place (kills players, etc.)
    Priority order:
      1. Veteran alert (kills visitors)
      2. Role blocks (Escort/Prostitute/Consort)
      3. Bodyguard protects
      4. Doctor heals
      5. Framer
      6. Forger
      7. Blackmailer
      8. Mafia kill
      9. Serial Killer kill
      10. Vigilante / Sheriff shoot
      11. Maniac kill
      12. Arsonist ignite
      13. Werewolf rampage
      14. Detective check
      15. Don check
      16. Cult conversion
      17. Spy / Lookout observe
    """
    events = []
    players = game.players

    def get_p(uid):
        return players.get(uid)

    def is_blocked(uid):
        return uid in game.night_blocks.values() or (get_p(uid) and get_p(uid).night_blocked)

    def kill_player(uid, attacker_id=None, cause="night"):
        p = get_p(uid)
        if not p or not p.is_alive:
            return False
        # Check defense
        atk_power = ROLES[get_p(attacker_id).role_id].attack_power if attacker_id else 1
        def_power = ROLES[p.role_id].defense_power

        if p.was_healed and atk_power < 3:
            return False  # Healed
        if p.was_protected and atk_power < 2:
            return False  # Bodyguard protected
        if def_power >= atk_power:
            return False  # Natural defense

        p.is_alive = False
        return True

    # 1. Veteran alert — kill all visitors
    for uid, p in players.items():
        if p.role_id == RoleID.VETERAN and p.is_alive and p.on_alert:
            p.on_alert = False
            # find anyone who targeted veteran this night
            for other_uid, other_p in players.items():
                if other_uid != uid and other_p.night_target == uid and other_p.is_alive:
                    other_p.is_alive = False
                    events.append(("veteran_killed_visitor", {"name": other_p.name, "role": other_p.role_id.value}))

    # 2. Resolve blocks
    for blocker_uid, target_uid in game.night_blocks.items():
        target = get_p(target_uid)
        if target and target.is_alive:
            # Serial killer kills blockers
            if target.role_id == RoleID.SERIAL_KILLER:
                blocker = get_p(blocker_uid)
                if blocker and blocker.is_alive:
                    blocker.is_alive = False
                    events.append(("player_died", {"name": blocker.name, "role": blocker.role_id.value}))
            else:
                target.night_blocked = True

    # 3+4. Bodyguard and Doctor
    for uid, p in players.items():
        if not p.is_alive:
            continue
        if p.role_id == RoleID.BODYGUARD and p.night_target and not p.night_blocked:
            target = get_p(p.night_target)
            if target and target.is_alive:
                target.was_protected = True
                game.night_guards[p.night_target] = uid

        if p.role_id == RoleID.DOCTOR and p.night_target and not p.night_blocked:
            target = get_p(p.night_target)
            if target and target.is_alive:
                target.was_healed = True
                game.night_heals[p.night_target] = uid

    # 5. Framer
    for uid, p in players.items():
        if p.role_id == RoleID.FRAMER and p.is_alive and p.night_target and not p.night_blocked:
            game.night_frames.add(p.night_target)

    # 6. Forger
    for uid, p in players.items():
        if p.role_id == RoleID.FORGER and p.is_alive and p.night_target and not p.night_blocked:
            target = get_p(p.night_target)
            if target and not target.is_alive:
                if p.forged_role:
                    target.role_id = p.forged_role

    # 7. Blackmailer
    for uid, p in players.items():
        if p.role_id == RoleID.BLACKMAILER and p.is_alive and p.night_target and not p.night_blocked:
            target = get_p(p.night_target)
            if target and target.is_alive:
                target.is_blackmailed = True

    # 8. Mafia kill
    if game.mafia_kill_target:
        target = get_p(game.mafia_kill_target)
        if target and target.is_alive and not target.night_blocked:
            # Check bodyguard
            if game.mafia_kill_target in game.night_guards:
                bg_uid = game.night_guards[game.mafia_kill_target]
                bg = get_p(bg_uid)
                # Bodyguard and attacker both die (attacker = mafia member who targeted)
                if bg and bg.is_alive:
                    bg.is_alive = False
                    events.append(("player_died", {"name": bg.name, "role": bg.role_id.value}))
                # Mafia member (pick first alive mafia) also dies
                for mp in game.get_mafia():
                    mp.is_alive = False
                    events.append(("player_died", {"name": mp.name, "role": mp.role_id.value}))
                    break
            else:
                killed = kill_player(game.mafia_kill_target)
                if killed:
                    events.append(("player_died", {"name": target.name, "role": target.role_id.value}))
                    # Terrorist explosion
                    if target.role_id == RoleID.TERRORIST:
                        _terrorist_explode(game, target, events)

    # 9. Serial Killer
    for uid, p in players.items():
        if p.role_id == RoleID.SERIAL_KILLER and p.is_alive and p.night_target and not p.night_blocked:
            target = get_p(p.night_target)
            if target and target.is_alive:
                killed = kill_player(p.night_target, uid)
                if killed:
                    events.append(("player_died", {"name": target.name, "role": target.role_id.value}))

    # 10. Vigilante / Sheriff
    for uid, p in players.items():
        if p.role_id in (RoleID.VIGILANTE, RoleID.SHERIFF) and p.is_alive and p.night_target and not p.night_blocked:
            target = get_p(p.night_target)
            if target and target.is_alive:
                killed = kill_player(p.night_target, uid)
                if killed:
                    events.append(("player_died", {"name": target.name, "role": target.role_id.value}))
                    if p.role_id == RoleID.VIGILANTE and target.faction.value == "town":
                        p.is_alive = False  # Vigilante dies of guilt
                        events.append(("player_died", {"name": p.name, "role": p.role_id.value}))

    # 11. Maniac
    for uid, p in players.items():
        if p.role_id == RoleID.MANIAC and p.is_alive and p.night_target and not p.night_blocked:
            target = get_p(p.night_target)
            if target and target.is_alive:
                killed = kill_player(p.night_target, uid)
                if killed:
                    events.append(("player_died", {"name": target.name, "role": target.role_id.value}))

    # 12. Arsonist ignite (only if player chose to ignite this night)
    for uid, p in players.items():
        if p.role_id == RoleID.ARSONIST and p.is_alive and not p.night_blocked:
            if p.night_target == -1:  # special signal = ignite
                burned_names = []
                for t_uid, t_p in players.items():
                    if t_p.doused and t_p.is_alive:
                        t_p.is_alive = False
                        burned_names.append(t_p.name)
                if burned_names:
                    events.append(("arsonist_burned", {"names": ", ".join(burned_names)}))
            elif p.night_target:
                target = get_p(p.night_target)
                if target:
                    target.doused = True

    # 13. Werewolf (odd nights — kills neighbors in player list)
    if game.night_number % 2 == 1:
        ww = game.get_by_role(RoleID.WEREWOLF)
        if ww and ww.is_alive and not ww.night_blocked:
            alive_list = game.get_alive()
            try:
                idx = next(i for i, p in enumerate(alive_list) if p.user_id == ww.user_id)
                neighbors_idx = [(idx - 1) % len(alive_list), (idx + 1) % len(alive_list)]
                for ni in set(neighbors_idx):
                    if ni != idx:
                        nb = alive_list[ni]
                        nb.is_alive = False
                        events.append(("player_died", {"name": nb.name, "role": nb.role_id.value}))
            except StopIteration:
                pass

    # 14. Detective check
    for uid, p in players.items():
        if p.role_id == RoleID.DETECTIVE and p.is_alive and p.night_target and not p.night_blocked:
            target = get_p(p.night_target)
            if target:
                # Store check result for sending via PM
                game.night_checks[uid] = p.night_target

    # 15. Don check (is target a detective?)
    for uid, p in players.items():
        if p.role_id == RoleID.DON and p.is_alive and p.night_target and not p.night_blocked:
            game.night_checks[uid] = p.night_target

    # 16. Cult conversion
    cult_leader = game.get_by_role(RoleID.CULT_LEADER)
    if cult_leader and cult_leader.is_alive and cult_leader.night_target and not cult_leader.night_blocked:
        target = get_p(cult_leader.night_target)
        if target and target.is_alive and target.faction.value not in ("mafia", "cult"):
            target.role_id = RoleID.CULTIST
            target.cult_converted = True

    # Reset per-night player flags
    for p in players.values():
        p.was_healed = False
        p.was_protected = False

    return events


def _terrorist_explode(game: "GameState", terrorist: "Player", events: list):
    """Terrorist explodes on kill — kills the killer and adjacent players."""
    alive_list = game.get_alive()
    try:
        idx = next(i for i, p in enumerate(alive_list) if p.user_id == terrorist.user_id)
        to_kill = set()
        if idx > 0:
            to_kill.add(alive_list[idx - 1].user_id)
        if idx < len(alive_list) - 1:
            to_kill.add(alive_list[idx + 1].user_id)
        killed_names = []
        for uid in to_kill:
            p = game.players.get(uid)
            if p and p.is_alive:
                p.is_alive = False
                killed_names.append(p.name)
        if killed_names:
            events.append(("terrorist_exploded", {"name": terrorist.name, "killed": ", ".join(killed_names)}))
    except StopIteration:
        pass
