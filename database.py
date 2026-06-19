"""
Sistema de banco de dados SQLite para o Bot Pokémon
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
        # Garantir que o diretório do banco existe
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
                    last_message TEXT
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
                    is_shiny INTEGER DEFAULT 0,
                    is_favorite INTEGER DEFAULT 0,
                    is_in_team INTEGER DEFAULT 0,
                    team_position INTEGER DEFAULT -1,
                    battle_wins INTEGER DEFAULT 0,
                    battle_losses INTEGER DEFAULT 0,
                    caught_at TEXT,
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

            await db.commit()

    async def get_trainer(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM trainers WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(zip([col[0] for col in cursor.description], row))
                return None

    async def create_trainer(self, user_id, username, display_name):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO trainers (user_id, username, display_name, created_at, last_message)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, display_name, datetime.now().isoformat(), datetime.now().isoformat()))
            await db.commit()

    async def update_trainer(self, user_id, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [user_id]
            await db.execute(f"UPDATE trainers SET {set_clause} WHERE user_id = ?", values)
            await db.commit()

    async def add_pokemon(self, user_id, pokemon_data):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO pokemons (
                    user_id, pokedex_number, name, nickname, types, rarity, level, xp,
                    hp, max_hp, attack, defense, speed, moves, nature, potential,
                    is_shiny, caught_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, pokemon_data["pokedex_number"], pokemon_data["name"],
                pokemon_data.get("nickname", pokemon_data["name"]),
                json.dumps(pokemon_data["types"]), pokemon_data["rarity"],
                pokemon_data["level"], pokemon_data["xp"],
                pokemon_data["hp"], pokemon_data["max_hp"],
                pokemon_data["attack"], pokemon_data["defense"], pokemon_data["speed"],
                json.dumps(pokemon_data["moves"]), pokemon_data["nature"],
                json.dumps(pokemon_data.get("potential", {})),
                1 if pokemon_data.get("is_shiny") else 0,
                datetime.now().isoformat()
            ))
            await db.commit()
            return db.last_insert_rowid()

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
            async with db.execute(
                "SELECT * FROM inventory WHERE user_id = ?", (user_id,)
            ) as cursor:
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
                    await db.execute(
                        "UPDATE inventory SET quantity = quantity + ? WHERE id = ?",
                        (quantity, row[0])
                    )
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
                "SELECT t.user_id, t.username, t.level, t.xp, t.total_catches, t.total_wins, l.points "
                "FROM trainers t LEFT JOIN leaderboard l ON t.user_id = l.user_id "
                "ORDER BY t.level DESC, t.xp DESC LIMIT ?", (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]

    async def update_leaderboard(self, user_id, points):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO leaderboard (user_id, points, updated_at) VALUES (?, ?, ?)",
                (user_id, points, datetime.now().isoformat())
            )
            await db.commit()

# Instância global
db = Database()
