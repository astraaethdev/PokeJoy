"""
Configurações do Bot Pokémon — MUNDO VIVO RPG
"""
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_NAME = "Pokémon World"
BOT_PREFIX = "!"
DEFAULT_GUILD = None

XP_COOLDOWN_SECONDS = 60
XP_PER_MESSAGE = 5
XP_PER_CATCH = 50
XP_PER_BATTLE_WIN = 100
XP_PER_QUEST = 150
XP_PER_DAILY = 200
XP_PER_EXPLORE = 10
XP_PER_GYM_WIN = 200

BASE_XP = 100
XP_MULTIPLIER = 1.5
BATTLE_TIMEOUT = 120
MAX_TEAM_SIZE = 6
BASE_CATCH_RATE = 0.3
SHINY_CHANCE = 0.004096
DAILY_COINS = 500
STARTING_COINS = 1000

RARITY_CHANCES = {
    "comum": 0.60, "raro": 0.25, "epico": 0.10,
    "lendario": 0.04, "mitico": 0.01,
}

POKEAPI_BASE = "https://pokeapi.co/api/v2"
POKEAPI_SPRITE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"
POKEAPI_OFFICIAL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork"

COLORS = {
    "comum": 0x95A5A6, "raro": 0x3498DB, "epico": 0x9B59B6,
    "lendario": 0xF1C40F, "mitico": 0xE74C3C, "shiny": 0xFF69B4,
    "info": 0x2ECC71, "warning": 0xE67E22, "error": 0xC0392B,
    "premium": 0x1ABC9C,
    "verdalia": 0x27AE60, "frostvale": 0x5DADE2, "mareazul": 0x2980B9,
    "vulkar": 0xE74C3C, "drakoria": 0x8E44AD, "lumina": 0xF1C40F,
    "sol": 0xF39C12, "chuva": 0x3498DB, "tempestade": 0x2C3E50,
    "neve": 0xECF0F1, "nevoa": 0xBDC3C7, "noite": 0x1A1A2E,
}

EMOJIS = {
    "pokeball": "⚪", "greatball": "🔵", "ultraball": "🟡", "masterball": "🔴",
    "coin": "💰", "xp": "✨", "hp": "❤️", "attack": "⚔️", "defense": "🛡️",
    "speed": "💨", "star": "⭐", "shiny": "✨", "level": "📊", "trophy": "🏆",
    "chest": "📦", "potion": "🧪", "card": "🃏", "quest": "📜", "battle": "⚔️",
    "catch": "🎯", "evolve": "🔄", "trade": "🤝", "shop": "🏪", "inventory": "🎒",
    "pokedex": "📖", "profile": "👤", "leaderboard": "📈", "daily": "📅", "gift": "🎁",
    "fire": "🔥", "water": "💧", "grass": "🌿", "electric": "⚡", "ice": "❄️",
    "fighting": "👊", "poison": "☠️", "ground": "🌍", "flying": "🦅", "psychic": "🔮",
    "bug": "🐛", "rock": "🪨", "ghost": "👻", "dragon": "🐉", "dark": "🌑",
    "steel": "⚙️", "fairy": "🧚", "map": "🗺️", "explore": "🔍", "camp": "🏕️",
    "weather": "🌦️", "egg": "🥚", "gym": "🏛️", "badge": "🏅", "clan": "👥",
    "raid": "🌋", "market": "💹", "diary": "📓", "friendship": "💝", "personality": "🎭",
}

# ═══════════════════════════════════════════════════════════════
# 🌍 MUNDO VIVO — CONTINENTE ELYNDRA
# ═══════════════════════════════════════════════════════════════

