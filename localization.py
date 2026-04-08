STRINGS = {
    "ru": {
        # General
        "bot_name": "🤵 HarshMafia",
        "lang_set": "🌐 Язык установлен: Русский",
        "only_group": "❌ Бот работает только в групповых чатах!",
        "no_game": "❌ Нет активной игры. Начни с /game",
        "game_exists": "⚠️ Игра уже идёт!",
        "not_in_game": "❌ Ты не участник этой игры.",
        "already_joined": "⚠️ Ты уже в игре!",
        "game_full": "❌ Игра заполнена (макс. {max}).",
        "not_enough": "❌ Недостаточно игроков (мин. {min}).",
        "you_are_dead": "💀 Ты мёртв и не можешь совершать действия.",
        "not_your_turn": "⏳ Сейчас не твоя очередь.",
        "target_dead": "❌ Этот игрок уже мёртв.",
        "target_self": "❌ Нельзя выбрать себя.",

        # Registration
        "game_created": "🎰 <b>HarshMafia</b> — регистрация открыта!\n\nНажми кнопку чтобы вступить.\nИгроков: <b>{count}/{max}</b>\n\nВремя: {time} сек.",
        "joined": "✅ <b>{name}</b> вступил в игру! [{count}/{max}]",
        "left_game": "🚪 <b>{name}</b> вышел из игры. [{count}/{max}]",
        "join_btn": "🙋 Вступить",
        "leave_btn": "🚪 Выйти",
        "start_btn": "▶️ Начать игру",
        "reg_closed": "🔒 Регистрация закрыта.",
        "not_creator": "❌ Только создатель игры может начать.",

        # Roles
        "your_role": "🎭 Твоя роль: <b>{role}</b>\n\n{desc}",
        "role_mafia": "Мафия",
        "role_don": "Дон Мафии",
        "role_godfather": "Крёстный Отец",
        "role_citizen": "Мирный житель",
        "role_detective": "Детектив",
        "role_sheriff": "Шериф",
        "role_doctor": "Доктор",
        "role_maniac": "Маньяк",
        "role_prostitute": "Путана",
        "role_bodyguard": "Телохранитель",
        "role_vigilante": "Страж",
        "role_journalist": "Журналист",
        "role_mayor": "Мэр",
        "role_lawyer": "Адвокат",
        "role_bomb": "Бомба",
        "role_spy": "Шпион",
        "role_terrorist": "Террорист",
        "role_angel": "Ангел",
        "role_witch": "Ведьма",
        "role_jester": "Шут",
        "role_executioner": "Палач",
        "role_veteran": "Ветеран",
        "role_escort": "Эскорт",
        "role_lookout": "Наблюдатель",
        "role_forger": "Фальсификатор",
        "role_framer": "Подставщик",
        "role_blackmailer": "Шантажист",
        "role_consort": "Консорт",
        "role_disguiser": "Маскировщик",
        "role_serial_killer": "Серийный убийца",
        "role_arsonist": "Поджигатель",
        "role_werewolf": "Оборотень",
        "role_cult_leader": "Лидер культа",

        # Role descriptions
        "desc_mafia": "🔫 Ты член Мафии. Каждую ночь вместе с командой выбираешь жертву для убийства. Победа — уничтожить всех мирных.",
        "desc_don": "👑 Ты Дон Мафии. Руководишь мафией, каждую ночь можешь проверить — является ли игрок детективом. Неуязвим для обычной проверки детектива.",
        "desc_godfather": "🎩 Крёстный Отец. Выглядишь мирным при проверке детектива. Руководишь убийствами мафии.",
        "desc_citizen": "👤 Мирный житель. У тебя нет особых способностей, но твой голос важен. Найди мафию и линчуй её!",
        "desc_detective": "🔍 Детектив. Каждую ночь проверяешь одного игрока — узнаёшь его фракцию (мафия/мирный).",
        "desc_sheriff": "⭐ Шериф. Каждую ночь можешь застрелить подозреваемого. Если промахнёшься по мирному — теряешь выстрел.",
        "desc_doctor": "💊 Доктор. Каждую ночь лечишь одного игрока, защищая от убийства. Нельзя лечить себя 2 ночи подряд.",
        "desc_maniac": "🔪 Маньяк. Одиночка. Каждую ночь убиваешь одного игрока. Победа — остаться последним.",
        "desc_prostitute": "💋 Путана. Каждую ночь блокируешь действие одного игрока. Если зайдёшь к мафии — можешь погибнуть.",
        "desc_bodyguard": "🛡 Телохранитель. Защищаешь игрока ночью. Если нападут — погибаете оба с нападавшим.",
        "desc_vigilante": "🔫 Страж. Мирный с пистолетом. 3 пули. Можешь застрелить ночью кого угодно, но если убьёшь мирного — умрёшь от вины.",
        "desc_journalist": "📰 Журналист. Каждую ночь можешь публично раскрыть роль одного мёртвого игрока или подслушать разговор мафии.",
        "desc_mayor": "🏛 Мэр. Твой голос на линчевании считается за 3. Можешь публично раскрыть свою роль — после этого голос x3 виден всем.",
        "desc_lawyer": "⚖️ Адвокат. Каждую ночь защищаешь игрока от линчевания на следующий день (иммунитет к голосованию).",
        "desc_bomb": "💣 Бомба. Если тебя линчуют — взрываешься и убиваешь всех, кто голосовал за тебя.",
        "desc_spy": "🕵️ Шпион. Каждую ночь видишь, кто посещал кого (список визитов без раскрытия ролей).",
        "desc_terrorist": "💥 Террорист. Если тебя убьют ночью — взрываешься и убиваешь убийцу и его соседей.",
        "desc_angel": "😇 Ангел. Выбираешь одного игрока в начале игры. Если он выживет до конца — ты побеждаешь вместе с ним.",
        "desc_witch": "🧙 Ведьма. 2 зелья: лечения и смерти. Одно использование каждого. Можешь видеть цель мафии.",
        "desc_jester": "🤡 Шут. Твоя цель — быть линчеванным. Если тебя линчуют — ты побеждаешь, игра продолжается.",
        "desc_executioner": "🪓 Палач. В начале игры получаешь цель. Заставь её быть линчеванной — и победишь.",
        "desc_veteran": "🎖 Ветеран. 3 ночи можешь уйти в «режим боевой готовности» — все, кто посетят тебя этой ночью, погибнут.",
        "desc_escort": "💃 Эскорт. Блокируешь действие одного игрока ночью. Мирная сторона.",
        "desc_lookout": "👁 Наблюдатель. Следишь за одним игроком ночью — видишь всех, кто его посещал.",
        "desc_forger": "📝 Фальсификатор. Подделываешь роль мёртвого игрока — при вскрытии будет показана другая роль.",
        "desc_framer": "🖼 Подставщик. Делаешь игрока «виновным» — детектив увидит его как мафию.",
        "desc_blackmailer": "📧 Шантажист. Запрещаешь игроку говорить в чате следующий день.",
        "desc_consort": "🎭 Консорт. Мафийный эскорт. Блокирует мирного игрока ночью.",
        "desc_disguiser": "🎭 Маскировщик. Принимаешь личность другого игрока — при смерти будет казаться, что умер тот игрок.",
        "desc_serial_killer": "🗡 Серийный убийца. Убиваешь каждую ночь. Неуязвим для путаны/эскорта (убиваешь их при визите).",
        "desc_arsonist": "🔥 Поджигатель. Ночью обливаешь игрока бензином. В выбранную ночь поджигаешь всех облитых сразу.",
        "desc_werewolf": "🐺 Оборотень. В нечётные ночи убиваешь всех соседей по списку игроков. Неуязвим ночью.",
        "desc_cult_leader": "🌀 Лидер культа. Каждую ночь обращаешь одного игрока в культ (меняешь его роль на «Культист»).",

        # Day phase
        "day_start": "☀️ <b>День {day}</b>\n\n{events}\n\nОбсуждайте и голосуйте за подозреваемого!\nВремя: {time} сек.",
        "nobody_died": "Этой ночью никто не погиб.",
        "player_died": "💀 <b>{name}</b> ({role}) был убит ночью.",
        "player_died_unknown": "💀 <b>{name}</b> был убит ночью. Роль неизвестна.",
        "vote_start": "🗳 <b>Голосование!</b>\nВыберите кого линчевать или нажмите «Пропустить».",
        "vote_btn": "👆 {name} [{votes}]",
        "skip_btn": "⏭ Пропустить [{votes}]",
        "voted": "✅ {voter} проголосовал за {target}",
        "vote_skip": "✅ {voter} проголосовал за пропуск",
        "already_voted": "⚠️ Ты уже проголосовал!",
        "lynched": "⚖️ <b>{name}</b> ({role}) был линчеван!",
        "no_lynch": "⚖️ Город решил никого не линчевать.",
        "last_will": "📜 Последняя воля <b>{name}</b>:\n<i>{will}</i>",
        "no_last_will": "📜 <b>{name}</b> не оставил последней воли.",

        # Night phase
        "night_start": "🌙 <b>Ночь {night}</b>\n\nГород засыпает... Проверьте личные сообщения от бота!",
        "night_action_prompt": "🌙 Ночь {night}. Выбери цель:",
        "night_skip_btn": "⏭ Пропустить ход",
        "night_action_done": "✅ Действие записано.",
        "night_no_action": "😴 У тебя нет ночного действия.",
        "mafia_chat": "🔫 <b>Чат мафии:</b>\nУчастники: {members}\nВыберите жертву:",

        # Veterans
        "veteran_alert_on": "🎖 Ты в режиме боевой готовности! Все визитёры погибнут.",
        "veteran_alert_off": "😴 Ты решил отдохнуть этой ночью.",
        "veteran_killed_visitor": "💀 Ветеран убил <b>{name}</b> ({role}), который посетил его!",

        # Arsonist
        "arsonist_doused": "🛢 Ты облил <b>{name}</b> бензином.",
        "arsonist_ignite": "🔥 Поджечь всех облитых!",
        "arsonist_burned": "🔥 Поджигатель поджёг: {names}",

        # Witch
        "witch_see_target": "🧙 Мафия этой ночью идёт к: <b>{name}</b>",
        "witch_heal_btn": "💚 Зелье лечения",
        "witch_kill_btn": "💀 Зелье смерти",

        # Jester / Executioner
        "jester_win": "🤡 <b>{name}</b> — Шут был линчеван и победил! Игра продолжается.",
        "executioner_target": "🪓 Твоя цель: <b>{name}</b>. Заставь его быть линчеванным!",
        "executioner_win": "🪓 <b>{name}</b> — Палач добился линчевания своей цели и победил!",
        "executioner_becomes_jester": "🤡 Цель Палача погибла. Теперь он — Шут.",

        # Mayor
        "mayor_reveal": "🏛 <b>{name}</b> раскрылся как Мэр! Его голос теперь считается за 3.",

        # Blackmailer
        "blackmailed": "📧 Ты под шантажом! Не можешь говорить сегодня.",
        "blackmail_blocked": "🔇 Сообщение удалено — ты под шантажом.",

        # Bomb
        "bomb_exploded": "💣 <b>{name}</b> оказался Бомбой! Взрыв убил: {killed}",

        # Terrorist
        "terrorist_exploded": "💥 <b>{name}</b> оказался Террористом! Взрыв при убийстве уничтожил: {killed}",

        # Cult
        "cult_converted": "🌀 Ты обращён в культ! Теперь ты Культист и помогаешь Лидеру.",
        "cult_win": "🌀 Культ захватил власть! Победили: {members}",

        # Win conditions
        "mafia_win": "🔫 <b>Мафия победила!</b>\nМафия: {members}",
        "town_win": "🏙 <b>Город победил!</b>\nВыжившие: {members}",
        "maniac_win": "🔪 <b>Маньяк победил!</b>",
        "jester_win_end": "🤡 <b>Шут победил!</b>",
        "draw": "🤝 <b>Ничья!</b> Все погибли.",
        "werewolf_win": "🐺 <b>Оборотень победил!</b>",

        # Spy
        "spy_report": "🕵️ Ночные визиты:\n{visits}",
        "spy_no_visits": "Никто никого не посещал.",

        # Lookout
        "lookout_report": "👁 К <b>{target}</b> приходили: {visitors}",
        "lookout_nobody": "👁 К <b>{target}</b> никто не приходил.",

        # Journalist
        "journalist_reveal": "📰 Журналист раскрывает: <b>{name}</b> был <b>{role}</b>.",
        "journalist_mafia_chat": "📰 Журналист подслушал: мафия говорила о <b>{target}</b>.",

        # Last will
        "write_lastwill": "✍️ Напиши свою последнюю волю (до 200 символов).\nОна будет показана после смерти.",
        "lastwill_saved": "📜 Последняя воля сохранена.",
        "lastwill_toolong": "❌ Слишком длинно! Максимум 200 символов.",

        # Admin commands
        "game_cancelled": "❌ Игра отменена администратором.",
        "player_kicked": "👢 <b>{name}</b> выгнан из игры.",

        # Language
        "choose_lang": "🌐 Выбери язык / Choose language:",
        "lang_ru_btn": "🇷🇺 Русский",
        "lang_en_btn": "🇬🇧 English",

        # Players list
        "players_list": "👥 <b>Игроки ({count}):</b>\n{players}",
        "alive_list": "💚 <b>Живые ({count}):</b>\n{players}",
        "dead_list": "💀 <b>Мёртвые ({count}):</b>\n{players}",
    },

    "en": {
        "bot_name": "🤵 HarshMafia",
        "lang_set": "🌐 Language set: English",
        "only_group": "❌ This bot only works in group chats!",
        "no_game": "❌ No active game. Start with /game",
        "game_exists": "⚠️ A game is already running!",
        "not_in_game": "❌ You are not a participant in this game.",
        "already_joined": "⚠️ You already joined!",
        "game_full": "❌ Game is full (max {max}).",
        "not_enough": "❌ Not enough players (min {min}).",
        "you_are_dead": "💀 You are dead and cannot take actions.",
        "not_your_turn": "⏳ It's not your turn.",
        "target_dead": "❌ That player is already dead.",
        "target_self": "❌ You cannot target yourself.",

        "game_created": "🎰 <b>HarshMafia</b> — registration is open!\n\nPress the button to join.\nPlayers: <b>{count}/{max}</b>\n\nTime: {time} sec.",
        "joined": "✅ <b>{name}</b> joined the game! [{count}/{max}]",
        "left_game": "🚪 <b>{name}</b> left the game. [{count}/{max}]",
        "join_btn": "🙋 Join",
        "leave_btn": "🚪 Leave",
        "start_btn": "▶️ Start game",
        "reg_closed": "🔒 Registration closed.",
        "not_creator": "❌ Only the game creator can start.",

        "your_role": "🎭 Your role: <b>{role}</b>\n\n{desc}",
        "role_mafia": "Mafia",
        "role_don": "Mafia Don",
        "role_godfather": "Godfather",
        "role_citizen": "Citizen",
        "role_detective": "Detective",
        "role_sheriff": "Sheriff",
        "role_doctor": "Doctor",
        "role_maniac": "Maniac",
        "role_prostitute": "Escort",
        "role_bodyguard": "Bodyguard",
        "role_vigilante": "Vigilante",
        "role_journalist": "Journalist",
        "role_mayor": "Mayor",
        "role_lawyer": "Lawyer",
        "role_bomb": "Bomb",
        "role_spy": "Spy",
        "role_terrorist": "Terrorist",
        "role_angel": "Guardian Angel",
        "role_witch": "Witch",
        "role_jester": "Jester",
        "role_executioner": "Executioner",
        "role_veteran": "Veteran",
        "role_escort": "Escort",
        "role_lookout": "Lookout",
        "role_forger": "Forger",
        "role_framer": "Framer",
        "role_blackmailer": "Blackmailer",
        "role_consort": "Consort",
        "role_disguiser": "Disguiser",
        "role_serial_killer": "Serial Killer",
        "role_arsonist": "Arsonist",
        "role_werewolf": "Werewolf",
        "role_cult_leader": "Cult Leader",

        "desc_mafia": "🔫 You are Mafia. Each night, choose a victim with your team. Win by eliminating all town.",
        "desc_don": "👑 You are the Mafia Don. You lead the mafia and can check if a player is a Detective each night. You appear innocent to the Detective.",
        "desc_godfather": "🎩 Godfather. You appear innocent to the Detective. You direct mafia kills.",
        "desc_citizen": "👤 Citizen. No special ability, but your vote matters. Find the mafia and lynch them!",
        "desc_detective": "🔍 Detective. Each night, check one player to learn their faction (mafia/town).",
        "desc_sheriff": "⭐ Sheriff. Each night you may shoot a suspect. If you shoot a townie — you lose a bullet.",
        "desc_doctor": "💊 Doctor. Each night heal one player, protecting them from death. Cannot heal yourself two nights in a row.",
        "desc_maniac": "🔪 Maniac. Lone killer. Kill one player each night. Win by being the last one standing.",
        "desc_prostitute": "💋 Escort. Each night block one player's action. If you visit mafia — you may die.",
        "desc_bodyguard": "🛡 Bodyguard. Protect a player at night. If they are attacked — you both die with the attacker.",
        "desc_vigilante": "🔫 Vigilante. Town with a gun. 3 bullets. Shoot anyone at night, but if you kill a townie — you die of guilt.",
        "desc_journalist": "📰 Journalist. Each night reveal a dead player's role publicly or eavesdrop on the mafia chat.",
        "desc_mayor": "🏛 Mayor. Your lynch vote counts as 3. Reveal yourself publicly to make your triple vote visible.",
        "desc_lawyer": "⚖️ Lawyer. Each night grant a player immunity from the next day's lynch vote.",
        "desc_bomb": "💣 Bomb. If you are lynched — you explode, killing everyone who voted for you.",
        "desc_spy": "🕵️ Spy. Each night see who visited whom (list of visits without roles revealed).",
        "desc_terrorist": "💥 Terrorist. If killed at night — you explode, killing your killer and their neighbors.",
        "desc_angel": "😇 Guardian Angel. Choose one player at game start. If they survive to the end — you win with them.",
        "desc_witch": "🧙 Witch. 2 potions: healing and death. One use each. You can see the mafia's target.",
        "desc_jester": "🤡 Jester. Your goal is to be lynched. If you are lynched — you win and the game continues.",
        "desc_executioner": "🪓 Executioner. You receive a target at game start. Get them lynched to win.",
        "desc_veteran": "🎖 Veteran. 3 times you may go on alert — all visitors that night will die.",
        "desc_escort": "💃 Escort. Block one player's night action. Town-aligned.",
        "desc_lookout": "👁 Lookout. Watch one player at night — see everyone who visits them.",
        "desc_forger": "📝 Forger. Forge a dead player's role — a different role is shown on reveal.",
        "desc_framer": "🖼 Framer. Frame a player as guilty — the Detective will see them as mafia.",
        "desc_blackmailer": "📧 Blackmailer. Prevent a player from speaking in chat the next day.",
        "desc_consort": "🎭 Consort. Mafia escort. Blocks a town player at night.",
        "desc_disguiser": "🎭 Disguiser. Take another player's identity — when you die, it appears they died.",
        "desc_serial_killer": "🗡 Serial Killer. Kill every night. Immune to escorts (you kill them if they visit).",
        "desc_arsonist": "🔥 Arsonist. Each night douse a player in gasoline. On your chosen night, ignite all doused players at once.",
        "desc_werewolf": "🐺 Werewolf. On odd nights, kill all neighbors in the player list. Immune at night.",
        "desc_cult_leader": "🌀 Cult Leader. Each night convert one player to the cult (change their role to Cultist).",

        "day_start": "☀️ <b>Day {day}</b>\n\n{events}\n\nDiscuss and vote to lynch a suspect!\nTime: {time} sec.",
        "nobody_died": "Nobody died last night.",
        "player_died": "💀 <b>{name}</b> ({role}) was killed last night.",
        "player_died_unknown": "💀 <b>{name}</b> was killed last night. Role unknown.",
        "vote_start": "🗳 <b>Vote!</b>\nChoose who to lynch or press 'Skip'.",
        "vote_btn": "👆 {name} [{votes}]",
        "skip_btn": "⏭ Skip [{votes}]",
        "voted": "✅ {voter} voted for {target}",
        "vote_skip": "✅ {voter} voted to skip",
        "already_voted": "⚠️ You already voted!",
        "lynched": "⚖️ <b>{name}</b> ({role}) was lynched!",
        "no_lynch": "⚖️ The town decided not to lynch anyone.",
        "last_will": "📜 Last will of <b>{name}</b>:\n<i>{will}</i>",
        "no_last_will": "📜 <b>{name}</b> left no last will.",

        "night_start": "🌙 <b>Night {night}</b>\n\nThe town falls asleep... Check your private messages from the bot!",
        "night_action_prompt": "🌙 Night {night}. Choose your target:",
        "night_skip_btn": "⏭ Skip action",
        "night_action_done": "✅ Action recorded.",
        "night_no_action": "😴 You have no night action.",
        "mafia_chat": "🔫 <b>Mafia chat:</b>\nMembers: {members}\nChoose a victim:",

        "veteran_alert_on": "🎖 You are on high alert! All visitors will die.",
        "veteran_alert_off": "😴 You decided to rest tonight.",
        "veteran_killed_visitor": "💀 The Veteran killed <b>{name}</b> ({role}) who visited him!",

        "arsonist_doused": "🛢 You doused <b>{name}</b> in gasoline.",
        "arsonist_ignite": "🔥 Ignite all doused targets!",
        "arsonist_burned": "🔥 The Arsonist ignited: {names}",

        "witch_see_target": "🧙 The mafia is going to: <b>{name}</b> tonight.",
        "witch_heal_btn": "💚 Healing potion",
        "witch_kill_btn": "💀 Death potion",

        "jester_win": "🤡 <b>{name}</b> — The Jester was lynched and wins! Game continues.",
        "executioner_target": "🪓 Your target: <b>{name}</b>. Get them lynched!",
        "executioner_win": "🪓 <b>{name}</b> — The Executioner got their target lynched and wins!",
        "executioner_becomes_jester": "🤡 Executioner's target died. They are now a Jester.",

        "mayor_reveal": "🏛 <b>{name}</b> revealed as Mayor! Their vote now counts as 3.",

        "blackmailed": "📧 You are blackmailed! You cannot speak today.",
        "blackmail_blocked": "🔇 Message deleted — you are blackmailed.",

        "bomb_exploded": "💣 <b>{name}</b> was a Bomb! The explosion killed: {killed}",
        "terrorist_exploded": "💥 <b>{name}</b> was a Terrorist! The explosion killed: {killed}",

        "cult_converted": "🌀 You have been converted to the cult! You are now a Cultist.",
        "cult_win": "🌀 The Cult took over! Winners: {members}",

        "mafia_win": "🔫 <b>Mafia wins!</b>\nMafia: {members}",
        "town_win": "🏙 <b>Town wins!</b>\nSurvivors: {members}",
        "maniac_win": "🔪 <b>The Maniac wins!</b>",
        "jester_win_end": "🤡 <b>The Jester wins!</b>",
        "draw": "🤝 <b>Draw!</b> Everyone died.",
        "werewolf_win": "🐺 <b>The Werewolf wins!</b>",

        "spy_report": "🕵️ Night visits:\n{visits}",
        "spy_no_visits": "Nobody visited anyone.",

        "lookout_report": "👁 Visitors to <b>{target}</b>: {visitors}",
        "lookout_nobody": "👁 Nobody visited <b>{target}</b>.",

        "journalist_reveal": "📰 Journalist reveals: <b>{name}</b> was <b>{role}</b>.",
        "journalist_mafia_chat": "📰 Journalist eavesdropped: mafia was talking about <b>{target}</b>.",

        "write_lastwill": "✍️ Write your last will (max 200 chars).\nIt will be shown after your death.",
        "lastwill_saved": "📜 Last will saved.",
        "lastwill_toolong": "❌ Too long! Maximum 200 characters.",

        "game_cancelled": "❌ Game cancelled by admin.",
        "player_kicked": "👢 <b>{name}</b> was kicked from the game.",

        "choose_lang": "🌐 Выбери язык / Choose language:",
        "lang_ru_btn": "🇷🇺 Русский",
        "lang_en_btn": "🇬🇧 English",

        "players_list": "👥 <b>Players ({count}):</b>\n{players}",
        "alive_list": "💚 <b>Alive ({count}):</b>\n{players}",
        "dead_list": "💀 <b>Dead ({count}):</b>\n{players}",
    }
}


def t(lang: str, key: str, **kwargs) -> str:
    text = STRINGS.get(lang, STRINGS["ru"]).get(key, STRINGS["ru"].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
