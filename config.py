"""
Configurações do Bot Pokémon
"""
import os

# Token do Discord (do Railway via variável de ambiente)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Configurações gerais
BOT_NAME = "Pokémon World"
BOT_PREFIX = "!"
DEFAULT_GUILD = None

# Configurações de XP
XP_COOLDOWN_SECONDS = 60
XP_PER_MESSAGE = 5
XP_PER_CATCH = 50
XP_PER_BATTLE_WIN = 100
XP_PER_QUEST = 150
XP_PER_DAILY = 200

# Curva de níveis
BASE_XP = 100
XP_MULTIPLIER = 1.5

# Configurações de batalha
BATTLE_TIMEOUT = 120
MAX_TEAM_SIZE = 6

# Configurações de captura
BASE_CATCH_RATE = 0.3
SHINY_CHANCE = 0.004096

# Configurações de economia
DAILY_COINS = 500
STARTING_COINS = 1000

# Raridades e chances
RARITY_CHANCES = {
    "comum": 0.60,
    "raro": 0.25,
    "epico": 0.10,
    "lendario": 0.04,
    "mitico": 0.01,
}

# URLs da PokéAPI
POKEAPI_BASE = "https://pokeapi.co/api/v2"
POKEAPI_SPRITE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"
POKEAPI_OFFICIAL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork"

# Cores para embeds
COLORS = {
    "comum": 0x95A5A6,
    "raro": 0x3498DB,
    "epico": 0x9B59B6,
    "lendario": 0xF1C40F,
    "mitico": 0xE74C3C,
    "shiny": 0xFF69B4,
    "info": 0x2ECC71,
    "warning": 0xE67E22,
    "error": 0xC0392B,
    "premium": 0x1ABC9C,
}

# Emojis premium
EMOJIS = {
    "pokeball": "⚪",
    "greatball": "🔵",
    "ultraball": "🟡",
    "masterball": "🔴",
    "coin": "💰",
    "xp": "✨",
    "hp": "❤️",
    "attack": "⚔️",
    "defense": "🛡️",
    "speed": "💨",
    "star": "⭐",
    "shiny": "✨",
    "level": "📊",
    "trophy": "🏆",
    "chest": "📦",
    "potion": "🧪",
    "card": "🃏",
    "quest": "📜",
    "battle": "⚔️",
    "catch": "🎯",
    "evolve": "🔄",
    "trade": "🤝",
    "shop": "🏪",
    "inventory": "🎒",
    "pokedex": "📖",
    "profile": "👤",
    "leaderboard": "📈",
    "daily": "📅",
    "gift": "🎁",
    "fire": "🔥",
    "water": "💧",
    "grass": "🌿",
    "electric": "⚡",
    "ice": "❄️",
    "fighting": "👊",
    "poison": "☠️",
    "ground": "🌍",
    "flying": "🦅",
    "psychic": "🔮",
    "bug": "🐛",
    "rock": "🪨",
    "ghost": "👻",
    "dragon": "🐉",
    "dark": "🌑",
    "steel": "⚙️",
    "fairy": "🧚",
}