ELYNDRA_WORLD = {
    "name": "Elyndra",
    "description": "Um continente vasto e misterioso, lar de Pokémon de todos os tipos e lendas antigas.",
    "map_url": "https://i.imgur.com/TTi1DH9.jpeg",
    "regions": {
        "verdalia": {
            "name": "Verdália", "emoji": "🌿", "color": "verdalia",
            "description": "Região inicial coberta por florestas exuberantes e vida selvagem abundante.",
            "climate": "temperate", "min_level": 1, "unlock_requirement": None,
            "areas": {
                "bosque_esmeralda": {
                    "name": "Bosque Esmeralda", "emoji": "🌲",
                    "description": "Uma floresta densa e vibrante, cheia de Pokémon do tipo Planta e Inseto.",
                    "min_level": 1, "max_level": 15,
                    "pokemon_ids": [1,2,3,10,11,12,13,14,15,16,17,18,21,22,25,29,30,32,33,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,69,70,71,102,103,113,114,122,123,125],
                    "rarity_weights": {"comum":0.55,"raro":0.30,"epico":0.12,"lendario":0.03,"mitico":0.00},
                    "events": ["pokemon_wild","item_found","trainer_encounter","secret_path","chest"],
                    "event_weights": [0.40,0.25,0.15,0.12,0.08],
                    "items": ["potion","pokeball","greatball","revive"],
                    "npcs": ["liora"],
                    "weather": ["sol","chuva","nevoa"],
                    "explore_actions": ["explorar","seguir_pegadas","coletar_recursos","montar_acampamento"],
                },
                "arvore_ancestral": {
                    "name": "Árvore Ancestral", "emoji": "🌳",
                    "description": "Uma árvore colossal que abriga Pokémon raros e sábios.",
                    "min_level": 8, "max_level": 20,
                    "pokemon_ids": [1,2,3,43,44,45,46,47,69,70,71,102,103,113,114],
                    "rarity_weights": {"comum":0.40,"raro":0.35,"epico":0.18,"lendario":0.06,"mitico":0.01},
                    "events": ["pokemon_wild","item_found","secret_path","chest","npc_wise"],
                    "event_weights": [0.35,0.20,0.20,0.15,0.10],
                    "items": ["potion","superpotion","pokeball","greatball","rarecandy"],
                    "npcs": ["elder_wood"],
                    "weather": ["sol","chuva","nevoa"],
                    "explore_actions": ["explorar","escalar","meditar","procurar_ninho"],
                },
                "caverna_cogumelos": {
                    "name": "Caverna dos Cogumelos", "emoji": "🍄",
                    "description": "Uma caverna iluminada por cogumelos bioluminescentes.",
                    "min_level": 5, "max_level": 18,
                    "pokemon_ids": [29,30,31,32,33,34,41,42,46,47,48,49,50,51,52,53,88,89,109,110],
                    "rarity_weights": {"comum":0.50,"raro":0.30,"epico":0.15,"lendario":0.04,"mitico":0.01},
                    "events": ["pokemon_wild","item_found","chest","secret_path"],
                    "event_weights": [0.45,0.25,0.20,0.10],
                    "items": ["potion","superpotion","pokeball","greatball","antidote"],
                    "npcs": ["mushroom_hermit"],
                    "weather": ["nevoa"],
                    "explore_actions": ["explorar","investigar_luz","coletar_cogumelos","descer_profundezas"],
                },
            },
        },
        "frostvale": {
            "name": "Frostvale", "emoji": "❄️", "color": "frostvale",
            "description": "Um reino congelado onde apenas os mais resistentes sobrevivem.",
            "climate": "cold", "min_level": 15,
            "unlock_requirement": {"chapter": "capitulo_1"},
            "areas": {
                "lago_cristalino": {
                    "name": "Lago Cristalino", "emoji": "🧊",
                    "description": "Um lago congelado de beleza hipnotizante.",
                    "min_level": 15, "max_level": 28,
                    "pokemon_ids": [86,87,90,91,116,117,118,119,120,121,124,126,131],
                    "rarity_weights": {"comum":0.50,"raro":0.30,"epico":0.15,"lendario":0.04,"mitico":0.01},
                    "events": ["pokemon_wild","item_found","trainer_encounter","chest"],
                    "event_weights": [0.40,0.25,0.20,0.15],
                    "items": ["potion","superpotion","greatball","ultraball","ice_heal"],
                    "npcs": ["nerys"],
                    "weather": ["neve","nevoa","sol"],
                    "explore_actions": ["explorar","pescar_no_gelo","escavar_neve","observar_aurora"],
                },
                "pico_vento_branco": {
                    "name": "Pico do Vento Branco", "emoji": "🏔️",
                    "description": "A montanha mais alta de Frostvale, lar de Pokémon lendários do gelo.",
                    "min_level": 20, "max_level": 35,
                    "pokemon_ids": [86,87,91,124,126,131,144],
                    "rarity_weights": {"comum":0.35,"raro":0.30,"epico":0.22,"lendario":0.10,"mitico":0.03},
                    "events": ["pokemon_wild","item_found","secret_path","chest","legendary_sign"],
                    "event_weights": [0.30,0.20,0.20,0.18,0.12],
                    "items": ["superpotion","hyperpotion","ultraball","rarecandy","ice_heal"],
                    "npcs": ["mountain_sage"],
                    "weather": ["neve","tempestade","nevoa"],
                    "explore_actions": ["explorar","escalar","buscar_abrigo","observar_horizonte"],
                },
                "ruinas_geladas": {
                    "name": "Ruínas Geladas", "emoji": "🏛️",
                    "description": "Ruínas antigas cobertas de gelo, guardando segredos do passado.",
                    "min_level": 18, "max_level": 32,
                    "pokemon_ids": [86,87,90,91,92,93,94,124,131],
                    "rarity_weights": {"comum":0.40,"raro":0.30,"epico":0.20,"lendario":0.08,"mitico":0.02},
                    "events": ["pokemon_wild","item_found","chest","secret_path","ancient_rune"],
                    "event_weights": [0.35,0.20,0.20,0.15,0.10],
                    "items": ["superpotion","hyperpotion","ultraball","revive","rarecandy"],
                    "npcs": ["ghost_historian"],
                    "weather": ["neve","nevoa"],
                    "explore_actions": ["explorar","decifrar_runas","escavar_ruinas","entrar_templo"],
                },
            },
        },
        "mareazul": {
            "name": "Maré Azul", "emoji": "🌊", "color": "mareazul",
            "description": "Um arquipélago de ilhas tropicais e mares cristalinos.",
            "climate": "tropical", "min_level": 25,
            "unlock_requirement": {"chapter": "capitulo_2"},
            "areas": {
                "ilha_coral": {
                    "name": "Ilha Coral", "emoji": "🐚",
                    "description": "Uma ilha paradisíaca com recifes de coral coloridos.",
                    "min_level": 25, "max_level": 40,
                    "pokemon_ids": [54,55,60,61,62,72,73,86,87,90,91,116,117,118,119,120,121,129,130],
                    "rarity_weights": {"comum":0.50,"raro":0.30,"epico":0.15,"lendario":0.04,"mitico":0.01},
                    "events": ["pokemon_wild","item_found","trainer_encounter","chest","tide_pool"],
                    "event_weights": [0.40,0.25,0.15,0.12,0.08],
                    "items": ["superpotion","hyperpotion","greatball","ultraball","dive_ball"],
                    "npcs": ["coral_diver"],
                    "weather": ["sol","chuva","tempestade"],
                    "explore_actions": ["explorar","mergulhar","coletar_conchas","observar_recife"],
                },
                "gruta_mares": {
                    "name": "Gruta das Marés", "emoji": "🌊",
                    "description": "Uma gruta submersa que só é acessível na maré baixa.",
                    "min_level": 30, "max_level": 45,
                    "pokemon_ids": [72,73,86,87,90,91,116,117,118,119,120,121,129,130,131],
                    "rarity_weights": {"comum":0.45,"raro":0.30,"epico":0.18,"lendario":0.05,"mitico":0.02},
                    "events": ["pokemon_wild","item_found","chest","secret_path","underwater_ruins"],
                    "event_weights": [0.40,0.20,0.20,0.12,0.08],
                    "items": ["hyperpotion","ultraball","dive_ball","revive","rarecandy"],
                    "npcs": ["tide_master"],
                    "weather": ["sol","chuva"],
                    "explore_actions": ["explorar","nadar","procurar_tesouro","respirar_bolha"],
                },
                "abismo_azul": {
                    "name": "Abismo Azul", "emoji": "🌑",
                    "description": "As profundezas mais escuras do oceano, onde monstros dormem.",
                    "min_level": 35, "max_level": 50,
                    "pokemon_ids": [72,73,90,91,116,117,118,119,120,121,129,130,131],
                    "rarity_weights": {"comum":0.30,"raro":0.30,"epico":0.25,"lendario":0.12,"mitico":0.03},
                    "events": ["pokemon_wild","item_found","chest","abyssal_horror","ancient_treasure"],
                    "event_weights": [0.35,0.20,0.20,0.15,0.10],
                    "items": ["hyperpotion","ultraball","masterball","revive","rarecandy","max_revive"],
                    "npcs": ["abyssal_watcher"],
                    "weather": ["nevoa","tempestade"],
                    "explore_actions": ["explorar","descer","usar_lanterna","escutar_silencio"],
                },
            },
        },
        "vulkar": {
            "name": "Vulkar", "emoji": "🔥", "color": "vulkar",
            "description": "Terras vulcânicas ardentes, forja de Pokémon de fogo e determinação.",
            "climate": "hot", "min_level": 35,
            "unlock_requirement": {"chapter": "capitulo_3"},
            "areas": {
                "vale_cinzas": {
                    "name": "Vale das Cinzas", "emoji": "🌋",
                    "description": "Um vale coberto de cinzas vulcânicas onde o calor é intenso.",
                    "min_level": 35, "max_level": 50,
                    "pokemon_ids": [4,5,6,37,38,58,59,77,78,109,110,111,112,126],
                    "rarity_weights": {"comum":0.45,"raro":0.30,"epico":0.18,"lendario":0.05,"mitico":0.02},
                    "events": ["pokemon_wild","item_found","trainer_encounter","chest","lava_flow"],
                    "event_weights": [0.40,0.25,0.15,0.12,0.08],
                    "items": ["superpotion","hyperpotion","ultraball","burn_heal","rarecandy"],
                    "npcs": ["kael"],
                    "weather": ["sol","tempestade"],
                    "explore_actions": ["explorar","cruzar_lava","coletar_cristais","observar_erupcao"],
                },
                "cratera_escarlate": {
                    "name": "Cratera Escarlate", "emoji": "🔴",
                    "description": "A boca do vulcão, onde o fogo é puro e intenso.",
                    "min_level": 40, "max_level": 55,
                    "pokemon_ids": [4,5,6,37,38,58,59,77,78,126,146],
                    "rarity_weights": {"comum":0.35,"raro":0.30,"epico":0.22,"lendario":0.10,"mitico":0.03},
                    "events": ["pokemon_wild","item_found","chest","legendary_sign","volcanic_eruption"],
                    "event_weights": [0.35,0.20,0.20,0.15,0.10],
                    "items": ["hyperpotion","ultraball","masterball","burn_heal","rarecandy","fire_stone"],
                    "npcs": ["volcano_keeper"],
                    "weather": ["sol","tempestade"],
                    "explore_actions": ["explorar","descer_cratera","resistir_calor","encontrar_abrigo"],
                },
                "mina_obsidiana": {
                    "name": "Mina de Obsidiana", "emoji": "⛏️",
                    "description": "Uma mina profunda onde se extraem cristais de obsidiana negra.",
                    "min_level": 38, "max_level": 52,
                    "pokemon_ids": [50,51,74,75,76,95,111,112],
                    "rarity_weights": {"comum":0.45,"raro":0.30,"epico":0.18,"lendario":0.05,"mitico":0.02},
                    "events": ["pokemon_wild","item_found","chest","cave_in","rare_mineral"],
                    "event_weights": [0.40,0.25,0.20,0.10,0.05],
                    "items": ["hyperpotion","ultraball","revive","rarecandy","fire_stone"],
                    "npcs": ["miner_boss"],
                    "weather": ["sol"],
                    "explore_actions": ["explorar","escavar","procurar_veios","descer_galeria"],
                },
            },
        },
        "drakoria": {
            "name": "Drakoria", "emoji": "🐉", "color": "drakoria",
            "description": "Terras ancestrais onde dragões governam os céus e a terra.",
            "climate": "mountain", "min_level": 45,
            "unlock_requirement": {"chapter": "capitulo_4"},
            "areas": {
                "ninho_celestial": {
                    "name": "Ninho Celestial", "emoji": "☁️",
                    "description": "Ninhos de dragões nas montanhas mais altas, tocando as nuvens.",
                    "min_level": 45, "max_level": 60,
                    "pokemon_ids": [6,130,142,148,149],
                    "rarity_weights": {"comum":0.30,"raro":0.30,"epico":0.25,"lendario":0.12,"mitico":0.03},
                    "events": ["pokemon_wild","item_found","chest","dragon_roar","celestial_egg"],
                    "event_weights": [0.35,0.20,0.20,0.15,0.10],
                    "items": ["hyperpotion","ultraball","masterball","rarecandy","dragon_scale"],
                    "npcs": ["ragnar"],
                    "weather": ["sol","tempestade","nevoa"],
                    "explore_actions": ["explorar","escalar","observar_ninhos","escutar_rugido"],
                },
                "picos_ancioes": {
                    "name": "Picos dos Anciões", "emoji": "🏔️",
                    "description": "Picos sagrados onde anciões dragões descansam eternamente.",
                    "min_level": 50, "max_level": 65,
                    "pokemon_ids": [6,130,142,148,149],
                    "rarity_weights": {"comum":0.25,"raro":0.28,"epico":0.27,"lendario":0.15,"mitico":0.05},
                    "events": ["pokemon_wild","item_found","chest","ancient_dragon","dragon_bone"],
                    "event_weights": [0.30,0.20,0.20,0.18,0.12],
                    "items": ["hyperpotion","ultraball","masterball","rarecandy","dragon_scale","ancient_egg"],
                    "npcs": ["dragon_elder"],
                    "weather": ["sol","tempestade","nevoa"],
                    "explore_actions": ["explorar","meditar","honrar_ancioes","procurar_reliquias"],
                },
                "vale_tempestade": {
                    "name": "Vale da Tempestade", "emoji": "⛈️",
                    "description": "Um vale onde tempestades elétricas nunca cessam.",
                    "min_level": 48, "max_level": 62,
                    "pokemon_ids": [25,26,125,135,145],
                    "rarity_weights": {"comum":0.30,"raro":0.28,"epico":0.25,"lendario":0.13,"mitico":0.04},
                    "events": ["pokemon_wild","item_found","chest","thunder_strike","storm_eye"],
                    "event_weights": [0.35,0.20,0.20,0.15,0.10],
                    "items": ["hyperpotion","ultraball","masterball","rarecandy","thunder_stone"],
                    "npcs": ["volt"],
                    "weather": ["tempestade","sol"],
                    "explore_actions": ["explorar","enfrentar_tempestade","coletar_raios","buscar_abrigo"],
                },
            },
        },
        "lumina": {
            "name": "Lumina", "emoji": "🏰", "color": "lumina",
            "description": "A capital de Elyndra, centro de civilização e poder.",
            "climate": "temperate", "min_level": 1,
            "unlock_requirement": None,
            "areas": {
                "centro_liga": {
                    "name": "Centro da Liga", "emoji": "🏛️",
                    "description": "O coração da Liga Pokémon de Elyndra.",
                    "min_level": 1, "max_level": 100,
                    "pokemon_ids": [],
                    "rarity_weights": {},
                    "events": ["heal_pokemon","gym_challenge","register_battle"],
                    "event_weights": [0.50,0.30,0.20],
                    "items": [],
                    "npcs": ["aether"],
                    "weather": ["sol"],
                    "explore_actions": ["curar_pokemon","desafiar_ginasio","registrar_batalha","visitar_hall"],
                },
                "mercado_mundial": {
                    "name": "Mercado Mundial", "emoji": "🏪",
                    "description": "O maior mercado de Elyndra, onde tudo pode ser encontrado.",
                    "min_level": 1, "max_level": 100,
                    "pokemon_ids": [],
                    "rarity_weights": {},
                    "events": ["shop_visit","auction","mysterious_merchant","trade_center"],
                    "event_weights": [0.40,0.25,0.20,0.15],
                    "items": [],
                    "npcs": ["merchant_king"],
                    "weather": ["sol"],
                    "explore_actions": ["comprar","vender","participar_leilao","trocar"],
                },
                "arena_campeoes": {
                    "name": "Arena dos Campeões", "emoji": "⚔️",
                    "description": "A arena onde os melhores treinadores duelam.",
                    "min_level": 30, "max_level": 100,
                    "pokemon_ids": [],
                    "rarity_weights": {},
                    "events": ["pvp_challenge","tournament","ranked_match","spectate"],
                    "event_weights": [0.35,0.25,0.25,0.15],
                    "items": [],
                    "npcs": ["arena_master"],
                    "weather": ["sol"],
                    "explore_actions": ["desafiar","torneio","ranqueada","assistir"],
                },
                "biblioteca_lendarios": {
                    "name": "Biblioteca dos Lendários", "emoji": "📚",
                    "description": "Uma biblioteca imensa com registros de todos os Pokémon lendários.",
                    "min_level": 20, "max_level": 100,
                    "pokemon_ids": [],
                    "rarity_weights": {},
                    "events": ["read_lore","research_pokemon","discover_clue","ancient_map"],
                    "event_weights": [0.30,0.25,0.25,0.20],
                    "items": [],
                    "npcs": ["lore_master"],
                    "weather": ["sol"],
                    "explore_actions": ["ler_lore","pesquisar","descobrir_pista","estudar_mapa"],
                },
            },
        },
    },
}

