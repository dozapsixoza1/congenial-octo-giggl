from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class Faction(Enum):
    TOWN = "town"
    MAFIA = "mafia"
    NEUTRAL = "neutral"
    CULT = "cult"


class RoleID(Enum):
    # Town
    CITIZEN = "citizen"
    DETECTIVE = "detective"
    SHERIFF = "sheriff"
    DOCTOR = "doctor"
    BODYGUARD = "bodyguard"
    VIGILANTE = "vigilante"
    JOURNALIST = "journalist"
    MAYOR = "mayor"
    LAWYER = "lawyer"
    BOMB = "bomb"
    SPY = "spy"
    VETERAN = "veteran"
    ESCORT = "escort"
    LOOKOUT = "lookout"
    ANGEL = "angel"
    TERRORIST = "terrorist"

    # Mafia
    MAFIA = "mafia"
    DON = "don"
    GODFATHER = "godfather"
    CONSORT = "consort"
    FRAMER = "framer"
    BLACKMAILER = "blackmailer"
    DISGUISER = "disguiser"
    FORGER = "forger"

    # Neutral
    MANIAC = "maniac"
    PROSTITUTE = "prostitute"
    WITCH = "witch"
    JESTER = "jester"
    EXECUTIONER = "executioner"
    SERIAL_KILLER = "serial_killer"
    ARSONIST = "arsonist"
    WEREWOLF = "werewolf"

    # Cult
    CULT_LEADER = "cult_leader"
    CULTIST = "cultist"


@dataclass
class RoleDef:
    role_id: RoleID
    faction: Faction
    has_night_action: bool = False
    attack_power: int = 0       # 0=none,1=basic,2=powerful,3=unstoppable
    defense_power: int = 0      # 0=none,1=basic,2=powerful,3=invincible
    is_unique: bool = False     # only 1 per game
    mafia_knows: bool = False   # other mafia members see this role
    appears_innocent: bool = False  # looks innocent to detective


ROLES: dict[RoleID, RoleDef] = {
    # ── TOWN ──────────────────────────────────────────────
    RoleID.CITIZEN:     RoleDef(RoleID.CITIZEN,     Faction.TOWN),
    RoleID.DETECTIVE:   RoleDef(RoleID.DETECTIVE,   Faction.TOWN,  has_night_action=True, is_unique=True),
    RoleID.SHERIFF:     RoleDef(RoleID.SHERIFF,     Faction.TOWN,  has_night_action=True, attack_power=1, is_unique=True),
    RoleID.DOCTOR:      RoleDef(RoleID.DOCTOR,      Faction.TOWN,  has_night_action=True, is_unique=True),
    RoleID.BODYGUARD:   RoleDef(RoleID.BODYGUARD,   Faction.TOWN,  has_night_action=True, attack_power=2, defense_power=1),
    RoleID.VIGILANTE:   RoleDef(RoleID.VIGILANTE,   Faction.TOWN,  has_night_action=True, attack_power=1),
    RoleID.JOURNALIST:  RoleDef(RoleID.JOURNALIST,  Faction.TOWN,  has_night_action=True, is_unique=True),
    RoleID.MAYOR:       RoleDef(RoleID.MAYOR,       Faction.TOWN,  is_unique=True),
    RoleID.LAWYER:      RoleDef(RoleID.LAWYER,      Faction.TOWN,  has_night_action=True),
    RoleID.BOMB:        RoleDef(RoleID.BOMB,        Faction.TOWN,  attack_power=2, is_unique=True),
    RoleID.SPY:         RoleDef(RoleID.SPY,         Faction.TOWN,  has_night_action=True, is_unique=True),
    RoleID.VETERAN:     RoleDef(RoleID.VETERAN,     Faction.TOWN,  has_night_action=True, attack_power=2, is_unique=True),
    RoleID.ESCORT:      RoleDef(RoleID.ESCORT,      Faction.TOWN,  has_night_action=True),
    RoleID.LOOKOUT:     RoleDef(RoleID.LOOKOUT,     Faction.TOWN,  has_night_action=True),
    RoleID.ANGEL:       RoleDef(RoleID.ANGEL,       Faction.TOWN,  has_night_action=True, is_unique=True),
    RoleID.TERRORIST:   RoleDef(RoleID.TERRORIST,   Faction.TOWN,  attack_power=2, is_unique=True),

    # ── MAFIA ─────────────────────────────────────────────
    RoleID.MAFIA:       RoleDef(RoleID.MAFIA,       Faction.MAFIA, has_night_action=True, attack_power=1, mafia_knows=True),
    RoleID.DON:         RoleDef(RoleID.DON,         Faction.MAFIA, has_night_action=True, attack_power=1, is_unique=True, mafia_knows=True, appears_innocent=True),
    RoleID.GODFATHER:   RoleDef(RoleID.GODFATHER,   Faction.MAFIA, has_night_action=True, attack_power=1, defense_power=1, is_unique=True, mafia_knows=True, appears_innocent=True),
    RoleID.CONSORT:     RoleDef(RoleID.CONSORT,     Faction.MAFIA, has_night_action=True, mafia_knows=True),
    RoleID.FRAMER:      RoleDef(RoleID.FRAMER,      Faction.MAFIA, has_night_action=True, mafia_knows=True),
    RoleID.BLACKMAILER: RoleDef(RoleID.BLACKMAILER, Faction.MAFIA, has_night_action=True, mafia_knows=True),
    RoleID.DISGUISER:   RoleDef(RoleID.DISGUISER,   Faction.MAFIA, has_night_action=True, mafia_knows=True),
    RoleID.FORGER:      RoleDef(RoleID.FORGER,      Faction.MAFIA, has_night_action=True, mafia_knows=True),

    # ── NEUTRAL ───────────────────────────────────────────
    RoleID.MANIAC:       RoleDef(RoleID.MANIAC,       Faction.NEUTRAL, has_night_action=True, attack_power=1, is_unique=True),
    RoleID.PROSTITUTE:   RoleDef(RoleID.PROSTITUTE,   Faction.NEUTRAL, has_night_action=True, is_unique=True),
    RoleID.WITCH:        RoleDef(RoleID.WITCH,         Faction.NEUTRAL, has_night_action=True, is_unique=True),
    RoleID.JESTER:       RoleDef(RoleID.JESTER,        Faction.NEUTRAL, is_unique=True),
    RoleID.EXECUTIONER:  RoleDef(RoleID.EXECUTIONER,   Faction.NEUTRAL, is_unique=True),
    RoleID.SERIAL_KILLER:RoleDef(RoleID.SERIAL_KILLER, Faction.NEUTRAL, has_night_action=True, attack_power=2, defense_power=1, is_unique=True),
    RoleID.ARSONIST:     RoleDef(RoleID.ARSONIST,      Faction.NEUTRAL, has_night_action=True, attack_power=3, defense_power=1, is_unique=True),
    RoleID.WEREWOLF:     RoleDef(RoleID.WEREWOLF,      Faction.NEUTRAL, has_night_action=True, attack_power=2, defense_power=2, is_unique=True),

    # ── CULT ──────────────────────────────────────────────
    RoleID.CULT_LEADER:  RoleDef(RoleID.CULT_LEADER,   Faction.CULT, has_night_action=True, is_unique=True),
    RoleID.CULTIST:      RoleDef(RoleID.CULTIST,        Faction.CULT),
}


