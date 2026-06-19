"""
Utilitários visuais e funções auxiliares para o Bot Pokémon — MUNDO VIVO RPG
"""
import math
import random
from config import COLORS, EMOJIS, TYPE_EFFECTIVENESS, NATURES, TRAINER_RANKS, BASE_XP, XP_MULTIPLIER, WEATHER_SYSTEM, FRIENDSHIP_LEVELS, POKEMON_PERSONALITIES

def calculate_xp_for_level(level):
    return int(BASE_XP * (level ** XP_MULTIPLIER))

def calculate_level_from_xp(xp):
    level = 1
    while xp >= calculate_xp_for_level(level + 1):
        level += 1
    return level

def get_rank(level):
    for rank in reversed(TRAINER_RANKS):
        if level >= rank["min_level"]:
            return rank
    return TRAINER_RANKS[0]

def create_progress_bar(current, maximum, length=10, filled="█", empty="░"):
    if maximum <= 0:
        return filled * length
    ratio = min(current / maximum, 1.0)
    filled_length = int(length * ratio)
    return filled * filled_length + empty * (length - filled_length)

def create_hp_bar(current_hp, max_hp):
    ratio = current_hp / max_hp if max_hp > 0 else 0
    if ratio > 0.5:
        filled = "🟢"
    elif ratio > 0.25:
        filled = "🟡"
    else:
        filled = "🔴"
    bar = create_progress_bar(current_hp, max_hp, 10, filled, "⬛")
    return f"{bar} {current_hp}/{max_hp}"

def create_xp_bar(current_xp, level):
    xp_for_current = calculate_xp_for_level(level)
    xp_for_next = calculate_xp_for_level(level + 1)
    xp_needed = xp_for_next - xp_for_current
    xp_progress = current_xp - xp_for_current
    bar = create_progress_bar(xp_progress, xp_needed, 12, "▰", "▱")
    return f"{bar} {xp_progress}/{xp_needed} XP"

def create_friendship_bar(friendship_points):
    max_points = 500
    bar = create_progress_bar(friendship_points, max_points, 10, "💖", "🖤")
    level = get_friendship_level(friendship_points)
    return f"{bar} {friendship_points}/{max_points} ({level['emoji']} {level['name']})"

def get_friendship_level(points):
    for level in reversed(FRIENDSHIP_LEVELS):
        if points >= level["min_points"]:
            return level
    return FRIENDSHIP_LEVELS[0]

def get_type_emoji(pokemon_type):
    type_emojis = {
        "normal": "⚪", "fire": "🔥", "water": "💧", "grass": "🌿",
        "electric": "⚡", "ice": "❄️", "fighting": "👊", "poison": "☠️",
        "ground": "🌍", "flying": "🦅", "psychic": "🔮", "bug": "🐛",
        "rock": "🪨", "ghost": "👻", "dragon": "🐉", "dark": "🌑",
        "steel": "⚙️", "fairy": "🧚",
    }
    return type_emojis.get(pokemon_type.lower(), "✦")

def get_rarity_emoji(rarity):
    rarity_emojis = {"comum": "☆", "raro": "★", "epico": "◆", "lendario": "❖", "mitico": "✦"}
    return rarity_emojis.get(rarity.lower(), "☆")

def get_rarity_color(rarity):
    return COLORS.get(rarity.lower(), COLORS["comum"])

def format_rarity_name(rarity):
    names = {"comum": "Comum", "raro": "Raro", "epico": "Épico", "lendario": "Lendário", "mitico": "Mítico"}
    return names.get(rarity.lower(), rarity.capitalize())

def get_weather_emoji(weather):
    return WEATHER_SYSTEM.get(weather, {}).get("emoji", "🌤️")

def get_weather_name(weather):
    return WEATHER_SYSTEM.get(weather, {}).get("name", "Desconhecido")

def get_personality_emoji(personality):
    return POKEMON_PERSONALITIES.get(personality, {}).get("emoji", "🎭")

def get_personality_name(personality):
    return POKEMON_PERSONALITIES.get(personality, {}).get("name", "Desconhecido")

def calculate_type_effectiveness(attacker_type, defender_types):
    effectiveness = 1.0
    attacker_type = attacker_type.lower()
    if attacker_type in TYPE_EFFECTIVENESS:
        for defender_type in defender_types:
            defender_type = defender_type.lower()
            if defender_type in TYPE_EFFECTIVENESS[attacker_type]:
                effectiveness *= TYPE_EFFECTIVENESS[attacker_type][defender_type]
    return effectiveness