# ═══════════════════════════════════════════════════════════════
# 👤 TREINADORES IMPORTANTES (NPCs)
# ═══════════════════════════════════════════════════════════════

IMPORTANT_TRAINERS = {
    "liora": {
        "name": "Liora", "title": "Guardiã do Bosque", "specialization": "grass",
        "emoji": "🌿", "location": "verdalia", "area": "bosque_esmeralda",
        "difficulty": "easy", "min_level": 10, "max_level": 18, "team_size": 3,
        "pokemon_pool": [1,2,3,43,44,45,46,47,69,70,71,102,103,114],
        "strategy": "defensive",
        "dialogue": {
            "greeting": "Bem-vindo ao Bosque Esmeralda! A natureza é nossa aliada mais forte.",
            "defeat": "Você realmente entende o poder da natureza. Tome, esta insígnia é sua.",
            "victory": "A natureza sempre prevalece. Volte quando estiver mais forte, jovem treinador.",
        },
        "rewards": {"coins": 500, "xp": 300, "badge": "insignia_floresta", "items": ["greatball","potion","rarecandy"]},
    },
    "kael": {
        "name": "Kael", "title": "Senhor das Chamas", "specialization": "fire",
        "emoji": "🔥", "location": "vulkar", "area": "vale_cinzas",
        "difficulty": "medium", "min_level": 35, "max_level": 45, "team_size": 4,
        "pokemon_pool": [4,5,6,37,38,58,59,77,78,126],
        "strategy": "aggressive",
        "dialogue": {
            "greeting": "HAHA! Sinta o calor da minha paixão! Meus Pokémon de fogo vão incinerar tudo!",
            "defeat": "Incrível... Você superou minhas chamas. Aqui, leve a Insígnia do Vulcão.",
            "victory": "As chamas nunca morrem! Volte quando puder suportar o calor, fraco!",
        },
        "rewards": {"coins": 1200, "xp": 800, "badge": "insignia_vulcao", "items": ["ultraball","hyperpotion","fire_stone"]},
    },
    "nerys": {
        "name": "Nerys", "title": "Dama das Profundezas", "specialization": "water",
        "emoji": "🌊", "location": "frostvale", "area": "lago_cristalino",
        "difficulty": "medium", "min_level": 20, "max_level": 30, "team_size": 3,
        "pokemon_pool": [54,55,60,61,62,72,73,86,87,90,91,116,117,118,119,120,121,124,131],
        "strategy": "balanced",
        "dialogue": {
            "greeting": "As águas de Frostvale são frias, mas minha determinação é de ferro.",
            "defeat": "Você navegou habilmente pelas minhas ondas. A Insígnia do Gelo é sua.",
            "victory": "As marés estão ao meu favor hoje. Treine mais antes de me desafiar novamente.",
        },
        "rewards": {"coins": 800, "xp": 500, "badge": "insignia_gelo", "items": ["greatball","superpotion","water_stone"]},
    },
    "volt": {
        "name": "Volt", "title": "Mestre do Trovão", "specialization": "electric",
        "emoji": "⚡", "location": "drakoria", "area": "vale_tempestade",
        "difficulty": "hard", "min_level": 48, "max_level": 58, "team_size": 4,
        "pokemon_pool": [25,26,125,135,145],
        "strategy": "speed",
        "dialogue": {
            "greeting": "⚡ ZAP! Você não verá meus ataques chegando! Sou rápido como um raio!",
            "defeat": "⚡ Uau... Você foi mais rápido que o trovão! Aqui está a Insígnia do Trovão.",
            "victory": "⚡ Muito lento! Volte quando puder acompanhar minha velocidade!",
        },
        "rewards": {"coins": 1500, "xp": 1000, "badge": "insignia_trovao", "items": ["ultraball","hyperpotion","thunder_stone"]},
    },
    "ragnar": {
        "name": "Ragnar", "title": "Mestre dos Dragões", "specialization": "dragon",
        "emoji": "🐉", "location": "drakoria", "area": "ninho_celestial",
        "difficulty": "very_hard", "min_level": 55, "max_level": 70, "team_size": 5,
        "pokemon_pool": [6,130,142,148,149],
        "strategy": "legendary",
        "dialogue": {
            "greeting": "🐉 Poucos ousam pisar no território dos dragões. Prove seu valor, mortal.",
            "defeat": "🐉 Impressionante... Você tem o espírito de um verdadeiro dragão. A Insígnia do Dragão é sua.",
            "victory": "🐉 Os dragões não se curvam a ninguém. Volte quando tiver o poder de um verdadeiro mestre.",
        },
        "rewards": {"coins": 3000, "xp": 2000, "badge": "insignia_dragao", "items": ["masterball","rarecandy","dragon_scale"]},
    },
    "aether": {
        "name": "Aether", "title": "Campeão de Elyndra", "specialization": "mixed",
        "emoji": "👑", "location": "lumina", "area": "centro_liga",
        "difficulty": "champion", "min_level": 70, "max_level": 85, "team_size": 6,
        "pokemon_pool": [3,6,9,38,59,65,76,94,112,130,131,143,149],
        "strategy": "champion",
        "dialogue": {
            "greeting": "👑 Bem-vindo ao Hall da Fama. Eu sou Aether, Campeão de Elyndra. Mostre-me o poder da sua jornada!",
            "defeat": "👑 Inacreditável... Você superou todas as minhas expectativas. Você é o novo Campeão de Elyndra!",
            "victory": "👑 Ainda há muito para aprender, jovem treinador. A jornada é longa, mas a recompensa é eterna.",
        },
        "rewards": {"coins": 10000, "xp": 5000, "badge": "insignia_campeao", "items": ["masterball","rarecandy","rarecandy","rarecandy","shiny_charm"], "title": "Campeão de Elyndra"},
    },
}