# Role pools for auto-assignment based on player count
def get_role_pool(player_count: int) -> list[RoleID]:
    """Returns a balanced list of roles for the given player count."""
    pool = []

    if player_count <= 5:
        pool = [
            RoleID.DON, RoleID.MAFIA,
            RoleID.DETECTIVE, RoleID.DOCTOR,
            RoleID.CITIZEN,
        ]
    elif player_count <= 7:
        pool = [
            RoleID.GODFATHER, RoleID.MAFIA,
            RoleID.DETECTIVE, RoleID.DOCTOR, RoleID.SHERIFF,
            RoleID.CITIZEN, RoleID.CITIZEN,
        ]
    elif player_count <= 9:
        pool = [
            RoleID.GODFATHER, RoleID.DON, RoleID.MAFIA,
            RoleID.DETECTIVE, RoleID.DOCTOR, RoleID.BODYGUARD,
            RoleID.VIGILANTE, RoleID.CITIZEN, RoleID.JESTER,
        ]
    elif player_count <= 11:
        pool = [
            RoleID.GODFATHER, RoleID.DON, RoleID.MAFIA, RoleID.CONSORT,
            RoleID.DETECTIVE, RoleID.DOCTOR, RoleID.SHERIFF, RoleID.BODYGUARD,
            RoleID.VIGILANTE, RoleID.CITIZEN, RoleID.MANIAC,
        ]
    elif player_count <= 13:
        pool = [
            RoleID.GODFATHER, RoleID.DON, RoleID.MAFIA, RoleID.FRAMER,
            RoleID.DETECTIVE, RoleID.DOCTOR, RoleID.SHERIFF, RoleID.SPY,
            RoleID.BODYGUARD, RoleID.VIGILANTE, RoleID.MAYOR,
            RoleID.CITIZEN, RoleID.JESTER,
        ]
    elif player_count <= 15:
        pool = [
            RoleID.GODFATHER, RoleID.DON, RoleID.MAFIA, RoleID.CONSORT, RoleID.BLACKMAILER,
            RoleID.DETECTIVE, RoleID.DOCTOR, RoleID.SHERIFF, RoleID.SPY,
            RoleID.BODYGUARD, RoleID.VIGILANTE, RoleID.MAYOR, RoleID.ESCORT,
            RoleID.CITIZEN, RoleID.MANIAC,
        ]
    else:  # 16-20
        pool = [
            RoleID.GODFATHER, RoleID.DON, RoleID.MAFIA, RoleID.CONSORT,
            RoleID.BLACKMAILER, RoleID.FRAMER, RoleID.DISGUISER,
            RoleID.DETECTIVE, RoleID.DOCTOR, RoleID.SHERIFF, RoleID.SPY,
            RoleID.BODYGUARD, RoleID.VIGILANTE, RoleID.MAYOR, RoleID.ESCORT,
            RoleID.LOOKOUT, RoleID.BOMB, RoleID.VETERAN,
            RoleID.JESTER, RoleID.SERIAL_KILLER,
        ]

    # Pad with citizens if needed
    while len(pool) < player_count:
        pool.append(RoleID.CITIZEN)

    return pool[:player_count]