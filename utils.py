"""
Utilitários visuais e funções auxiliares para o Bot Pokémon
"""
import math
import random
from config import COLORS, EMOJIS, TYPE_EFFECTIVENESS, NATURES, TRAINER_RANKS, BASE_XP, XP_MULTIPLIER

def calculate_xp_for_level(level):
    """Calcula XP necessário para alcançar um nível"""
    return int(BASE_XP * (level ** XP_MULTIPLIER))

def calculate_level_from_xp(xp):
    """Calcula nível baseado no XP"""
    level = 1
    while xp >= calculate_xp_for_level(level + 1):
        level += 1
    return level

def get_rank(level):
    """Obtém rank baseado no nível"""
    for rank in reversed(TRAINER_RANKS):
        if level >= rank["min_level"]:
            return rank
    return TRAINER_RANKS[0]

def create_progress_bar(current, maximum, length=10, filled="█", empty="░"):
    """Cria uma barra de progresso visual"""
    if maximum <= 0:
        return filled * length
    ratio = min(current / maximum, 1.0)
    filled_length = int(length * ratio)
    return filled * filled_length + empty * (length - filled_length)

def create_hp_bar(current_hp, max_hp):
    """Cria barra de HP com cores"""
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
    """Cria barra de XP"""
    xp_for_current = calculate_xp_for_level(level)
    xp_for_next = calculate_xp_for_level(level + 1)
    xp_needed = xp_for_next - xp_for_current
    xp_progress = current_xp - xp_for_current

    bar = create_progress_bar(xp_progress, xp_needed, 12, "▰", "▱")
    return f"{bar} {xp_progress}/{xp_needed} XP"

def get_type_emoji(pokemon_type):
    """Retorna emoji do tipo"""
    type_emojis = {
        "normal": "⚪", "fire": "🔥", "water": "💧", "grass": "🌿",
        "electric": "⚡", "ice": "❄️", "fighting": "👊", "poison": "☠️",
        "ground": "🌍", "flying": "🦅", "psychic": "🔮", "bug": "🐛",
        "rock": "🪨", "ghost": "👻", "dragon": "🐉", "dark": "🌑",
        "steel": "⚙️", "fairy": "🧚",
    }
    return type_emojis.get(pokemon_type.lower(), "✦")

def get_rarity_emoji(rarity):
    """Retorna emoji da raridade"""
    rarity_emojis = {
        "comum": "☆",
        "raro": "★",
        "epico": "◆",
        "lendario": "❖",
        "mitico": "✦",
    }
    return rarity_emojis.get(rarity.lower(), "☆")

def get_rarity_color(rarity):
    """Retorna cor da raridade"""
    return COLORS.get(rarity.lower(), COLORS["comum"])

def format_rarity_name(rarity):
    """Formata nome da raridade"""
    names = {
        "comum": "Comum",
        "raro": "Raro",
        "epico": "Épico",
        "lendario": "Lendário",
        "mitico": "Mítico",
    }
    return names.get(rarity.lower(), rarity.capitalize())

def calculate_type_effectiveness(attacker_type, defender_types):
    """Calcula vantagem de tipo"""
    effectiveness = 1.0
    attacker_type = attacker_type.lower()

    if attacker_type in TYPE_EFFECTIVENESS:
        for defender_type in defender_types:
            defender_type = defender_type.lower()
            if defender_type in TYPE_EFFECTIVENESS[attacker_type]:
                effectiveness *= TYPE_EFFECTIVENESS[attacker_type][defender_type]

    return effectiveness

def get_effectiveness_text(effectiveness):
    """Retorna texto da efetividade"""
    if effectiveness == 0:
        return "❌ Sem efeito!"
    elif effectiveness < 1:
        return "▼ Não muito efetivo..."
    elif effectiveness > 1:
        return "▲ Super efetivo!"
    return ""

def calculate_damage(attacker, defender, move_power=50, is_critical=False):
    """Calcula dano de um ataque"""
    # Base damage formula
    attack_stat = attacker.get("attack", 50)
    defense_stat = defender.get("defense", 50)

    # Nature modifier
    nature = attacker.get("nature", "hardy")
    attack_mod = NATURES.get(nature, {}).get("attack", 1.0)

    # Level modifier
    level = attacker.get("level", 1)
    level_mod = 0.4 * level + 2

    # Base damage
    damage = ((2 * level_mod * attack_stat * attack_mod) / (defense_stat * 0.5)) + 2
    damage *= (move_power / 100)

    # Random factor (85-100%)
    damage *= random.uniform(0.85, 1.0)

    # Critical hit
    if is_critical:
        damage *= 1.5

    return max(1, int(damage))

def is_critical_hit(crit_chance=5):
    """Verifica se é crítico"""
    return random.randint(1, 100) <= crit_chance

def is_dodge(dodge_chance=5):
    """Verifica se esquivou"""
    return random.randint(1, 100) <= dodge_chance

def generate_nature():
    """Gera nature aleatória"""
    return random.choice(list(NATURES.keys()))

def format_number(num):
    """Formata número com separadores"""
    return f"{num:,}".replace(",", ".")

def format_time(seconds):
    """Formata tempo restante"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"

def get_pokemon_card_description(pokemon):
    """Gera descrição estilo carta para um Pokémon"""
    rarity = pokemon.get("rarity", "comum")
    shiny = "✨ SHINY " if pokemon.get("is_shiny") else ""

    desc = f"""
✦ ─────────────── ✦
{shiny}N.° {pokemon.get('pokedex_number', '???')} — {pokemon.get('name', 'Desconhecido')}
✦ ─────────────── ✦

Raridade: {get_rarity_emoji(rarity)} {format_rarity_name(rarity)}
Tipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in pokemon.get('types', ['Normal'])])}
Nature: {pokemon.get('nature', 'Hardy').capitalize()}

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
    """Trunca texto"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def create_box_animation(steps=5):
    """Gera frames de animação de abertura de caixa"""
    frames = []
    for i in range(steps + 1):
        filled = "█" * i
        empty = "░" * (steps - i)
        frames.append(f"[{filled}{empty}]")
    return frames

def get_random_move_for_type(pokemon_type):
    """Retorna um golpe aleatório do tipo"""
    from config import MOVES_BY_TYPE
    moves = MOVES_BY_TYPE.get(pokemon_type.lower(), ["Tackle"])
    return random.choice(moves)