# ═══════════════════════════════════════════════════════════════
# 🏅 GINÁSIOS
# ═══════════════════════════════════════════════════════════════

GYMS = {
    "ginasio_floresta": {"name": "Ginásio da Floresta", "emoji": "🌿", "region": "verdalia", "area": "bosque_esmeralda", "leader": "liora", "type": "grass", "badge": "insignia_floresta", "badge_emoji": "🌿", "min_level": 10, "description": "Um ginásio escondido entre as árvores do Bosque Esmeralda.", "rewards": {"coins": 500, "xp": 300, "items": ["greatball","potion","rarecandy"]}},
    "ginasio_gelo": {"name": "Ginásio do Gelo", "emoji": "❄️", "region": "frostvale", "area": "lago_cristalino", "leader": "nerys", "type": "water", "badge": "insignia_gelo", "badge_emoji": "❄️", "min_level": 20, "description": "Um ginásio construído sobre o Lago Cristalino congelado.", "rewards": {"coins": 800, "xp": 500, "items": ["greatball","superpotion","water_stone"]}},
    "ginasio_vulcao": {"name": "Ginásio do Vulcão", "emoji": "🔥", "region": "vulkar", "area": "vale_cinzas", "leader": "kael", "type": "fire", "badge": "insignia_vulcao", "badge_emoji": "🔥", "min_level": 35, "description": "Um ginásio forjado no coração do vulcão ativo.", "rewards": {"coins": 1200, "xp": 800, "items": ["ultraball","hyperpotion","fire_stone"]}},
    "ginasio_trovao": {"name": "Ginásio do Trovão", "emoji": "⚡", "region": "drakoria", "area": "vale_tempestade", "leader": "volt", "type": "electric", "badge": "insignia_trovao", "badge_emoji": "⚡", "min_level": 48, "description": "Um ginásio onde raios caem sem parar, testando a coragem dos desafiantes.", "rewards": {"coins": 1500, "xp": 1000, "items": ["ultraball","hyperpotion","thunder_stone"]}},
    "ginasio_dragao": {"name": "Ginásio do Dragão", "emoji": "🐉", "region": "drakoria", "area": "ninho_celestial", "leader": "ragnar", "type": "dragon", "badge": "insignia_dragao", "badge_emoji": "🐉", "min_level": 55, "description": "O ginásio mais temido de Elyndra, guardado por verdadeiros dragões.", "rewards": {"coins": 3000, "xp": 2000, "items": ["masterball","rarecandy","dragon_scale"]}},
    "ginasio_campeao": {"name": "Ginásio do Campeão", "emoji": "👑", "region": "lumina", "area": "centro_liga", "leader": "aether", "type": "mixed", "badge": "insignia_campeao", "badge_emoji": "👑", "min_level": 70, "description": "O desafio final. Apenas treinadores com todas as insígnias podem entrar.", "rewards": {"coins": 10000, "xp": 5000, "items": ["masterball","rarecandy","rarecandy","rarecandy","shiny_charm"], "title": "Campeão de Elyndra"}},
}

