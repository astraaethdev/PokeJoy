"""
Sistema de banco de dados SQLite para o Bot Pokémon — MUNDO VIVO RPG
"""
import aiosqlite
import json
import os
import asyncio
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "pokemon_bot.db")

class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self._lock = asyncio.Lock()

    async def init(self):
        """Inicializa o banco de dados com todas as tabelas"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        async with aiosqlite.connect(self.db_path) as db:
            # Tabela de treinadores
            await db.execute("""
                CREATE TABLE IF NOT EXISTS trainers (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    display_name TEXT,
                    level INTEGER DEFAULT 1,
                    xp INTEGER DEFAULT 0,
                    coins INTEGER DEFAULT 1000,
                    rank TEXT DEFAULT 'Novato',
                    specialization TEXT,
                    titles TEXT DEFAULT '[]',
                    stats TEXT DEFAULT '{}',
                    created_at TEXT,
                    last_daily TEXT,
                    total_catches INTEGER DEFAULT 0,
                    total_battles INTEGER DEFAULT 0,
                    total_wins INTEGER DEFAULT 0,
                    streak INTEGER DEFAULT 0,
                    last_message TEXT,
                    current_region TEXT DEFAULT 'verdalia',
                    current_area TEXT DEFAULT 'bosque_esmeralda',
                    unlocked_regions TEXT DEFAULT '["verdalia","lumina"]',
                    badges TEXT DEFAULT '[]',
                    current_chapter TEXT DEFAULT 'capitulo_1',
                    completed_chapters TEXT DEFAULT '[]',
                    friendship_points TEXT DEFAULT '{}',
                    diary_entries TEXT DEFAULT '[]',
                    clan_id INTEGER DEFAULT NULL,
                    clan_role TEXT DEFAULT NULL,
                    active_title TEXT DEFAULT NULL,
                    weather_preference TEXT DEFAULT NULL
                )
            """)

            # Tabela de Pokémon
            await db.execute("""
                CREATE TABLE IF NOT EXISTS pokemons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    pokedex_number INTEGER,
                    name TEXT,
                    nickname TEXT,
                    types TEXT,
                    rarity TEXT,
                    level INTEGER DEFAULT 1,
                    xp INTEGER DEFAULT 0,
                    hp INTEGER,
                    max_hp INTEGER,
                    attack INTEGER,
                    defense INTEGER,
                    speed INTEGER,
                    moves TEXT,
                    nature TEXT,
                    potential TEXT,
                    personality TEXT DEFAULT 'agressivo',
                    friendship INTEGER DEFAULT 0,
                    is_shiny INTEGER DEFAULT 0,
                    is_favorite INTEGER DEFAULT 0,
                    is_in_team INTEGER DEFAULT 0,
                    team_position INTEGER DEFAULT -1,
                    battle_wins INTEGER DEFAULT 0,
                    battle_losses INTEGER DEFAULT 0,
                    caught_at TEXT,
                    caught_region TEXT,
                    caught_area TEXT,
                    FOREIGN KEY (user_id) REFERENCES trainers(user_id)
                )
            """)

            # Tabela de inventário
            await db.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item_type TEXT,
                    item_id TEXT,
                    quantity INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES trainers(user_id)
                )
            """)

            # Tabela de missões
            await db.execute("""
                CREATE TABLE IF NOT EXISTS quests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    quest_name TEXT,
                    quest_type TEXT,
                    description TEXT,
                    requirements TEXT,
                    progress TEXT,
                    completed INTEGER DEFAULT 0,
                    claimed INTEGER DEFAULT 0,
                    created_at TEXT,
                    expires_at TEXT,
                    reward TEXT,
                    FOREIGN KEY (user_id) REFERENCES trainers(user_id)
                )
            """)

            # Tabela de cooldowns
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cooldowns (
                    user_id INTEGER,
                    cooldown_type TEXT,
                    expires_at TEXT,
                    PRIMARY KEY (user_id, cooldown_type)
                )
            """)

            # Tabela de batalhas PvP
            await db.execute("""
                CREATE TABLE IF NOT EXISTS pvp_battles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    challenger_id INTEGER,
                    opponent_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT,
                    battle_data TEXT
                )
            """)

            # Tabela de leaderboard
            await db.execute("""
                CREATE TABLE IF NOT EXISTS leaderboard (
                    user_id INTEGER PRIMARY KEY,
                    points INTEGER DEFAULT 0,
                    rank_position INTEGER,
                    updated_at TEXT
                )
            """)

            # Tabela de ovos
            await db.execute("""
                CREATE TABLE IF NOT EXISTS eggs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    egg_type TEXT,
                    pokemon_id INTEGER DEFAULT NULL,
                    hatch_progress INTEGER DEFAULT 0,
                    hatch_time INTEGER,
                    obtained_at TEXT,
                    hatched INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES trainers(user_id)
                )
            """)

            # Tabela de clãs
            await db.execute("""
                CREATE TABLE IF NOT EXISTS clans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    tag TEXT,
                    description TEXT,
                    leader_id INTEGER,
                    members TEXT DEFAULT '[]',
                    bank_coins INTEGER DEFAULT 0,
                    total_xp INTEGER DEFAULT 0,
                    created_at TEXT,
                    emblem TEXT DEFAULT '🛡️'
                )
            """)

            # Tabela de raids
            await db.execute("""
                CREATE TABLE IF NOT EXISTS raids (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    boss_id TEXT,
                    region TEXT,
                    area TEXT,
                    started_at TEXT,
                    ends_at TEXT,
                    participants TEXT DEFAULT '[]',
                    total_damage INTEGER DEFAULT 0,
                    defeated INTEGER DEFAULT 0,
                    rewards_distributed INTEGER DEFAULT 0
                )
            """)

            # Tabela de spawns selvagens
            await db.execute("""
                CREATE TABLE IF NOT EXISTS wild_spawns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    pokemon_data TEXT,
                    spawn_time TEXT,
                    despawn_time TEXT,
                    caught INTEGER DEFAULT 0,
                    caught_by INTEGER DEFAULT NULL
                )
            """)

            # Tabela de diário de jornada
            await db.execute("""
                CREATE TABLE IF NOT EXISTS diary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    entry_type TEXT,
                    entry_data TEXT,
                    entry_time TEXT,
                    FOREIGN KEY (user_id) REFERENCES trainers(user_id)
                )
            """)

            # Tabela de mercado
            await db.execute("""
                CREATE TABLE IF NOT EXISTS market (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seller_id INTEGER,
                    item_type TEXT,
                    item_id TEXT,
                    pokemon_id INTEGER DEFAULT NULL,
                    price INTEGER,
                    listed_at TEXT,
                    sold INTEGER DEFAULT 0,
                    buyer_id INTEGER DEFAULT NULL
                )
            """)

            await db.commit()

    async def get_trainer(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM trainers WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    result = dict(zip([col[0] for col in cursor.description], row))
                    # Parse JSON fields
                    for field in ['titles', 'stats', 'unlocked_regions', 'badges', 'completed_chapters', 'friendship_points', 'diary_entries']:
                        if field in result and result[field]:
                            try:
                                result[field] = json.loads(result[field])
                            except:
                                result[field] = [] if field in ['titles', 'unlocked_regions', 'badges', 'completed_chapters', 'diary_entries'] else {}
                    return result
                return None

    async def create_trainer(self, user_id, username, display_name):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO trainers (user_id, username, display_name, created_at, last_message, current_region, current_area, unlocked_regions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, display_name, datetime.now().isoformat(), datetime.now().isoformat(),
                  'verdalia', 'bosque_esmeralda', json.dumps(['verdalia', 'lumina'])))
            await db.commit()

    async def update_trainer(self, user_id, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            # Handle JSON fields
            json_fields = ['titles', 'stats', 'unlocked_regions', 'badges', 'completed_chapters', 'friendship_points', 'diary_entries']
            for k, v in kwargs.items():
                if k in json_fields and not isinstance(v, str):
                    kwargs[k] = json.dumps(v)
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [user_id]
            await db.execute(f"UPDATE trainers SET {set_clause} WHERE user_id = ?", values)
            await db.commit()

    async def add_pokemon(self, user_id, pokemon_data):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO pokemons (
                    user_id, pokedex_number, name, nickname, types, rarity, level, xp,
                    hp, max_hp, attack, defense, speed, moves, nature, potential,
                    personality, friendship, is_shiny, caught_at, caught_region, caught_area
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, pokemon_data["pokedex_number"], pokemon_data["name"],
                pokemon_data.get("nickname", pokemon_data["name"]),
                json.dumps(pokemon_data["types"]), pokemon_data["rarity"],
                pokemon_data["level"], pokemon_data["xp"],
                pokemon_data["hp"], pokemon_data["max_hp"],
                pokemon_data["attack"], pokemon_data["defense"], pokemon_data["speed"],
                json.dumps(pokemon_data["moves"]), pokemon_data["nature"],
                json.dumps(pokemon_data.get("potential", {})),
                pokemon_data.get("personality", "agressivo"),
                pokemon_data.get("friendship", 0),
                1 if pokemon_data.get("is_shiny") else 0,
                datetime.now().isoformat(),
                pokemon_data.get("caught_region", "verdalia"),
                pokemon_data.get("caught_area", "bosque_esmeralda")
            ))
            await db.commit()
            return cursor.lastrowid

    async def get_pokemons(self, user_id, in_team_only=False):
        async with aiosqlite.connect(self.db_path) as db:
            query = "SELECT * FROM pokemons WHERE user_id = ?"
            params = [user_id]
            if in_team_only:
                query += " AND is_in_team = 1 ORDER BY team_position"
            else:
                query += " ORDER BY is_in_team DESC, team_position ASC, id DESC"
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    pokemon = dict(zip([col[0] for col in cursor.description], row))
                    pokemon["types"] = json.loads(pokemon["types"])
                    pokemon["moves"] = json.loads(pokemon["moves"])
                    pokemon["potential"] = json.loads(pokemon["potential"])
                    pokemon["is_shiny"] = bool(pokemon["is_shiny"])
                    pokemon["is_favorite"] = bool(pokemon["is_favorite"])
                    pokemon["is_in_team"] = bool(pokemon["is_in_team"])
                    result.append(pokemon)
                return result

    async def get_pokemon_by_id(self, pokemon_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM pokemons WHERE id = ?", (pokemon_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    pokemon = dict(zip([col[0] for col in cursor.description], row))
                    pokemon["types"] = json.loads(pokemon["types"])
                    pokemon["moves"] = json.loads(pokemon["moves"])
                    pokemon["potential"] = json.loads(pokemon["potential"])
                    pokemon["is_shiny"] = bool(pokemon["is_shiny"])
                    pokemon["is_favorite"] = bool(pokemon["is_favorite"])
                    pokemon["is_in_team"] = bool(pokemon["is_in_team"])
                    return pokemon
                return None

    async def update_pokemon(self, pokemon_id, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [pokemon_id]
            await db.execute(f"UPDATE pokemons SET {set_clause} WHERE id = ?", values)
            await db.commit()

    async def delete_pokemon(self, pokemon_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM pokemons WHERE id = ?", (pokemon_id,))
            await db.commit()

    async def get_inventory(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM inventory WHERE user_id = ?", (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]

    async def add_item(self, user_id, item_type, item_id, quantity=1):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, quantity FROM inventory WHERE user_id = ? AND item_type = ? AND item_id = ?",
                (user_id, item_type, item_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    await db.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (quantity, row[0]))
                else:
                    await db.execute(
                        "INSERT INTO inventory (user_id, item_type, item_id, quantity) VALUES (?, ?, ?, ?)",
                        (user_id, item_type, item_id, quantity)
                    )
            await db.commit()

    async def remove_item(self, user_id, item_type, item_id, quantity=1):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, quantity FROM inventory WHERE user_id = ? AND item_type = ? AND item_id = ?",
                (user_id, item_type, item_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    new_qty = row[1] - quantity
                    if new_qty <= 0:
                        await db.execute("DELETE FROM inventory WHERE id = ?", (row[0],))
                    else:
                        await db.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_qty, row[0]))
                    await db.commit()
                    return True
                return False

    async def get_quests(self, user_id, completed=None):
        async with aiosqlite.connect(self.db_path) as db:
            query = "SELECT * FROM quests WHERE user_id = ?"
            params = [user_id]
            if completed is not None:
                query += " AND completed = ?"
                params.append(1 if completed else 0)
            query += " ORDER BY created_at DESC"
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    quest = dict(zip([col[0] for col in cursor.description], row))
                    quest["requirements"] = json.loads(quest["requirements"])
                    quest["progress"] = json.loads(quest["progress"])
                    quest["reward"] = json.loads(quest["reward"])
                    result.append(quest)
                return result

    async def add_quest(self, user_id, quest_data):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO quests (user_id, quest_name, quest_type, description, requirements, progress, reward, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, quest_data["name"], quest_data["type"], quest_data["description"],
                json.dumps(quest_data["requirements"]), json.dumps(quest_data.get("progress", {})),
                json.dumps(quest_data["reward"]), datetime.now().isoformat(),
                quest_data.get("expires_at", (datetime.now() + timedelta(days=1)).isoformat())
            ))
            await db.commit()

    async def update_quest(self, quest_id, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [quest_id]
            await db.execute(f"UPDATE quests SET {set_clause} WHERE id = ?", values)
            await db.commit()

    async def check_cooldown(self, user_id, cooldown_type, duration_seconds):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT expires_at FROM cooldowns WHERE user_id = ? AND cooldown_type = ?",
                (user_id, cooldown_type)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    expires = datetime.fromisoformat(row[0])
                    if expires > datetime.now():
                        remaining = (expires - datetime.now()).total_seconds()
                        return False, remaining
            expires_at = (datetime.now() + timedelta(seconds=duration_seconds)).isoformat()
            await db.execute(
                "INSERT OR REPLACE INTO cooldowns (user_id, cooldown_type, expires_at) VALUES (?, ?, ?)",
                (user_id, cooldown_type, expires_at)
            )
            await db.commit()
            return True, 0

    async def get_leaderboard(self, limit=10):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT t.user_id, t.username, t.level, t.xp, t.total_catches, t.total_wins, t.badges, l.points "
                "FROM trainers t LEFT JOIN leaderboard l ON t.user_id = l.user_id "
                "ORDER BY t.level DESC, t.xp DESC LIMIT ?", (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    entry = dict(zip([col[0] for col in cursor.description], row))
                    try:
                        entry["badges"] = json.loads(entry["badges"]) if entry["badges"] else []
                    except:
                        entry["badges"] = []
                    result.append(entry)
                return result

    async def update_leaderboard(self, user_id, points):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO leaderboard (user_id, points, updated_at) VALUES (?, ?, ?)",
                (user_id, points, datetime.now().isoformat())
            )
            await db.commit()

    # ═══════════════════════════════════════════════════════════════
    # NOVOS MÉTODOS — MUNDO VIVO RPG
    # ═══════════════════════════════════════════════════════════════

    async def add_diary_entry(self, user_id, entry_type, entry_data):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO diary (user_id, entry_type, entry_data, entry_time) VALUES (?, ?, ?, ?)",
                (user_id, entry_type, json.dumps(entry_data), datetime.now().isoformat())
            )
            await db.commit()

    async def get_diary(self, user_id, limit=50):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM diary WHERE user_id = ? ORDER BY entry_time DESC LIMIT ?",
                (user_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    entry = dict(zip([col[0] for col in cursor.description], row))
                    entry["entry_data"] = json.loads(entry["entry_data"])
                    result.append(entry)
                return result

    async def add_egg(self, user_id, egg_type, hatch_time):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO eggs (user_id, egg_type, hatch_time, obtained_at) VALUES (?, ?, ?, ?)",
                (user_id, egg_type, hatch_time, datetime.now().isoformat())
            )
            await db.commit()
            return cursor.lastrowid

    async def get_eggs(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM eggs WHERE user_id = ? AND hatched = 0", (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]

    async def update_egg(self, egg_id, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [egg_id]
            await db.execute(f"UPDATE eggs SET {set_clause} WHERE id = ?", values)
            await db.commit()

    async def create_clan(self, name, tag, description, leader_id, emblem='🛡️'):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO clans (name, tag, description, leader_id, members, created_at, emblem) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, tag, description, leader_id, json.dumps([leader_id]), datetime.now().isoformat(), emblem)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_clan(self, clan_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM clans WHERE id = ?", (clan_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    clan = dict(zip([col[0] for col in cursor.description], row))
                    clan["members"] = json.loads(clan["members"])
                    return clan
                return None

    async def update_clan(self, clan_id, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            if "members" in kwargs and not isinstance(kwargs["members"], str):
                kwargs["members"] = json.dumps(kwargs["members"])
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [clan_id]
            await db.execute(f"UPDATE clans SET {set_clause} WHERE id = ?", values)
            await db.commit()

    async def add_wild_spawn(self, guild_id, channel_id, pokemon_data, despawn_minutes=5):
        async with aiosqlite.connect(self.db_path) as db:
            spawn_time = datetime.now().isoformat()
            despawn_time = (datetime.now() + timedelta(minutes=despawn_minutes)).isoformat()
            cursor = await db.execute(
                "INSERT INTO wild_spawns (guild_id, channel_id, pokemon_data, spawn_time, despawn_time) VALUES (?, ?, ?, ?, ?)",
                (guild_id, channel_id, json.dumps(pokemon_data), spawn_time, despawn_time)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_active_spawns(self, guild_id=None):
        async with aiosqlite.connect(self.db_path) as db:
            query = "SELECT * FROM wild_spawns WHERE caught = 0 AND despawn_time > ?"
            params = [datetime.now().isoformat()]
            if guild_id:
                query += " AND guild_id = ?"
                params.append(guild_id)
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    spawn = dict(zip([col[0] for col in cursor.description], row))
                    spawn["pokemon_data"] = json.loads(spawn["pokemon_data"])
                    result.append(spawn)
                return result

    async def catch_spawn(self, spawn_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE wild_spawns SET caught = 1, caught_by = ? WHERE id = ?",
                (user_id, spawn_id)
            )
            await db.commit()

    async def create_raid(self, boss_id, region, area, duration_minutes=30):
        async with aiosqlite.connect(self.db_path) as db:
            started_at = datetime.now().isoformat()
            ends_at = (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
            cursor = await db.execute(
                "INSERT INTO raids (boss_id, region, area, started_at, ends_at) VALUES (?, ?, ?, ?, ?)",
                (boss_id, region, area, started_at, ends_at)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_active_raids(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM raids WHERE defeated = 0 AND ends_at > ?",
                (datetime.now().isoformat(),)
            ) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    raid = dict(zip([col[0] for col in cursor.description], row))
                    raid["participants"] = json.loads(raid["participants"])
                    result.append(raid)
                return result

    async def join_raid(self, raid_id, user_id, damage):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT participants, total_damage FROM raids WHERE id = ?", (raid_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    participants = json.loads(row[0])
                    participants.append({"user_id": user_id, "damage": damage})
                    total_damage = row[1] + damage
                    await db.execute(
                        "UPDATE raids SET participants = ?, total_damage = ? WHERE id = ?",
                        (json.dumps(participants), total_damage, raid_id)
                    )
                    await db.commit()

    async def add_market_listing(self, seller_id, item_type, item_id, price, pokemon_id=None):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO market (seller_id, item_type, item_id, pokemon_id, price, listed_at) VALUES (?, ?, ?, ?, ?, ?)",
                (seller_id, item_type, item_id, pokemon_id, price, datetime.now().isoformat())
            )
            await db.commit()
            return cursor.lastrowid

    async def get_market_listings(self, sold=False):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM market WHERE sold = ? ORDER BY listed_at DESC",
                (1 if sold else 0,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]

# Instância global
db = Database()