# Tipos de Pokémon e vantagens
TYPE_EFFECTIVENESS = {
    "normal": {"rock": 0.5, "ghost": 0, "steel": 0.5},
    "fire": {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "bug": 2, "rock": 0.5, "dragon": 0.5, "steel": 2},
    "water": {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, "rock": 2, "dragon": 0.5},
    "grass": {"fire": 0.5, "water": 2, "grass": 0.5, "poison": 0.5, "ground": 2, "flying": 0.5, "bug": 0.5, "rock": 2, "dragon": 0.5, "steel": 0.5},
    "electric": {"water": 2, "grass": 0.5, "electric": 0.5, "ground": 0, "flying": 2, "dragon": 0.5},
    "ice": {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 0.5, "ground": 2, "flying": 2, "dragon": 2, "steel": 0.5},
    "fighting": {"normal": 2, "ice": 2, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2, "ghost": 0, "dark": 2, "steel": 2, "fairy": 0.5},
    "poison": {"grass": 2, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0, "fairy": 2},
    "ground": {"fire": 2, "electric": 2, "grass": 0.5, "poison": 2, "flying": 0, "bug": 0.5, "rock": 2, "steel": 2},
    "flying": {"electric": 0.5, "grass": 2, "fighting": 2, "bug": 2, "rock": 0.5, "steel": 0.5},
    "psychic": {"fighting": 2, "poison": 2, "psychic": 0.5, "dark": 0, "steel": 0.5},
    "bug": {"fire": 0.5, "grass": 2, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2, "ghost": 0.5, "dark": 2, "steel": 0.5, "fairy": 0.5},
    "rock": {"fire": 2, "ice": 2, "fighting": 0.5, "ground": 0.5, "flying": 2, "bug": 2, "steel": 0.5},
    "ghost": {"normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5},
    "dragon": {"dragon": 2, "steel": 0.5, "fairy": 0},
    "dark": {"fighting": 0.5, "psychic": 2, "ghost": 2, "dark": 0.5, "fairy": 0.5},
    "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2, "rock": 2, "steel": 0.5, "fairy": 2},
    "fairy": {"fire": 0.5, "fighting": 2, "poison": 0.5, "dragon": 2, "dark": 2, "steel": 0.5},
}

# Natures e seus efeitos
NATURES = {
    "hardy": {"attack": 1.0, "defense": 1.0, "speed": 1.0},
    "lonely": {"attack": 1.1, "defense": 0.9, "speed": 1.0},
    "brave": {"attack": 1.1, "defense": 1.0, "speed": 0.9},
    "adamant": {"attack": 1.1, "defense": 1.0, "speed": 1.0},
    "naughty": {"attack": 1.1, "defense": 1.0, "speed": 1.0},
    "bold": {"attack": 0.9, "defense": 1.1, "speed": 1.0},
    "docile": {"attack": 1.0, "defense": 1.0, "speed": 1.0},
    "relaxed": {"attack": 1.0, "defense": 1.1, "speed": 0.9},
    "impish": {"attack": 1.0, "defense": 1.1, "speed": 1.0},
    "lax": {"attack": 1.0, "defense": 1.1, "speed": 1.0},
    "timid": {"attack": 0.9, "defense": 1.0, "speed": 1.1},
    "hasty": {"attack": 1.0, "defense": 0.9, "speed": 1.1},
    "serious": {"attack": 1.0, "defense": 1.0, "speed": 1.0},
    "jolly": {"attack": 1.0, "defense": 1.0, "speed": 1.1},
    "naive": {"attack": 1.0, "defense": 1.0, "speed": 1.1},
    "modest": {"attack": 0.9, "defense": 1.0, "speed": 1.0},
    "mild": {"attack": 1.0, "defense": 0.9, "speed": 1.0},
    "quiet": {"attack": 1.0, "defense": 1.0, "speed": 0.9},
    "bashful": {"attack": 1.0, "defense": 1.0, "speed": 1.0},
    "rash": {"attack": 1.0, "defense": 0.9, "speed": 1.0},
    "calm": {"attack": 0.9, "defense": 1.0, "speed": 1.0},
    "gentle": {"attack": 1.0, "defense": 0.9, "speed": 1.0},
    "sassy": {"attack": 1.0, "defense": 1.0, "speed": 0.9},
    "careful": {"attack": 1.0, "defense": 1.0, "speed": 1.0},
    "quirky": {"attack": 1.0, "defense": 1.0, "speed": 1.0},
}

# Golpes por tipo
MOVES_BY_TYPE = {
    "normal": ["Tackle", "Quick Attack", "Body Slam", "Hyper Beam", "Double-Edge", "Slam", "Headbutt"],
    "fire": ["Ember", "Flamethrower", "Fire Blast", "Fire Punch", "Heat Wave", "Flame Wheel"],
    "water": ["Water Gun", "Hydro Pump", "Surf", "Bubble Beam", "Aqua Jet", "Waterfall"],
    "grass": ["Vine Whip", "Razor Leaf", "Solar Beam", "Energy Ball", "Leaf Blade", "Petal Dance"],
    "electric": ["Thunder Shock", "Thunderbolt", "Thunder", "Spark", "Thunder Punch", "Volt Switch"],
    "ice": ["Ice Beam", "Blizzard", "Ice Punch", "Aurora Beam", "Ice Shard", "Frost Breath"],
    "fighting": ["Karate Chop", "Cross Chop", "Dynamic Punch", "Close Combat", "Focus Blast", "Mach Punch"],
    "poison": ["Poison Sting", "Sludge Bomb", "Poison Jab", "Toxic", "Acid", "Venoshock"],
    "ground": ["Earthquake", "Dig", "Mud Shot", "Bulldoze", "Earth Power", "Sand Tomb"],
    "flying": ["Gust", "Wing Attack", "Air Slash", "Fly", "Hurricane", "Aerial Ace"],
    "psychic": ["Confusion", "Psychic", "Psybeam", "Future Sight", "Zen Headbutt", "Psyshock"],
    "bug": ["Bug Bite", "X-Scissor", "Bug Buzz", "Signal Beam", "Fury Cutter", "Leech Life"],
    "rock": ["Rock Throw", "Rock Slide", "Stone Edge", "Rock Blast", "Power Gem", "Ancient Power"],
    "ghost": ["Shadow Ball", "Shadow Claw", "Hex", "Night Shade", "Phantom Force", "Shadow Sneak"],
    "dragon": ["Dragon Breath", "Dragon Claw", "Dragon Pulse", "Outrage", "Draco Meteor", "Dragon Rush"],
    "dark": ["Bite", "Crunch", "Dark Pulse", "Night Slash", "Foul Play", "Knock Off"],
    "steel": ["Metal Claw", "Iron Head", "Steel Wing", "Flash Cannon", "Meteor Mash", "Bullet Punch"],
    "fairy": ["Fairy Wind", "Moonblast", "Dazzling Gleam", "Play Rough", "Draining Kiss", "Sweet Kiss"],
}

# Itens da loja
SHOP_ITEMS = {
    "pokeball": {"name": "Poké Ball", "price": 200, "description": "Bola básica para capturar Pokémon", "emoji": "⚪"},
    "greatball": {"name": "Great Ball", "price": 600, "description": "Bola com melhor taxa de captura", "emoji": "🔵"},
    "ultraball": {"name": "Ultra Ball", "price": 1200, "description": "Bola com excelente taxa de captura", "emoji": "🟡"},
    "masterball": {"name": "Master Ball", "price": 50000, "description": "Captura garantida (exceto lendários)", "emoji": "🔴"},
    "potion": {"name": "Poção", "price": 300, "description": "Recupera 20 HP", "emoji": "🧪"},
    "superpotion": {"name": "Super Poção", "price": 700, "description": "Recupera 50 HP", "emoji": "🧪"},
    "hyperpotion": {"name": "Hiper Poção", "price": 1500, "description": "Recupera 200 HP", "emoji": "🧪"},
    "revive": {"name": "Reviver", "price": 2000, "description": "Revive um Pokémon com metade do HP", "emoji": "💊"},
    "xattack": {"name": "X Ataque", "price": 500, "description": "Aumenta ataque em batalha", "emoji": "⚔️"},
    "xdefense": {"name": "X Defesa", "price": 500, "description": "Aumenta defesa em batalha", "emoji": "🛡️"},
    "rarecandy": {"name": "Doce Raro", "price": 3000, "description": "Aumenta 1 nível do Pokémon", "emoji": "🍬"},
    "mysterybox": {"name": "Caixa Misteriosa", "price": 1000, "description": "Contém um item ou Pokémon surpresa", "emoji": "📦"},
}

# Cartas de melhoria
UPGRADE_CARDS = {
    "attack_card": {"name": "Carta de Ataque", "effect": {"attack": 10}, "rarity": "comum", "description": "+10 de Ataque"},
    "defense_card": {"name": "Carta de Defesa", "effect": {"defense": 10}, "rarity": "comum", "description": "+10 de Defesa"},
    "speed_card": {"name": "Carta de Velocidade", "effect": {"speed": 10}, "rarity": "comum", "description": "+10 de Velocidade"},
    "hp_card": {"name": "Carta de Vida", "effect": {"hp": 20}, "rarity": "comum", "description": "+20 de HP"},
    "xp_card": {"name": "Carta de XP", "effect": {"xp": 100}, "rarity": "raro", "description": "+100 de XP"},
    "crit_card": {"name": "Carta Crítica", "effect": {"crit_chance": 5}, "rarity": "epico", "description": "+5% chance de crítico"},
    "shiny_charm": {"name": "Amuleto Shiny", "effect": {"shiny_chance": 2}, "rarity": "lendario", "description": "Dobra chance de Shiny"},
    "master_fragment": {"name": "Fragmento Mestre", "effect": {"all": 5}, "rarity": "mitico", "description": "+5 em todos os atributos"},
}

# Missões diárias
DAILY_QUESTS = [
    {"name": "Caçador Iniciante", "description": "Capture 3 Pokémon", "requirement": {"catches": 3}, "reward": {"coins": 300, "xp": 100}},
    {"name": "Treinador Dedicado", "description": "Vença 2 batalhas", "requirement": {"wins": 2}, "reward": {"coins": 500, "xp": 150}},
    {"name": "Explorador", "description": "Envie 20 mensagens no servidor", "requirement": {"messages": 20}, "reward": {"coins": 200, "xp": 80}},
    {"name": "Colecionador", "description": "Adicione 1 Pokémon ao time", "requirement": {"team_add": 1}, "reward": {"coins": 400, "xp": 120}},
    {"name": "Comerciante", "description": "Compre 1 item na loja", "requirement": {"shop_buy": 1}, "reward": {"coins": 250, "xp": 60}},
]

# Ranks de treinador
TRAINER_RANKS = [
    {"name": "Novato", "min_level": 1, "emoji": "🌱"},
    {"name": "Aprendiz", "min_level": 10, "emoji": "🌿"},
    {"name": "Treinador", "min_level": 25, "emoji": "🍃"},
    {"name": "Especialista", "min_level": 40, "emoji": "🌳"},
    {"name": "Líder", "min_level": 60, "emoji": "⭐"},
    {"name": "Elite", "min_level": 80, "emoji": "🌟"},
    {"name": "Campeão", "min_level": 100, "emoji": "🏆"},
    {"name": "Mestre", "min_level": 150, "emoji": "👑"},
]

# Especializações de treinador
SPECIALIZATIONS = {
    "capturador": {"name": "Capturador", "bonus": {"catch_rate": 0.1, "xp_catch": 1.2}, "description": "Maior chance de captura e mais XP"},
    "batalhador": {"name": "Batalhador", "bonus": {"attack": 1.1, "xp_battle": 1.3}, "description": "Mais ataque e XP em batalhas"},
    "tank": {"name": "Tanque", "bonus": {"defense": 1.15, "hp": 1.1}, "description": "Mais defesa e HP"},
    "velocista": {"name": "Velocista", "bonus": {"speed": 1.2, "crit_chance": 5}, "description": "Mais velocidade e chance de crítico"},
    "estrategista": {"name": "Estrategista", "bonus": {"type_advantage": 1.2, "dodge_chance": 5}, "description": "Vantagem de tipo aumentada e esquiva"},
}