# ═══════════════════════════════════════════════════════════════
# 🌦 SISTEMA DE CLIMA
# ═══════════════════════════════════════════════════════════════

WEATHER_SYSTEM = {
    "sol": {"name": "Ensolarado", "emoji": "☀️", "description": "O sol brilha forte. Pokémon de fogo e planta estão mais ativos.", "type_bonus": ["fire","grass"], "type_penalty": ["water","ice"], "catch_modifier": 1.0, "spawn_rate": 1.2},
    "chuva": {"name": "Chuvoso", "emoji": "🌧️", "description": "A chuva cai suavemente. Pokémon de água e elétrico aparecem mais.", "type_bonus": ["water","electric"], "type_penalty": ["fire","ground"], "catch_modifier": 1.1, "spawn_rate": 1.3},
    "tempestade": {"name": "Tempestade", "emoji": "⛈️", "description": "Uma tempestade feroz! Pokémon elétrico e voador dominam.", "type_bonus": ["electric","flying"], "type_penalty": ["bug","grass"], "catch_modifier": 0.8, "spawn_rate": 1.5},
    "neve": {"name": "Nevando", "emoji": "🌨️", "description": "A neve cobre tudo. Pokémon de gelo estão em seu elemento.", "type_bonus": ["ice"], "type_penalty": ["fire","grass"], "catch_modifier": 0.9, "spawn_rate": 1.2},
    "nevoa": {"name": "Neblina", "emoji": "🌫️", "description": "Uma névoa densa limita a visão. Pokémon fantasma e psíquico surgem.", "type_bonus": ["ghost","psychic"], "type_penalty": ["flying","bug"], "catch_modifier": 0.85, "spawn_rate": 1.1},
}

