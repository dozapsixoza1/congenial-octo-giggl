from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import random

from roles import RoleID, RoleDef, ROLES, Faction, get_role_pool


class GamePhase(Enum):
    REGISTRATION = "registration"
    NIGHT = "night"
    DAY = "day"
    VOTING = "voting"
    ENDED = "ended"


@dataclass
class Player:
    user_id: int
    name: str
    username: Optional[str]
    role_id: RoleID = RoleID.CITIZEN
    is_alive: bool = True
    last_will: str = ""
    is_revealed_mayor: bool = False
    is_blackmailed: bool = False
    is_immune_to_lynch: bool = False  # from Lawyer
    was_healed: bool = False
    was_protected: bool = False       # bodyguard
    night_target: Optional[int] = None  # user_id of target
    night_blocked: bool = False
    forged_role: Optional[RoleID] = None  # Forger overwrites this
    doused: bool = False              # Arsonist doused
    on_alert: bool = False            # Veteran alert
    has_voted: bool = False
    votes_received: int = 0
    veteran_alerts_left: int = 3
    vigilante_bullets: int = 3
    sheriff_bullets: int = 1
    angel_target: Optional[int] = None
    executioner_target: Optional[int] = None
    witch_heal_used: bool = False
    witch_kill_used: bool = False
    cult_converted: bool = False

    @property
    def role_def(self) -> RoleDef:
        return ROLES[self.role_id]

    @property
    def faction(self) -> Faction:
        return self.role_def.faction

    @property
    def mention(self) -> str:
        if self.username:
            return f"<a href='tg://user?id={self.user_id}'>{self.name}</a>"
        return f"<b>{self.name}</b>"


@dataclass
class GameState:
    chat_id: int
    creator_id: int
    lang: str = "ru"
    phase: GamePhase = GamePhase.REGISTRATION
    players: dict[int, Player] = field(default_factory=dict)  # user_id -> Player
    day_number: int = 0
    night_number: int = 0
    reg_message_id: Optional[int] = None
    vote_message_id: Optional[int] = None
    jester_winner: Optional[int] = None
    executioner_winner: Optional[int] = None
    angel_winner: Optional[int] = None
    night_events: list[str] = field(default_factory=list)

    # Night tracking
    night_kills: dict[int, int] = field(default_factory=dict)    # target -> attacker
    night_heals: dict[int, int] = field(default_factory=dict)    # target -> healer
    night_blocks: dict[int, int] = field(default_factory=dict)   # target -> blocker
    night_guards: dict[int, int] = field(default_factory=dict)   # target -> bodyguard
    night_checks: dict[int, int] = field(default_factory=dict)   # checker -> target
    night_frames: set[int] = field(default_factory=set)          # framed players
    night_forges: dict[int, RoleID] = field(default_factory=dict) # target -> fake role
    mafia_kill_target: Optional[int] = None
    mafia_votes: dict[int, int] = field(default_factory=dict)    # voter -> target

    def get_alive(self) -> list[Player]:
        return [p for p in self.players.values() if p.is_alive]

    def get_dead(self) -> list[Player]:
        return [p for p in self.players.values() if not p.is_alive]

    def get_mafia(self) -> list[Player]:
        return [p for p in self.get_alive()
                if p.faction in (Faction.MAFIA, Faction.CULT)]

    def get_town(self) -> list[Player]:
        return [p for p in self.get_alive() if p.faction == Faction.TOWN]

    def get_by_role(self, role_id: RoleID) -> Optional[Player]:
        for p in self.players.values():
            if p.role_id == role_id and p.is_alive:
                return p
        return None

    def assign_roles(self):
        pool = get_role_pool(len(self.players))
        random.shuffle(pool)
        player_list = list(self.players.values())
        random.shuffle(player_list)

        for i, player in enumerate(player_list):
            player.role_id = pool[i]

        # Assign special targets
        exec_player = self.get_by_role(RoleID.EXECUTIONER)
        angel_player = self.get_by_role(RoleID.ANGEL)
        town_players = [p for p in player_list if p.faction == Faction.TOWN
                        and p.role_id != RoleID.EXECUTIONER]

        if exec_player and town_players:
            target = random.choice(town_players)
            exec_player.executioner_target = target.user_id

        if angel_player:
            candidates = [p for p in player_list if p.user_id != angel_player.user_id]
            if candidates:
                target = random.choice(candidates)
                angel_player.angel_target = target.user_id

    def reset_night_data(self):
        self.night_kills.clear()
        self.night_heals.clear()
        self.night_blocks.clear()
        self.night_guards.clear()
        self.night_checks.clear()
        self.night_frames.clear()
        self.night_forges.clear()
        self.mafia_kill_target = None
        self.mafia_votes.clear()
        for p in self.players.values():
            p.night_target = None
            p.night_blocked = False
            p.was_healed = False
            p.was_protected = False
            p.has_voted = False
            p.votes_received = 0
            p.is_immune_to_lynch = False
            p.is_blackmailed = False

    def check_win(self) -> Optional[str]:
        alive = self.get_alive()
        if not alive:
            return "draw"

        alive_mafia = [p for p in alive if p.faction == Faction.MAFIA]
        alive_cult = [p for p in alive if p.faction == Faction.CULT]
        alive_town = [p for p in alive if p.faction == Faction.TOWN]
        alive_sk = [p for p in alive if p.role_id == RoleID.SERIAL_KILLER]
        alive_maniac = [p for p in alive if p.role_id == RoleID.MANIAC]
        alive_arsonist = [p for p in alive if p.role_id == RoleID.ARSONIST]
        alive_werewolf = [p for p in alive if p.role_id == RoleID.WEREWOLF]

        total = len(alive)
        evil = len(alive_mafia) + len(alive_sk) + len(alive_maniac) + len(alive_arsonist) + len(alive_werewolf)

        # Cult win
        if alive_cult and not alive_mafia and len(alive_cult) >= len(alive_town):
            return "cult"

        # Mafia win: mafia >= all non-mafia
        if alive_mafia and len(alive_mafia) >= (total - len(alive_mafia)):
            return "mafia"

        # Neutral solo wins
        if len(alive) == 1:
            p = alive[0]
            if p.role_id == RoleID.SERIAL_KILLER:
                return "serial_killer"
            if p.role_id == RoleID.MANIAC:
                return "maniac"
            if p.role_id == RoleID.ARSONIST:
                return "arsonist"
            if p.role_id == RoleID.WEREWOLF:
                return "werewolf"

        # Town win: no mafia and no threatening neutrals
        if not alive_mafia and not alive_cult and evil == 0:
            return "town"

        return None


# Global storage: chat_id -> GameState
games: dict[int, GameState] = {}

# Per-user language preference
user_langs: dict[int, str] = {}