def get_effectiveness_text(effectiveness):
    if effectiveness == 0:
        return "❌ Sem efeito!"
    elif effectiveness < 1:
        return "▼ Não muito efetivo..."
    elif effectiveness > 1:
        return "▲ Super efetivo!"
    return ""

def calculate_damage(attacker, defender, move_power=50, is_critical=False):
    attack_stat = attacker.get("attack", 50)
    defense_stat = defender.get("defense", 50)
    nature = attacker.get("nature", "hardy")
    attack_mod = NATURES.get(nature, {}).get("attack", 1.0)
    level = attacker.get("level", 1)
    level_mod = 0.4 * level + 2
    damage = ((2 * level_mod * attack_stat * attack_mod) / (defense_stat * 0.5)) + 2
    damage *= (move_power / 100)
    damage *= random.uniform(0.85, 1.0)
    # Apply personality bonus
    personality = attacker.get("personality", "agressivo")
    if personality in POKEMON_PERSONALITIES:
        damage *= POKEMON_PERSONALITIES[personality]["bonus"].get("attack", 1.0)
    if is_critical:
        damage *= 1.5
    return max(1, int(damage))

def is_critical_hit(crit_chance=5):
    return random.randint(1, 100) <= crit_chance

def is_dodge(dodge_chance=5):
    return random.randint(1, 100) <= dodge_chance

def generate_nature():
    return random.choice(list(NATURES.keys()))

def generate_personality():
    return random.choice(list(POKEMON_PERSONALITIES.keys()))

def format_number(num):
    return f"{num:,}".replace(",", ".")

def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"

def get_pokemon_card_description(pokemon):
    rarity = pokemon.get("rarity", "comum")
    shiny = "✨ SHINY " if pokemon.get("is_shiny") else ""
    personality = pokemon.get("personality", "agressivo")
    friendship = pokemon.get("friendship", 0)
    desc = f"""
✦ ─────────────── ✦
{shiny}N.° {pokemon.get('pokedex_number', '???')} — {pokemon.get('name', 'Desconhecido')}
✦ ─────────────── ✦

{get_rarity_emoji(rarity)} {format_rarity_name(rarity)}
{get_type_emoji(pokemon.get('types', ['normal'])[0])} Tipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in pokemon.get('types', ['Normal'])])}
{get_personality_emoji(personality)} Personalidade: {get_personality_name(personality)}
{create_friendship_bar(friendship)}

❤ HP: {pokemon.get('hp', 0)}/{pokemon.get('max_hp', 0)}
⚔ Ataque: {pokemon.get('attack', 0)}
🛡 Defesa: {pokemon.get('defense', 0)}
💨 Velocidade: {pokemon.get('speed', 0)}

📊 Nível: {pokemon.get('level', 1)}
✨ XP: {pokemon.get('xp', 0)}

🎯 Vitórias: {pokemon.get('battle_wins', 0)} | Derrotas: {pokemon.get('battle_losses', 0)}
"""
    return desc

def truncate_text(text, max_length=100):
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def create_box_animation(steps=5):
    frames = []
    for i in range(steps + 1):
        filled = "█" * i
        empty = "░" * (steps - i)
        frames.append(f"[{filled}{empty}]")
    return frames

def get_random_move_for_type(pokemon_type):
    from config import MOVES_BY_TYPE
    moves = MOVES_BY_TYPE.get(pokemon_type.lower(), ["Tackle"])
    return random.choice(moves)

def get_region_emoji(region_id):
    from config import ELYNDRA_WORLD
    return ELYNDRA_WORLD["regions"].get(region_id, {}).get("emoji", "🌍")

def get_region_name(region_id):
    from config import ELYNDRA_WORLD
    return ELYNDRA_WORLD["regions"].get(region_id, {}).get("name", "Desconhecido")

def get_area_name(region_id, area_id):
    from config import ELYNDRA_WORLD
    region = ELYNDRA_WORLD["regions"].get(region_id, {})
    return region.get("areas", {}).get(area_id, {}).get("name", "Desconhecido")

def get_area_emoji(region_id, area_id):
    from config import ELYNDRA_WORLD
    region = ELYNDRA_WORLD["regions"].get(region_id, {})
    return region.get("areas", {}).get(area_id, {}).get("emoji", "📍")