# ═══════════════════════════════════════════════════════════════
# 📜 MISSÕES E HISTÓRIA
# ═══════════════════════════════════════════════════════════════

STORY_CHAPTERS = {
    "capitulo_1": {"name": "Capítulo 1 — O Primeiro Passo", "emoji": "📖", "description": "Sua jornada começa em Verdália. Capture seus primeiros Pokémon e prove seu valor.", "requirements": {"catches_in_region": {"verdalia": 3}}, "rewards": {"coins": 500, "xp": 300, "items": ["pokeball","pokeball","potion"]}, "unlock_region": "frostvale"},
    "capitulo_2": {"name": "Capítulo 2 — O Despertar dos Elementos", "emoji": "📖", "description": "Eventos estranhos estão ocorrendo em Frostvale. Investigue o que está acontecendo.", "requirements": {"explore_area": {"frostvale": ["lago_cristalino","pico_vento_branco"]}, "defeat_trainer": ["nerys"]}, "rewards": {"coins": 800, "xp": 500, "items": ["greatball","superpotion","water_stone"]}, "unlock_region": "mareazul"},
    "capitulo_3": {"name": "Capítulo 3 — A Sombra Ancestral", "emoji": "📖", "description": "Descubra a origem dos Pokémon lendários que têm aparecido em Elyndra.", "requirements": {"explore_area": {"drakoria": ["ninho_celestial"]}, "catch_rarity": ["lendario"]}, "rewards": {"coins": 2000, "xp": 1500, "items": ["ultraball","ultraball","rarecandy","rarecandy"]}, "unlock_region": "vulkar"},
    "capitulo_4": {"name": "Capítulo 4 — O Coração do Vulcão", "emoji": "📖", "description": "O vulcão de Vulkar está prestes a entrar em erupção. Pare a catástrofe.", "requirements": {"explore_area": {"vulkar": ["vale_cinzas","cratera_escarlate"]}, "defeat_trainer": ["kael"]}, "rewards": {"coins": 3000, "xp": 2000, "items": ["ultraball","masterball","fire_stone","rarecandy"]}, "unlock_region": "drakoria"},
    "capitulo_5": {"name": "Capítulo 5 — O Campeão de Elyndra", "emoji": "📖", "description": "O desafio final. Enfrente Aether e torne-se o Campeão de Elyndra.", "requirements": {"defeat_trainer": ["aether"], "badges": ["insignia_floresta","insignia_gelo","insignia_vulcao","insignia_trovao","insignia_dragao"]}, "rewards": {"coins": 10000, "xp": 5000, "items": ["masterball","masterball","rarecandy","rarecandy","rarecandy","shiny_charm"], "title": "Campeão de Elyndra"}, "unlock_region": None},
}

DAILY_QUESTS = [
    {"name": "Caçador Iniciante", "type": "daily", "description": "Capture 3 Pokémon", "requirement": {"catches": 3}, "reward": {"coins": 300, "xp": 100}},
    {"name": "Treinador Dedicado", "type": "daily", "description": "Vença 2 batalhas", "requirement": {"wins": 2}, "reward": {"coins": 500, "xp": 150}},
    {"name": "Explorador", "type": "daily", "description": "Explore 5 áreas diferentes", "requirement": {"explores": 5}, "reward": {"coins": 200, "xp": 80}},
    {"name": "Colecionador", "type": "daily", "description": "Adicione 1 Pokémon ao time", "requirement": {"team_add": 1}, "reward": {"coins": 400, "xp": 120}},
    {"name": "Comerciante", "type": "daily", "description": "Compre 1 item na loja", "requirement": {"shop_buy": 1}, "reward": {"coins": 250, "xp": 60}},
    {"name": "Amigo dos Pokémon", "type": "daily", "description": "Alimente ou brinque com seus Pokémon 3 vezes", "requirement": {"friendship_actions": 3}, "reward": {"coins": 350, "xp": 100}},
    {"name": "Desafiante de Ginásio", "type": "daily", "description": "Desafie 1 ginásio", "requirement": {"gym_challenges": 1}, "reward": {"coins": 600, "xp": 200}},
]

# ═══════════════════════════════════════════════════════════════
# 🎴 CARTAS DE MELHORIA
# ═══════════════════════════════════════════════════════════════

UPGRADE_CARDS = {
    "attack_card": {"name": "Carta da Força", "effect": {"attack": 10}, "rarity": "comum", "description": "+10 de Ataque", "emoji": "⚔️"},
    "defense_card": {"name": "Carta da Muralha", "effect": {"defense": 10}, "rarity": "comum", "description": "+10 de Defesa", "emoji": "🛡️"},
    "speed_card": {"name": "Carta do Relâmpago", "effect": {"speed": 10}, "rarity": "comum", "description": "+10 de Velocidade", "emoji": "⚡"},
    "hp_card": {"name": "Carta Vital", "effect": {"hp": 20}, "rarity": "comum", "description": "+20 de HP", "emoji": "❤️"},
    "xp_card": {"name": "Carta da Ascensão", "effect": {"xp": 100}, "rarity": "raro", "description": "+100 de XP", "emoji": "🌟"},
    "potential_card": {"name": "Carta do Potencial", "effect": {"attack": 5, "defense": 5, "speed": 5, "hp": 10}, "rarity": "epico", "description": "Aumenta todos os atributos", "emoji": "💎"},
    "royal_card": {"name": "Carta Real", "effect": {"attack": 15, "defense": 15, "speed": 15, "hp": 30}, "rarity": "lendario", "description": "Bônus gerais poderosos", "emoji": "👑"},
    "crit_card": {"name": "Carta Crítica", "effect": {"crit_chance": 5}, "rarity": "epico", "description": "+5% chance de crítico", "emoji": "💥"},
    "shiny_charm": {"name": "Amuleto Shiny", "effect": {"shiny_chance": 2}, "rarity": "lendario", "description": "Dobra chance de Shiny", "emoji": "✨"},
    "master_fragment": {"name": "Fragmento Mestre", "effect": {"all": 5}, "rarity": "mitico", "description": "+5 em todos os atributos", "emoji": "🌌"},
    "celestial_fragment": {"name": "Fragmento Celestial", "effect": {"all": 10, "shiny_chance": 1}, "rarity": "mitico", "description": "Item lendário para evoluções especiais", "emoji": "🌌"},
}

# ═══════════════════════════════════════════════════════════════
# 🎒 ITENS DA LOJA
# ═══════════════════════════════════════════════════════════════

SHOP_ITEMS = {
    "pokeball": {"name": "Poké Ball", "price": 200, "description": "Bola básica para capturar Pokémon", "emoji": "⚪"},
    "greatball": {"name": "Great Ball", "price": 600, "description": "Bola com melhor taxa de captura", "emoji": "🔵"},
    "ultraball": {"name": "Ultra Ball", "price": 1200, "description": "Bola com excelente taxa de captura", "emoji": "🟡"},
    "masterball": {"name": "Master Ball", "price": 50000, "description": "Captura garantida (exceto lendários)", "emoji": "🔴"},
    "potion": {"name": "Poção", "price": 300, "description": "Recupera 20 HP", "emoji": "🧪"},
    "superpotion": {"name": "Super Poção", "price": 700, "description": "Recupera 50 HP", "emoji": "🧪"},
    "hyperpotion": {"name": "Hiper Poção", "price": 1500, "description": "Recupera 200 HP", "emoji": "🧪"},
    "maxpotion": {"name": "Poção Máxima", "price": 3000, "description": "Recupera todo o HP", "emoji": "🧪"},
    "revive": {"name": "Reviver", "price": 2000, "description": "Revive um Pokémon com metade do HP", "emoji": "💊"},
    "maxrevive": {"name": "Reviver Máximo", "price": 5000, "description": "Revive um Pokémon com HP completo", "emoji": "💊"},
    "xattack": {"name": "X Ataque", "price": 500, "description": "Aumenta ataque em batalha", "emoji": "⚔️"},
    "xdefense": {"name": "X Defesa", "price": 500, "description": "Aumenta defesa em batalha", "emoji": "🛡️"},
    "rarecandy": {"name": "Doce Raro", "price": 3000, "description": "Aumenta 1 nível do Pokémon", "emoji": "🍬"},
    "mysterybox": {"name": "Caixa Misteriosa", "price": 1000, "description": "Contém um item ou Pokémon surpresa", "emoji": "📦"},
    "fire_stone": {"name": "Pedra do Fogo", "price": 5000, "description": "Faz certos Pokémon evoluírem", "emoji": "🔥"},
    "water_stone": {"name": "Pedra da Água", "price": 5000, "description": "Faz certos Pokémon evoluírem", "emoji": "💧"},
    "thunder_stone": {"name": "Pedra do Trovão", "price": 5000, "description": "Faz certos Pokémon evoluírem", "emoji": "⚡"},
    "dragon_scale": {"name": "Escama de Dragão", "price": 8000, "description": "Item raro usado em evoluções especiais", "emoji": "🐉"},
    "ancient_egg": {"name": "Ovo Ancião", "price": 10000, "description": "Um ovo misterioso de um Pokémon antigo", "emoji": "🥚"},
    "dive_ball": {"name": "Dive Ball", "price": 1500, "description": "Melhor taxa de captura em áreas aquáticas", "emoji": "🔵"},
    "ice_heal": {"name": "Cura de Gelo", "price": 400, "description": "Cura congelamento", "emoji": "❄️"},
    "burn_heal": {"name": "Cura de Queimadura", "price": 400, "description": "Cura queimadura", "emoji": "🔥"},
    "antidote": {"name": "Antídoto", "price": 300, "description": "Cura envenenamento", "emoji": "☠️"},
    "elixir": {"name": "Elixir", "price": 2500, "description": "Restaura energia de ataques especiais", "emoji": "🔮"},
    "max_elixir": {"name": "Elixir Máximo", "price": 5000, "description": "Restaura toda a energia de ataques especiais", "emoji": "🔮"},
}

# ═══════════════════════════════════════════════════════════════
# ❤️ SISTEMA DE AMIZADE E PERSONALIDADE
# ═══════════════════════════════════════════════════════════════

FRIENDSHIP_LEVELS = [
    {"name": "Estranho", "min_points": 0, "emoji": "❓"},
    {"name": "Conhecido", "min_points": 20, "emoji": "🤝"},
    {"name": "Amigo", "min_points": 50, "emoji": "😊"},
    {"name": "Companheiro", "min_points": 100, "emoji": "💝"},
    {"name": "Melhor Amigo", "min_points": 200, "emoji": "💖"},
    {"name": "Alma Gêmea", "min_points": 500, "emoji": "💕"},
]

FRIENDSHIP_ACTIONS = {
    "feed": {"name": "Alimentar", "emoji": "🍎", "points": 5, "cooldown": 3600, "description": "Dê uma fruta ou berry ao seu Pokémon"},
    "play": {"name": "Brincar", "emoji": "🎾", "points": 8, "cooldown": 3600, "description": "Brinque com seu Pokémon por um tempo"},
    "train": {"name": "Treinar", "emoji": "💪", "points": 10, "cooldown": 7200, "description": "Treine habilidades específicas"},
    "pet": {"name": "Carinho", "emoji": "🤗", "points": 3, "cooldown": 1800, "description": "Faça carinho no seu Pokémon"},
    "camp": {"name": "Acampar", "emoji": "🏕️", "points": 15, "cooldown": 14400, "description": "Leve seu Pokémon para acampar"},
}

POKEMON_PERSONALITIES = {
    "agressivo": {"name": "Agressivo", "emoji": "😤", "bonus": {"attack": 1.15, "defense": 0.95, "speed": 1.05}, "description": "Ataca com ferocidade, mas deixa a defesa exposta."},
    "calmo": {"name": "Calmo", "emoji": "😌", "bonus": {"attack": 0.95, "defense": 1.15, "speed": 0.95}, "description": "Mantém a compostura, aumentando a defesa."},
    "rapido": {"name": "Rápido", "emoji": "⚡", "bonus": {"attack": 1.0, "defense": 0.95, "speed": 1.15}, "description": "Extremamente veloz, ataca antes dos oponentes."},
    "inteligente": {"name": "Inteligente", "emoji": "🧠", "bonus": {"attack": 1.05, "defense": 1.05, "speed": 1.0, "crit_chance": 5}, "description": "Usa táticas inteligentes, aumentando precisão e críticos."},
    "brincalhao": {"name": "Brincalhão", "emoji": "😜", "bonus": {"attack": 1.0, "defense": 1.0, "speed": 1.1, "dodge_chance": 5}, "description": "Esquivo e imprevisível, difícil de acertar."},
    "leal": {"name": "Leal", "emoji": "🛡️", "bonus": {"attack": 1.0, "defense": 1.1, "speed": 1.0, "friendship_gain": 1.5}, "description": "Leal ao treinador, ganha amizade mais rápido."},
    "solitario": {"name": "Solitário", "emoji": "🌑", "bonus": {"attack": 1.1, "defense": 1.0, "speed": 1.0, "xp_gain": 1.2}, "description": "Prefere lutar sozinho, ganha mais XP em batalhas."},
    "corajoso": {"name": "Corajoso", "emoji": "🦁", "bonus": {"attack": 1.1, "defense": 1.1, "speed": 0.9}, "description": "Nunca recua, mas é um pouco lento."},
}

# ═══════════════════════════════════════════════════════════════
# 🥚 SISTEMA DE OVOS
# ═══════════════════════════════════════════════════════════════

EGG_SYSTEM = {
    "common_egg": {"name": "Ovo Comum", "emoji": "🥚", "hatch_time": 3600, "rarity_weights": {"comum": 0.70, "raro": 0.25, "epico": 0.05}, "description": "Um ovo comum. Pode conter um Pokémon interessante."},
    "rare_egg": {"name": "Ovo Raro", "emoji": "🥚", "hatch_time": 7200, "rarity_weights": {"raro": 0.60, "epico": 0.30, "lendario": 0.10}, "description": "Um ovo raro brilhante."},
    "legendary_egg": {"name": "Ovo Lendário", "emoji": "🥚", "hatch_time": 14400, "rarity_weights": {"epico": 0.50, "lendario": 0.40, "mitico": 0.10}, "description": "Um ovo que pulsa com energia lendária."},
    "ancient_egg": {"name": "Ovo Ancião", "emoji": "🥚", "hatch_time": 21600, "rarity_weights": {"lendario": 0.60, "mitico": 0.40}, "description": "Um ovo de eras passadas. Contém um poder imenso."},
}

# ═══════════════════════════════════════════════════════════════
# 👥 SISTEMA DE CLÃS
# ═══════════════════════════════════════════════════════════════

CLAN_ROLES = {
    "leader": {"name": "Líder", "emoji": "👑", "permissions": ["invite", "kick", "promote", "disband", "manage_bank", "start_raid"]},
    "officer": {"name": "Oficial", "emoji": "⭐", "permissions": ["invite", "kick", "start_raid"]},
    "member": {"name": "Membro", "emoji": "🛡️", "permissions": ["participate_raid", "donate"]},
    "recruit": {"name": "Recruta", "emoji": "🌱", "permissions": ["participate_raid"]},
}

# ═══════════════════════════════════════════════════════════════
# 🌋 SISTEMA DE RAID
# ═══════════════════════════════════════════════════════════════

RAID_BOSSES = {
    "tyranitar_giant": {
        "name": "Tyranitar Gigante", "emoji": "🌋", "type": "rock",
        "hp": 5000, "attack": 200, "defense": 180, "speed": 80,
        "description": "Um Tyranitar colossal que devastou montanhas inteiras.",
        "location": "vulkar", "area": "cratera_escarlate",
        "rewards": {"coins": 5000, "xp": 3000, "items": ["rarecandy","dragon_scale","royal_card"]},
        "duration_minutes": 30,
    },
    "gyarados_leviathan": {
        "name": "Gyarados Leviatã", "emoji": "🌊", "type": "water",
        "hp": 4500, "attack": 220, "defense": 150, "speed": 100,
        "description": "Um Gyarados do tamanho de uma ilha inteira.",
        "location": "mareazul", "area": "abismo_azul",
        "rewards": {"coins": 4500, "xp": 2500, "items": ["rarecandy","water_stone","royal_card"]},
        "duration_minutes": 30,
    },
    "articuno_frost": {
        "name": "Articuno de Gelo Eterno", "emoji": "❄️", "type": "ice",
        "hp": 4000, "attack": 180, "defense": 200, "speed": 120,
        "description": "Um Articuno lendário cuja asa esquerda congela o tempo.",
        "location": "frostvale", "area": "pico_vento_branco",
        "rewards": {"coins": 4000, "xp": 2000, "items": ["rarecandy","ice_heal","shiny_charm"]},
        "duration_minutes": 25,
    },
    "mewtwo_psychic": {
        "name": "Mewtwo Psíquico Supremo", "emoji": "🔮", "type": "psychic",
        "hp": 6000, "attack": 250, "defense": 150, "speed": 150,
        "description": "Mewtwo em sua forma mais poderosa. A mente dele pode destruir cidades.",
        "location": "lumina", "area": "biblioteca_lendarios",
        "rewards": {"coins": 8000, "xp": 5000, "items": ["masterball","celestial_fragment","royal_card"]},
        "duration_minutes": 40,
    },
}

# ═══════════════════════════════════════════════════════════════
# TIPOS DE POKÉMON E VANTAGENS
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# NATURES E SEUS EFEITOS
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# GOLPES POR TIPO
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# RANKS DE TREINADOR
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# ESPECIALIZAÇÕES DE TREINADOR
# ═══════════════════════════════════════════════════════════════

SPECIALIZATIONS = {
    "capturador": {"name": "Capturador", "bonus": {"catch_rate": 0.1, "xp_catch": 1.2}, "description": "Maior chance de captura e mais XP"},
    "batalhador": {"name": "Batalhador", "bonus": {"attack": 1.1, "xp_battle": 1.3}, "description": "Mais ataque e XP em batalhas"},
    "tank": {"name": "Tanque", "bonus": {"defense": 1.15, "hp": 1.1}, "description": "Mais defesa e HP"},
    "velocista": {"name": "Velocista", "bonus": {"speed": 1.2, "crit_chance": 5}, "description": "Mais velocidade e chance de crítico"},
    "estrategista": {"name": "Estrategista", "bonus": {"type_advantage": 1.2, "dodge_chance": 5}, "description": "Vantagem de tipo aumentada e esquiva"},
}
