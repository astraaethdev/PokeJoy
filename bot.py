"""
Pokémon World — Bot Discord — MUNDO VIVO RPG
"""
import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
import asyncio
import random
import json
from datetime import datetime, timedelta

from config import (
    DISCORD_TOKEN, BOT_NAME, COLORS, XP_COOLDOWN_SECONDS, XP_PER_MESSAGE,
    XP_PER_CATCH, XP_PER_BATTLE_WIN, XP_PER_DAILY, XP_PER_EXPLORE, XP_PER_GYM_WIN,
    DAILY_COINS, STARTING_COINS, SHOP_ITEMS, UPGRADE_CARDS, DAILY_QUESTS,
    RARITY_CHANCES, MAX_TEAM_SIZE, BASE_CATCH_RATE,
    ELYNDRA_WORLD, WEATHER_SYSTEM, IMPORTANT_TRAINERS, GYMS,
    STORY_CHAPTERS, FRIENDSHIP_ACTIONS, POKEMON_PERSONALITIES,
    EGG_SYSTEM, RAID_BOSSES, CLAN_ROLES
)
from database import db
from pokeapi import pokeapi
from utils import (
    calculate_xp_for_level, calculate_level_from_xp, get_rank,
    create_hp_bar, create_xp_bar, get_type_emoji, get_rarity_emoji,
    get_rarity_color, format_rarity_name, calculate_type_effectiveness,
    get_effectiveness_text, calculate_damage, is_critical_hit, is_dodge,
    generate_nature, format_number, format_time, get_random_move_for_type,
    generate_personality, get_personality_emoji, get_personality_name,
    create_friendship_bar, get_friendship_level, get_weather_emoji,
    get_weather_name, get_region_emoji, get_region_name, get_area_name,
    get_area_emoji
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ═══════════════════════════════════════════════════════════════
# VARIÁVEIS GLOBAIS DO MUNDO
# ═══════════════════════════════════════════════════════════════

world_state = {
    "current_weather": {},  # guild_id -> weather
    "active_raids": {},     # raid_id -> raid_data
    "spawn_channels": {},   # guild_id -> channel_id
}

# ═══════════════════════════════════════════════════════════════
# EVENTOS DO BOT
# ═══════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    await db.init()
    await bot.tree.sync()
    print(f"✦ {BOT_NAME} online como {bot.user.name}")
    print(f"✦ ID: {bot.user.id}")
    print(f"✦ Servidores: {len(bot.guilds)}")

    # Iniciar loops de background
    daily_quest_reset.start()
    cleanup_battles.start()
    weather_cycle.start()
    wild_spawn_loop.start()
    raid_cycle.start()
    cleanup_spawns.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    user_id = message.author.id
    can_xp, remaining = await db.check_cooldown(user_id, "message_xp", XP_COOLDOWN_SECONDS)
    if can_xp:
        trainer = await db.get_trainer(user_id)
        if trainer:
            new_xp = trainer["xp"] + XP_PER_MESSAGE
            new_level = calculate_level_from_xp(new_xp)
            updates = {"xp": new_xp}
            if new_level > trainer["level"]:
                updates["level"] = new_level
                updates["rank"] = get_rank(new_level)["name"]
                await message.channel.send(
                    f"🎉 **{message.author.display_name}** subiu para o nível **{new_level}**! "
                    f"Novo rank: **{get_rank(new_level)['name']}** {get_rank(new_level)['emoji']}"
                )
            await db.update_trainer(user_id, **updates)

            # Atualizar progresso de missões
            await update_quest_progress(user_id, "messages", 1)
    await bot.process_commands(message)

# ═══════════════════════════════════════════════════════════════
# LOOPS DE BACKGROUND
# ═══════════════════════════════════════════════════════════════

@tasks.loop(hours=24)
async def daily_quest_reset():
    """Reseta missões diárias para todos os treinadores"""
    pass  # Implementado no comando /daily

@tasks.loop(minutes=5)
async def cleanup_battles():
    """Limpa batalhas expiradas"""
    pass

@tasks.loop(minutes=30)
async def weather_cycle():
    """Muda o clima de cada servidor periodicamente"""
    for guild in bot.guilds:
        weather_keys = list(WEATHER_SYSTEM.keys())
        new_weather = random.choice(weather_keys)
        world_state["current_weather"][guild.id] = new_weather

        # Notificar em canais configurados
        spawn_channel = world_state["spawn_channels"].get(guild.id)
        if spawn_channel:
            channel = bot.get_channel(spawn_channel)
            if channel:
                weather = WEATHER_SYSTEM[new_weather]
                embed = discord.Embed(
                    title=f"{weather['emoji']} Clima Mudou!",
                    description=f"O clima em Elyndra mudou para **{weather['name']}**!\n\n{weather['description']}",
                    color=COLORS.get(new_weather, COLORS["info"])
                )
                await channel.send(embed=embed)

@tasks.loop(minutes=15)
async def wild_spawn_loop():
    """Spawna Pokémon selvagens em canais configurados"""
    for guild_id, channel_id in world_state["spawn_channels"].items():
        channel = bot.get_channel(channel_id)
        if not channel:
            continue

        # Chance de spawn (30% a cada 15 min)
        if random.random() > 0.30:
            continue

        # Determinar região baseada no clima
        weather = world_state["current_weather"].get(guild_id, "sol")

        # Escolher região aleatória (ponderada por clima)
        if weather in ["neve", "nevoa"]:
            region_weights = {"verdalia": 0.2, "frostvale": 0.4, "mareazul": 0.1, "vulkar": 0.1, "drakoria": 0.1, "lumina": 0.1}
        elif weather == "tempestade":
            region_weights = {"verdalia": 0.2, "frostvale": 0.1, "mareazul": 0.3, "vulkar": 0.1, "drakoria": 0.2, "lumina": 0.1}
        elif weather == "sol":
            region_weights = {"verdalia": 0.3, "frostvale": 0.1, "mareazul": 0.2, "vulkar": 0.2, "drakoria": 0.1, "lumina": 0.1}
        else:
            region_weights = {"verdalia": 0.25, "frostvale": 0.15, "mareazul": 0.2, "vulkar": 0.15, "drakoria": 0.15, "lumina": 0.1}

        region_id = random.choices(list(region_weights.keys()), weights=list(region_weights.values()))[0]
        region = ELYNDRA_WORLD["regions"][region_id]

        # Escolher área aleatória
        area_id = random.choice(list(region["areas"].keys()))
        area = region["areas"][area_id]

        # Gerar Pokémon
        pokemon_ids = area.get("pokemon_ids", [])
        if not pokemon_ids:
            continue

        pokemon_id = random.choice(pokemon_ids)
        pokemon_data = await pokeapi.get_pokemon_data(pokemon_id)
        if not pokemon_data:
            continue

        # Aplicar raridade da área
        rarity_weights = area.get("rarity_weights", RARITY_CHANCES)
        pokemon_data["rarity"] = random.choices(list(rarity_weights.keys()), weights=list(rarity_weights.values()))[0]
        pokemon_data["is_shiny"] = random.random() < 0.004096

        # Aplicar modificador de clima
        weather_data = WEATHER_SYSTEM.get(weather, {})
        if any(t in weather_data.get("type_bonus", []) for t in pokemon_data["types"]):
            pokemon_data["rarity"] = min(pokemon_data["rarity"], "raro")  # Boost de raridade

        level = random.randint(area["min_level"], area["max_level"])
        pokemon_data["level"] = level
        pokemon_data["max_hp"] = pokemon_data["hp"] + (level * 2)
        pokemon_data["hp"] = pokemon_data["max_hp"]
        pokemon_data["attack"] = pokemon_data["attack"] + level
        pokemon_data["defense"] = pokemon_data["defense"] + level
        pokemon_data["speed"] = pokemon_data["speed"] + level
        pokemon_data["nature"] = generate_nature()
        pokemon_data["personality"] = generate_personality()
        pokemon_data["potential"] = {}

        # Salvar spawn no banco
        spawn_id = await db.add_wild_spawn(guild_id, channel_id, pokemon_data)

        # Criar embed de spawn
        sprite_url = pokemon_data["shiny_sprite_url"] if pokemon_data["is_shiny"] else pokemon_data["sprite_url"]
        shiny_text = "✨ **SHINY** " if pokemon_data["is_shiny"] else ""

        embed = discord.Embed(
            title=f"🌩 Algo estranho aconteceu em {region['name']}...",
            description=f"""
{get_weather_emoji(weather)} O clima está **{WEATHER_SYSTEM[weather]['name']}**

Um **{pokemon_data['name']}** selvagem apareceu!

{get_rarity_emoji(pokemon_data['rarity'])} Raridade: {format_rarity_name(pokemon_data['rarity'])}
{get_type_emoji(pokemon_data['types'][0])} Tipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in pokemon_data['types']])}
📊 Nível: {pokemon_data['level']}

❤ HP: {pokemon_data['hp']}/{pokemon_data['max_hp']}
⚔ Ataque: {pokemon_data['attack']}
🛡 Defesa: {pokemon_data['defense']}
💨 Velocidade: {pokemon_data['speed']}

⏰ Ele pode fugir em **5 minutos**!
            """,
            color=get_rarity_color(pokemon_data["rarity"])
        )
        embed.set_image(url=sprite_url)
        embed.set_footer(text=f"Spawn ID: {spawn_id} | Use /explore ou /catch para interagir")

        view = WildSpawnView(spawn_id, pokemon_data)
        await channel.send(embed=embed, view=view)

@tasks.loop(hours=6)
async def raid_cycle():
    """Inicia raids mundiais periodicamente"""
    active_raids = await db.get_active_raids()
    if len(active_raids) >= 2:  # Máximo 2 raids ativas
        return

    boss_id = random.choice(list(RAID_BOSSES.keys()))
    boss = RAID_BOSSES[boss_id]

    raid_id = await db.create_raid(boss_id, boss["location"], boss["area"], boss["duration_minutes"])

    # Notificar em todos os servidores
    for guild in bot.guilds:
        spawn_channel = world_state["spawn_channels"].get(guild.id)
        if spawn_channel:
            channel = bot.get_channel(spawn_channel)
            if channel:
                embed = discord.Embed(
                    title=f"🌋 ALERTA MUNDIAL",
                    description=f"""
✦ ─────────────── ✦
Um **{boss['name']}** gigante apareceu em **{get_region_name(boss['location'])}**!
✦ ─────────────── ✦

{boss['emoji']} **{boss['name']}**
Tipo: {get_type_emoji(boss['type'])} {boss['type'].capitalize()}
❤ HP: {format_number(boss['hp'])}
⚔ Ataque: {boss['attack']}
🛡 Defesa: {boss['defense']}

{boss['description']}

⏰ Tempo restante: **{boss['duration_minutes']} minutos**

Use `/raid` para entrar na batalha!
                    """,
                    color=COLORS["error"]
                )
                await channel.send(embed=embed)

@tasks.loop(minutes=5)
async def cleanup_spawns():
    """Remove spawns expirados"""
    pass  # Implementado via verificação no banco

# ═══════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════

async def update_quest_progress(user_id, progress_type, amount=1):
    """Atualiza progresso de missões ativas"""
    quests = await db.get_quests(user_id, completed=False)
    for quest in quests:
        progress = quest.get("progress", {})
        if progress_type in quest["requirements"]:
            current = progress.get(progress_type, 0)
            new_progress = current + amount
            progress[progress_type] = new_progress

            if new_progress >= quest["requirements"][progress_type]:
                await db.update_quest(quest["id"], progress=json.dumps(progress), completed=1)
            else:
                await db.update_quest(quest["id"], progress=json.dumps(progress))

async def check_region_unlock(user_id, region_id):
    """Verifica se o treinador desbloqueou uma região"""
    trainer = await db.get_trainer(user_id)
    if not trainer:
        return False
    unlocked = trainer.get("unlocked_regions", [])
    return region_id in unlocked

async def unlock_region(user_id, region_id):
    """Desbloqueia uma nova região para o treinador"""
    trainer = await db.get_trainer(user_id)
    if not trainer:
        return
    unlocked = trainer.get("unlocked_regions", [])
    if region_id not in unlocked:
        unlocked.append(region_id)
        await db.update_trainer(user_id, unlocked_regions=unlocked)

        region = ELYNDRA_WORLD["regions"][region_id]
        embed = discord.Embed(
            title=f"🗺️ Nova Região Desbloqueada!",
            description=f"**{region['emoji']} {region['name']}** foi desbloqueada!\n\n{region['description']}",
            color=COLORS.get(region_id, COLORS["premium"])
        )
        return embed
    return None

async def add_diary_entry(user_id, entry_type, title, description):
    """Adiciona entrada ao diário de jornada"""
    await db.add_diary_entry(user_id, entry_type, {"title": title, "description": description})

# ═══════════════════════════════════════════════════════════════
# VIEWS
# ═══════════════════════════════════════════════════════════════

class WildSpawnView(ui.View):
    def __init__(self, spawn_id, pokemon_data):
        super().__init__(timeout=300)  # 5 minutos
        self.spawn_id = spawn_id
        self.pokemon_data = pokemon_data

    @ui.button(label="🔍 Investigar", style=discord.ButtonStyle.primary)
    async def investigate(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="🔍 Investigação",
            description=f"Você observa o **{self.pokemon_data['name']}** de perto...\n\n"
                       f"Ele parece {random.choice(['agitado', 'calmo', 'alerta', 'curioso', 'assustado'])}.",
            color=COLORS["info"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="🤫 Se Aproximar", style=discord.ButtonStyle.secondary)
    async def approach(self, interaction: discord.Interaction, button: ui.Button):
        success = random.random() < 0.6
        if success:
            embed = discord.Embed(
                title="🤫 Sucesso!",
                description=f"Você se aproximou silenciosamente do **{self.pokemon_data['name']}**!\n"
                           f"A chance de captura aumentou!",
                color=COLORS["premium"]
            )
            self.pokemon_data["catch_bonus"] = 1.3
        else:
            embed = discord.Embed(
                title="😱 Ele te viu!",
                description=f"O **{self.pokemon_data['name']}** te notou e está mais alerta!",
                color=COLORS["warning"]
            )
            self.pokemon_data["catch_bonus"] = 0.8
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="⚪ Lançar Pokébola", style=discord.ButtonStyle.success)
    async def throw_ball(self, interaction: discord.Interaction, button: ui.Button):
        user_id = interaction.user.id
        trainer = await db.get_trainer(user_id)
        if not trainer:
            await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
            return

        inventory = await db.get_inventory(user_id)
        balls = [item for item in inventory if item["item_type"] == "ball"]

        if not balls:
            await interaction.response.send_message("✖ Você não tem Poké Balls!", ephemeral=True)
            return

        # Verificar se spawn ainda está ativo
        active_spawns = await db.get_active_spawns()
        if not any(s["id"] == self.spawn_id for s in active_spawns):
            await interaction.response.send_message("✖ Esse Pokémon já fugiu ou foi capturado!", ephemeral=True)
            return

        # Usar Poké Ball (simplificado - usa a primeira disponível)
        ball = balls[0]
        await db.remove_item(user_id, "ball", ball["item_id"], 1)

        # Calcular chance de captura
        base_rate = BASE_CATCH_RATE
        rarity_mod = {"comum": 1.0, "raro": 0.7, "epico": 0.4, "lendario": 0.1, "mitico": 0.05}
        catch_bonus = self.pokemon_data.get("catch_bonus", 1.0)
        ball_multiplier = {"pokeball": 1.0, "greatball": 1.5, "ultraball": 2.0, "masterball": 255.0}
        multiplier = ball_multiplier.get(ball["item_id"], 1.0)

        catch_chance = base_rate * multiplier * rarity_mod.get(self.pokemon_data["rarity"], 1.0) * catch_bonus

        if ball["item_id"] == "masterball" and self.pokemon_data["rarity"] != "mitico":
            catch_chance = 1.0

        caught = random.random() < catch_chance

        if caught:
            await db.catch_spawn(self.spawn_id, user_id)

            self.pokemon_data["xp"] = 0
            pokemon_id = await db.add_pokemon(user_id, self.pokemon_data)

            # XP do treinador
            new_xp = trainer["xp"] + XP_PER_CATCH
            new_level = calculate_level_from_xp(new_xp)
            new_catches = trainer["total_catches"] + 1

            updates = {"xp": new_xp, "total_catches": new_catches}
            if new_level > trainer["level"]:
                updates["level"] = new_level
                updates["rank"] = get_rank(new_level)["name"]

            await db.update_trainer(user_id, **updates)
            await update_quest_progress(user_id, "catches", 1)
            await add_diary_entry(user_id, "catch", f"Capturou {self.pokemon_data['name']}", 
                                 f"Capturou um {self.pokemon_data['name']} nível {self.pokemon_data['level']} em {get_region_name(self.pokemon_data.get('caught_region', 'verdalia'))}")

            shiny_text = "✨ **SHINY** " if self.pokemon_data["is_shiny"] else ""
            embed = discord.Embed(
                title="🎉 Capturado!",
                description=f"""
✦ ─────────────── ✦
{shiny_text}**{self.pokemon_data['name']}** foi capturado!
✦ ─────────────── ✦

{get_rarity_emoji(self.pokemon_data['rarity'])} {format_rarity_name(self.pokemon_data['rarity'])}
Tipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in self.pokemon_data['types']])}
📊 Nível: {self.pokemon_data['level']}

✨ +{XP_PER_CATCH} XP de treinador
🎯 Total de capturas: {new_catches}
                """,
                color=COLORS["premium"]
            )
            if new_level > trainer["level"]:
                embed.add_field(name="🎉 Level Up!", value=f"Você subiu para o nível **{new_level}**!", inline=False)

            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(
                title="✖ Escapou!",
                description=f"**{self.pokemon_data['name']}** escapou da Poké Ball!",
                color=COLORS["error"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="⚔ Iniciar Batalha", style=discord.ButtonStyle.danger)
    async def start_battle(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("⚔ Sistema de batalha contra spawns em desenvolvimento! Use `/battle` para batalhas PvE.", ephemeral=True)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — INÍCIO E PERFIL
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="start", description="Inicia sua jornada como treinador Pokémon em Elyndra")
async def start_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if trainer:
        embed = discord.Embed(
            title="✦ Jornada Iniciada",
            description="Você já é um treinador! Use `/profile` para ver seu progresso.",
            color=COLORS["warning"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await db.create_trainer(user_id, interaction.user.name, interaction.user.display_name)

    starter_pokemon = await pokeapi.get_pokemon_data(random.choice([1, 4, 7]))
    if starter_pokemon:
        starter_pokemon["level"] = 5
        starter_pokemon["xp"] = 0
        starter_pokemon["max_hp"] = starter_pokemon["hp"] + 10
        starter_pokemon["hp"] = starter_pokemon["max_hp"]
        starter_pokemon["attack"] = starter_pokemon["attack"] + 5
        starter_pokemon["defense"] = starter_pokemon["defense"] + 5
        starter_pokemon["speed"] = starter_pokemon["speed"] + 5
        starter_pokemon["rarity"] = "comum"
        starter_pokemon["nature"] = generate_nature()
        starter_pokemon["personality"] = generate_personality()
        starter_pokemon["potential"] = {}
        starter_pokemon["is_shiny"] = False
        starter_pokemon["friendship"] = 20
        starter_pokemon["caught_region"] = "verdalia"
        starter_pokemon["caught_area"] = "bosque_esmeralda"

        pokemon_id = await db.add_pokemon(user_id, starter_pokemon)
        await db.update_pokemon(pokemon_id, is_in_team=1, team_position=0)

    await db.add_item(user_id, "ball", "pokeball", 10)
    await db.add_item(user_id, "item", "potion", 5)

    # Adicionar missão inicial
    chapter = STORY_CHAPTERS["capitulo_1"]
    await db.add_quest(user_id, {
        "name": chapter["name"],
        "type": "story",
        "description": chapter["description"],
        "requirements": chapter["requirements"],
        "reward": chapter["rewards"],
        "progress": {}
    })

    # Diário
    await add_diary_entry(user_id, "start", "Início da Jornada", 
                         f"{interaction.user.display_name} iniciou sua jornada em Elyndra com um {starter_pokemon['name']}!")

    embed = discord.Embed(
        title="✦ Bem-vindo ao Mundo de Elyndra",
        description=f"""
Olá, **{interaction.user.display_name}**!

Sua jornada como treinador começou no continente **Elyndra**! Você recebeu:

☆ Pokémon inicial: **{starter_pokemon['name']}** (Nível 5)
⚪ 10 Poké Balls
🧪 5 Poções
💰 {STARTING_COINS} moedas

✦ Comandos essenciais:
→ `/profile` — Ver seu perfil
→ `/world` — Explorar o mundo
→ `/explore` — Explorar área atual
→ `/pokedex` — Ver seus Pokémon
→ `/team` — Gerenciar time
→ `/battle` — Batalhar
→ `/shop` — Loja
→ `/help` — Ajuda completa

Boa sorte em sua jornada! ⚔
        """,
        color=COLORS["premium"]
    )
    embed.set_thumbnail(url=starter_pokemon["sprite_url"])
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="profile", description="Mostra seu perfil de treinador em Elyndra")
async def profile_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        embed = discord.Embed(
            title="✖ Não encontrado",
            description="Você ainda não iniciou sua jornada! Use `/start` primeiro.",
            color=COLORS["error"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    team = await db.get_pokemons(user_id, in_team_only=True)
    rank = get_rank(trainer["level"])
    xp_bar = create_xp_bar(trainer["xp"], trainer["level"])

    # Badges
    badges = trainer.get("badges", [])
    badges_text = " ".join([f"🏅" for _ in badges]) if badges else "Nenhuma"

    # Regiões desbloqueadas
    unlocked = trainer.get("unlocked_regions", ["verdalia"])
    regions_text = " ".join([get_region_emoji(r) for r in unlocked])

    # Capítulo atual
    current_chapter = trainer.get("current_chapter", "capitulo_1")
    chapter_name = STORY_CHAPTERS.get(current_chapter, {}).get("name", "Desconhecido")

    # Título ativo
    active_title = trainer.get("active_title", "")
    title_text = f"『{active_title}』" if active_title else ""

    embed = discord.Embed(
        title=f"✦ {interaction.user.display_name} {title_text}",
        color=COLORS["premium"]
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    embed.add_field(
        name="📊 Informações",
        value=f"""
{rank['emoji']} **Rank:** {rank['name']}
⭐ **Nível:** {trainer['level']}
{xp_bar}
💰 **Moedas:** {format_number(trainer['coins'])}
🗺️ **Regiões:** {regions_text}
📖 **Capítulo:** {chapter_name}
        """,
        inline=False
    )

    embed.add_field(
        name="🏆 Estatísticas",
        value=f"""
🎯 Capturas: {trainer['total_catches']}
⚔ Batalhas: {trainer['total_battles']}
🏆 Vitórias: {trainer['total_wins']}
🔥 Streak: {trainer['streak']}
🏅 Insígnias: {badges_text}
        """,
        inline=True
    )

    if team:
        team_text = "\n".join([
            f"{i+1}. {get_type_emoji(p['types'][0])} **{p['name']}** (Nv. {p['level']}) {'✨' if p['is_shiny'] else ''}"
            for i, p in enumerate(team[:6])
        ])
        embed.add_field(name="⚔ Time Atual", value=team_text, inline=False)

    embed.add_field(
        name="🗺️ Localização",
        value=f"{get_region_emoji(trainer.get('current_region', 'verdalia'))} **{get_region_name(trainer.get('current_region', 'verdalia'))}** — {get_area_name(trainer.get('current_region', 'verdalia'), trainer.get('current_area', 'bosque_esmeralda'))}",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — MUNDO E EXPLORAÇÃO
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="world", description="Visualiza o mapa do mundo de Elyndra")
async def world_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🗺️ Mapa de Elyndra",
        description="""
✦ ─────────────── ✦
Bem-vindo ao continente de **Elyndra**
✦ ─────────────── ✦

Um mundo vasto e misterioso cheio de aventuras!
        """,
        color=COLORS["premium"]
    )
    embed.set_image(url=ELYNDRA_WORLD["map_url"])

    unlocked = trainer.get("unlocked_regions", ["verdalia"])

    for region_id, region in ELYNDRA_WORLD["regions"].items():
        is_unlocked = region_id in unlocked
        lock_emoji = "🔓" if is_unlocked else "🔒"
        areas_text = "\n".join([f"  {area['emoji']} {area['name']}" for area_id, area in region["areas"].items()])

        embed.add_field(
            name=f"{lock_emoji} {region['emoji']} {region['name']} {'(Desbloqueado)' if is_unlocked else '(Bloqueado)'}",
            value=f"{region['description']}\n{areas_text if is_unlocked else '🔒 Complete o capítulo anterior para desbloquear'}",
            inline=False
        )

    view = WorldMapView(user_id, trainer)
    await interaction.response.send_message(embed=embed, view=view)


class WorldMapView(ui.View):
    def __init__(self, user_id, trainer):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.trainer = trainer

        unlocked = trainer.get("unlocked_regions", ["verdalia"])
        options = []
        for region_id, region in ELYNDRA_WORLD["regions"].items():
            if region_id in unlocked:
                options.append(discord.SelectOption(
                    label=region["name"],
                    value=region_id,
                    description=region["description"][:100],
                    emoji=region["emoji"]
                ))

        if options:
            select = ui.Select(placeholder="🗺️ Viajar para região...", options=options[:25])
            select.callback = self.travel_callback
            self.add_item(select)

    async def travel_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é seu mapa!", ephemeral=True)
            return

        select = interaction.data["components"][0]["components"][0]
        region_id = select["values"][0]
        region = ELYNDRA_WORLD["regions"][region_id]

        # Escolher primeira área da região
        area_id = list(region["areas"].keys())[0]

        await db.update_trainer(self.user_id, current_region=region_id, current_area=area_id)

        embed = discord.Embed(
            title=f"🗺️ Viajando para {region['name']}",
            description=f"Você viajou para **{region['emoji']} {region['name']}** — {region['areas'][area_id]['name']}!",
            color=COLORS.get(region_id, COLORS["premium"])
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="explore", description="Explora a área atual em Elyndra")
async def explore_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    can_explore, remaining = await db.check_cooldown(user_id, "explore", 30)
    if not can_explore:
        embed = discord.Embed(
            title="⏳ Aguarde",
            description=f"Você precisa esperar **{format_time(remaining)}** para explorar novamente.",
            color=COLORS["warning"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    region_id = trainer.get("current_region", "verdalia")
    area_id = trainer.get("current_area", "bosque_esmeralda")
    region = ELYNDRA_WORLD["regions"][region_id]
    area = region["areas"][area_id]

    # Verificar nível mínimo
    if trainer["level"] < area["min_level"]:
        embed = discord.Embed(
            title="⚠️ Nível Insuficiente",
            description=f"Esta área requer nível **{area['min_level']}**. Você está no nível **{trainer['level']}**.",
            color=COLORS["warning"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title=f"{area['emoji']} {area['name']}",
        description=f"""
{region['emoji']} **{region['name']}**

{area['description']}

Nível recomendado: {area['min_level']} - {area['max_level']}

O que deseja fazer?
        """,
        color=COLORS.get(region_id, COLORS["premium"])
    )

    view = ExploreView(user_id, region_id, area_id, area)
    await interaction.response.send_message(embed=embed, view=view)

    # XP por explorar
    new_xp = trainer["xp"] + XP_PER_EXPLORE
    new_level = calculate_level_from_xp(new_xp)
    updates = {"xp": new_xp}
    if new_level > trainer["level"]:
        updates["level"] = new_level
        updates["rank"] = get_rank(new_level)["name"]
    await db.update_trainer(user_id, **updates)
    await update_quest_progress(user_id, "explores", 1)


class ExploreView(ui.View):
    def __init__(self, user_id, region_id, area_id, area):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.region_id = region_id
        self.area_id = area_id
        self.area = area

    @ui.button(label="🔍 Explorar", style=discord.ButtonStyle.primary)
    async def explore_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua exploração!", ephemeral=True)
            return

        # Determinar evento
        events = self.area.get("events", ["pokemon_wild"])
        weights = self.area.get("event_weights", [1.0])
        event = random.choices(events, weights=weights)[0]

        if event == "pokemon_wild":
            await self.spawn_pokemon(interaction)
        elif event == "item_found":
            await self.find_item(interaction)
        elif event == "trainer_encounter":
            await self.encounter_trainer(interaction)
        elif event == "chest":
            await self.find_chest(interaction)
        elif event == "secret_path":
            await self.find_secret(interaction)
        else:
            await self.generic_explore(interaction)

    @ui.button(label="👣 Seguir Pegadas", style=discord.ButtonStyle.secondary)
    async def tracks_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua exploração!", ephemeral=True)
            return

        pokemon_ids = self.area.get("pokemon_ids", [])
        if pokemon_ids and random.random() < 0.6:
            pokemon_id = random.choice(pokemon_ids)
            pokemon_data = await pokeapi.get_pokemon_data(pokemon_id)
            if pokemon_data:
                pokemon_data["rarity"] = random.choices(
                    list(self.area.get("rarity_weights", RARITY_CHANCES).keys()),
                    weights=list(self.area.get("rarity_weights", RARITY_CHANCES).values())
                )[0]
                pokemon_data["is_shiny"] = random.random() < 0.004096
                level = random.randint(self.area["min_level"], self.area["max_level"])
                pokemon_data["level"] = level
                pokemon_data["max_hp"] = pokemon_data["hp"] + (level * 2)
                pokemon_data["hp"] = pokemon_data["max_hp"]
                pokemon_data["attack"] = pokemon_data["attack"] + level
                pokemon_data["defense"] = pokemon_data["defense"] + level
                pokemon_data["speed"] = pokemon_data["speed"] + level
                pokemon_data["nature"] = generate_nature()
                pokemon_data["personality"] = generate_personality()
                pokemon_data["potential"] = {}
                pokemon_data["caught_region"] = self.region_id
                pokemon_data["caught_area"] = self.area_id

                sprite_url = pokemon_data["shiny_sprite_url"] if pokemon_data["is_shiny"] else pokemon_data["sprite_url"]
                shiny_text = "✨ **SHINY** " if pokemon_data["is_shiny"] else ""

                embed = discord.Embed(
                    title="👣 Você encontrou pegadas!",
                    description=f"""
As pegadas levam a um Pokémon selvagem!

{shiny_text}**{pokemon_data['name']}** apareceu!

{get_rarity_emoji(pokemon_data['rarity'])} Raridade: {format_rarity_name(pokemon_data['rarity'])}
Tipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in pokemon_data['types']])}
📊 Nível: {pokemon_data['level']}
                    """,
                    color=get_rarity_color(pokemon_data["rarity"])
                )
                embed.set_image(url=sprite_url)

                view = CatchView(self.user_id, pokemon_data, [])
                await interaction.response.send_message(embed=embed, view=view)
                return

        embed = discord.Embed(
            title="👣 Pegadas perdidas",
            description="As pegadas se perdem na vegetação... Nada por aqui.",
            color=COLORS["info"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="🍃 Coletar Recursos", style=discord.ButtonStyle.secondary)
    async def gather_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua exploração!", ephemeral=True)
            return

        items = self.area.get("items", ["potion", "pokeball"])
        found_item = random.choice(items)
        item_name = SHOP_ITEMS.get(found_item, {}).get("name", found_item)
        item_emoji = SHOP_ITEMS.get(found_item, {}).get("emoji", "📦")

        await db.add_item(self.user_id, "item" if found_item not in ["pokeball", "greatball", "ultraball", "masterball"] else "ball", found_item, 1)

        embed = discord.Embed(
            title="🍃 Recursos Coletados!",
            description=f"Você encontrou: **{item_emoji} {item_name}**!",
            color=COLORS["info"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="🏕️ Montar Acampamento", style=discord.ButtonStyle.secondary)
    async def camp_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua exploração!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🏕️ Acampamento",
            description="""
Você montou um acampamento!

O que deseja fazer?
            """,
            color=COLORS["premium"]
        )
        view = CampView(self.user_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def spawn_pokemon(self, interaction):
        pokemon_ids = self.area.get("pokemon_ids", [])
        if not pokemon_ids:
            await self.generic_explore(interaction)
            return

        pokemon_id = random.choice(pokemon_ids)
        pokemon_data = await pokeapi.get_pokemon_data(pokemon_id)
        if not pokemon_data:
            await self.generic_explore(interaction)
            return

        pokemon_data["rarity"] = random.choices(
            list(self.area.get("rarity_weights", RARITY_CHANCES).keys()),
            weights=list(self.area.get("rarity_weights", RARITY_CHANCES).values())
        )[0]
        pokemon_data["is_shiny"] = random.random() < 0.004096
        level = random.randint(self.area["min_level"], self.area["max_level"])
        pokemon_data["level"] = level
        pokemon_data["max_hp"] = pokemon_data["hp"] + (level * 2)
        pokemon_data["hp"] = pokemon_data["max_hp"]
        pokemon_data["attack"] = pokemon_data["attack"] + level
        pokemon_data["defense"] = pokemon_data["defense"] + level
        pokemon_data["speed"] = pokemon_data["speed"] + level
        pokemon_data["nature"] = generate_nature()
        pokemon_data["personality"] = generate_personality()
        pokemon_data["potential"] = {}
        pokemon_data["caught_region"] = self.region_id
        pokemon_data["caught_area"] = self.area_id

        sprite_url = pokemon_data["shiny_sprite_url"] if pokemon_data["is_shiny"] else pokemon_data["sprite_url"]
        shiny_text = "✨ **SHINY** " if pokemon_data["is_shiny"] else ""

        embed = discord.Embed(
            title=f"✦ Um Pokémon selvagem apareceu em {self.area['name']}!",
            description=f"""
{shiny_text}**{pokemon_data['name']}** apareceu!

{get_rarity_emoji(pokemon_data['rarity'])} Raridade: {format_rarity_name(pokemon_data['rarity'])}
Tipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in pokemon_data['types']])}
📊 Nível: {pokemon_data['level']}

❤ HP: {pokemon_data['hp']}/{pokemon_data['max_hp']}
⚔ Ataque: {pokemon_data['attack']}
🛡 Defesa: {pokemon_data['defense']}
💨 Velocidade: {pokemon_data['speed']}
            """,
            color=get_rarity_color(pokemon_data["rarity"])
        )
        embed.set_image(url=sprite_url)

        inventory = await db.get_inventory(self.user_id)
        balls = [item for item in inventory if item["item_type"] == "ball"]

        view = CatchView(self.user_id, pokemon_data, balls)
        await interaction.response.send_message(embed=embed, view=view)

    async def find_item(self, interaction):
        items = self.area.get("items", ["potion"])
        found_item = random.choice(items)
        item_name = SHOP_ITEMS.get(found_item, {}).get("name", found_item)
        item_emoji = SHOP_ITEMS.get(found_item, {}).get("emoji", "📦")

        await db.add_item(self.user_id, "item" if found_item not in ["pokeball", "greatball", "ultraball", "masterball"] else "ball", found_item, 1)

        embed = discord.Embed(
            title="📦 Item Encontrado!",
            description=f"Você encontrou **{item_emoji} {item_name}** enquanto explorava {self.area['name']}!",
            color=COLORS["info"]
        )
        await interaction.response.send_message(embed=embed)

    async def encounter_trainer(self, interaction):
        npcs = self.area.get("npcs", [])
        if npcs:
            npc_id = random.choice(npcs)
            npc = IMPORTANT_TRAINERS.get(npc_id)
            if npc:
                embed = discord.Embed(
                    title=f"👤 {npc['name']} — {npc['title']}",
                    description=f"""
✦ ─────────────── ✦
{npc['dialogue']['greeting']}
✦ ─────────────── ✦

Especialização: {get_type_emoji(npc['specialization'])} {npc['specialization'].capitalize()}
Dificuldade: {npc['difficulty']}

Use `/battle_trainer` para desafiá-lo!
                    """,
                    color=COLORS["premium"]
                )
                await interaction.response.send_message(embed=embed)
                return

        await self.generic_explore(interaction)

    async def find_chest(self, interaction):
        coins = random.randint(50, 300)
        trainer = await db.get_trainer(self.user_id)
        await db.update_trainer(self.user_id, coins=trainer["coins"] + coins)

        embed = discord.Embed(
            title="📦 Baú Encontrado!",
            description=f"Você encontrou um baú escondido!\n\n💰 **+{coins}** moedas!",
            color=COLORS["premium"]
        )
        await interaction.response.send_message(embed=embed)

    async def find_secret(self, interaction):
        embed = discord.Embed(
            title="🗝️ Caminho Secreto!",
            description="Você descobriu um caminho secreto! A exploração continua...",
            color=COLORS["premium"]
        )
        await interaction.response.send_message(embed=embed)

    async def generic_explore(self, interaction):
        texts = [
            "Você explora a área com cuidado...",
            "O vento sussurra segredos antigos...",
            "Você sente a presença de Pokémon por perto...",
            "A natureza está em harmonia aqui...",
        ]
        embed = discord.Embed(
            title="🔍 Explorando...",
            description=random.choice(texts),
            color=COLORS["info"]
        )
        await interaction.response.send_message(embed=embed)


class CampView(ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.user_id = user_id

    @ui.button(label="😴 Descansar", style=discord.ButtonStyle.primary)
    async def rest(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é seu acampamento!", ephemeral=True)
            return

        team = await db.get_pokemons(self.user_id, in_team_only=True)
        for pokemon in team:
            await db.update_pokemon(pokemon["id"], hp=pokemon["max_hp"])

        embed = discord.Embed(
            title="😴 Descansando...",
            description="Seus Pokémon descansaram e recuperaram todo o HP!",
            color=COLORS["info"]
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @ui.button(label="🍎 Alimentar Pokémon", style=discord.ButtonStyle.secondary)
    async def feed(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é seu acampamento!", ephemeral=True)
            return

        team = await db.get_pokemons(self.user_id, in_team_only=True)
        if not team:
            await interaction.response.send_message("✖ Você não tem Pokémon no time!", ephemeral=True)
            return

        # Aumentar amizade
        for pokemon in team:
            new_friendship = min(500, pokemon.get("friendship", 0) + 5)
            await db.update_pokemon(pokemon["id"], friendship=new_friendship)

        embed = discord.Embed(
            title="🍎 Alimentando...",
            description="Você alimentou seus Pokémon! A amizade aumentou! 💝",
            color=COLORS["info"]
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @ui.button(label="🎾 Brincar", style=discord.ButtonStyle.secondary)
    async def play(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é seu acampamento!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎾 Brincando...",
            description="Você brincou com seus Pokémon! Eles parecem mais felizes!",
            color=COLORS["info"]
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @ui.button(label="💪 Treinar", style=discord.ButtonStyle.secondary)
    async def train(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é seu acampamento!", ephemeral=True)
            return

        team = await db.get_pokemons(self.user_id, in_team_only=True)
        for pokemon in team:
            new_xp = pokemon.get("xp", 0) + 20
            await db.update_pokemon(pokemon["id"], xp=new_xp)

        embed = discord.Embed(
            title="💪 Treinando...",
            description="Seus Pokémon treinaram e ganharam +20 XP cada!",
            color=COLORS["info"]
        )
        await interaction.response.edit_message(embed=embed, view=None)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — POKÉDEX E TIME
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="pokedex", description="Ver seus Pokémon capturados em Elyndra")
@app_commands.describe(page="Página da Pokédex")
async def pokedex_command(interaction: discord.Interaction, page: int = 1):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    pokemons = await db.get_pokemons(user_id)
    if not pokemons:
        embed = discord.Embed(
            title="📖 Pokédex",
            description="Você ainda não capturou nenhum Pokémon!\nUse `/explore` para começar.",
            color=COLORS["warning"]
        )
        await interaction.response.send_message(embed=embed)
        return

    per_page = 5
    total_pages = max(1, (len(pokemons) + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    page_pokemons = pokemons[start:end]

    embed = discord.Embed(
        title=f"📖 Pokédex — Página {page}/{total_pages}",
        description=f"Total capturado: **{len(pokemons)}** Pokémon",
        color=COLORS["info"]
    )

    for pokemon in page_pokemons:
        shiny_text = " ✨ SHINY" if pokemon["is_shiny"] else ""
        team_text = " ⚔ TIME" if pokemon["is_in_team"] else ""
        personality_text = f"{get_personality_emoji(pokemon.get('personality', 'agressivo'))} {get_personality_name(pokemon.get('personality', 'agressivo'))}"
        friendship = create_friendship_bar(pokemon.get("friendship", 0))
        value = f"""
{get_rarity_emoji(pokemon['rarity'])} {format_rarity_name(pokemon['rarity'])}{shiny_text}{team_text}
{personality_text}
Tipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in pokemon['types']])}
❤ {pokemon['hp']}/{pokemon['max_hp']} | ⚔ {pokemon['attack']} | 🛡 {pokemon['defense']} | 💨 {pokemon['speed']}
📊 Nível {pokemon['level']} | ✨ {pokemon['xp']} XP
{friendship}
        """
        embed.add_field(
            name=f"#{pokemon['pokedex_number']} {pokemon['name']}{shiny_text}",
            value=value,
            inline=False
        )

    view = PokedexView(user_id, page, total_pages, pokemons)
    await interaction.response.send_message(embed=embed, view=view)


class PokedexView(ui.View):
    def __init__(self, user_id, current_page, total_pages, pokemons):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.current_page = current_page
        self.total_pages = total_pages
        self.pokemons = pokemons

    @ui.button(label="◀ Anterior", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua Pokédex!", ephemeral=True)
            return
        if self.current_page > 1:
            self.current_page -= 1
            await self.update_pokedex(interaction)

    @ui.button(label="Próximo ▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua Pokédex!", ephemeral=True)
            return
        if self.current_page < self.total_pages:
            self.current_page += 1
            await self.update_pokedex(interaction)

    async def update_pokedex(self, interaction):
        per_page = 5
        start = (self.current_page - 1) * per_page
        end = start + per_page
        page_pokemons = self.pokemons[start:end]

        embed = discord.Embed(
            title=f"📖 Pokédex — Página {self.current_page}/{self.total_pages}",
            description=f"Total capturado: **{len(self.pokemons)}** Pokémon",
            color=COLORS["info"]
        )

        for pokemon in page_pokemons:
            shiny_text = " ✨ SHINY" if pokemon["is_shiny"] else ""
            team_text = " ⚔ TIME" if pokemon["is_in_team"] else ""
            personality_text = f"{get_personality_emoji(pokemon.get('personality', 'agressivo'))} {get_personality_name(pokemon.get('personality', 'agressivo'))}"
            friendship = create_friendship_bar(pokemon.get("friendship", 0))
            value = f"""
{get_rarity_emoji(pokemon['rarity'])} {format_rarity_name(pokemon['rarity'])}{shiny_text}{team_text}
{personality_text}
Tipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in pokemon['types']])}
❤ {pokemon['hp']}/{pokemon['max_hp']} | ⚔ {pokemon['attack']} | 🛡 {pokemon['defense']} | 💨 {pokemon['speed']}
📊 Nível {pokemon['level']} | ✨ {pokemon['xp']} XP
{friendship}
            """
            embed.add_field(
                name=f"#{pokemon['pokedex_number']} {pokemon['name']}{shiny_text}",
                value=value,
                inline=False
            )

        await interaction.response.edit_message(embed=embed, view=self)


@bot.tree.command(name="team", description="Gerencia seu time de Pokémon")
async def team_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    team = await db.get_pokemons(user_id, in_team_only=True)
    all_pokemon = await db.get_pokemons(user_id)

    embed = discord.Embed(
        title="⚔ Gerenciar Time",
        description=f"Time atual: **{len(team)}/{MAX_TEAM_SIZE}** Pokémon",
        color=COLORS["premium"]
    )

    if team:
        team_text = "\n".join([f"{i+1}. {get_type_emoji(p['types'][0])} **{p['name']}** (Nv. {p['level']}) {'✨' if p['is_shiny'] else ''}" for i, p in enumerate(team)])
        embed.add_field(name="Time Atual", value=team_text, inline=False)

    available = [p for p in all_pokemon if not p["is_in_team"]]
    if available:
        available_text = "\n".join([f"{get_type_emoji(p['types'][0])} **{p['name']}** (Nv. {p['level']}) {'✨' if p['is_shiny'] else ''}" for p in available[:10]])
        embed.add_field(name="Disponíveis", value=available_text, inline=False)

    view = TeamView(user_id, all_pokemon)
    await interaction.response.send_message(embed=embed, view=view)


class TeamView(ui.View):
    def __init__(self, user_id, all_pokemon):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.all_pokemon = all_pokemon

        available = [p for p in all_pokemon if not p["is_in_team"]]
        if available:
            options = []
            for p in available[:25]:
                options.append(discord.SelectOption(
                    label=f"{p['name']} (Nv.{p['level']})",
                    value=str(p['id']),
                    description=f"{p['types'][0].capitalize()} | HP:{p['hp']}/{p['max_hp']}",
                    emoji=get_type_emoji(p['types'][0])
                ))
            add_select = ui.Select(placeholder="➕ Adicionar ao time", options=options[:25], custom_id="add_team")
            add_select.callback = self.add_callback
            self.add_item(add_select)

        team = [p for p in all_pokemon if p["is_in_team"]]
        if team:
            options = []
            for p in team[:25]:
                options.append(discord.SelectOption(
                    label=f"{p['name']} (Nv.{p['level']})",
                    value=str(p['id']),
                    description=f"Posição {p['team_position'] + 1}",
                    emoji=get_type_emoji(p['types'][0])
                ))
            remove_select = ui.Select(placeholder="➖ Remover do time", options=options[:25], custom_id="remove_team")
            remove_select.callback = self.remove_callback
            self.add_item(remove_select)

    async def add_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é seu time!", ephemeral=True)
            return
        select = interaction.data["components"][0]["components"][0]
        pokemon_id = int(select["values"][0])
        team = await db.get_pokemons(self.user_id, in_team_only=True)
        if len(team) >= MAX_TEAM_SIZE:
            await interaction.response.send_message(f"✖ Time cheio! Máximo {MAX_TEAM_SIZE} Pokémon.", ephemeral=True)
            return
        await db.update_pokemon(pokemon_id, is_in_team=1, team_position=len(team))
        pokemon = await db.get_pokemon_by_id(pokemon_id)
        embed = discord.Embed(title="✔ Adicionado!", description=f"**{pokemon['name']}** foi adicionado ao time!", color=COLORS["info"])
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def remove_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é seu time!", ephemeral=True)
            return
        select = interaction.data["components"][0]["components"][0]
        pokemon_id = int(select["values"][0])
        await db.update_pokemon(pokemon_id, is_in_team=0, team_position=-1)
        pokemon = await db.get_pokemon_by_id(pokemon_id)
        embed = discord.Embed(title="✔ Removido!", description=f"**{pokemon['name']}** foi removido do time.", color=COLORS["info"])
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — CAPTURA
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="catch", description="Tenta capturar um Pokémon selvagem na área atual")
async def catch_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    can_catch, remaining = await db.check_cooldown(user_id, "catch", 30)
    if not can_catch:
        embed = discord.Embed(
            title="⏳ Aguarde",
            description=f"Você precisa esperar **{format_time(remaining)}** para capturar outro Pokémon.",
            color=COLORS["warning"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Usar a área atual do treinador
    region_id = trainer.get("current_region", "verdalia")
    area_id = trainer.get("current_area", "bosque_esmeralda")
    region = ELYNDRA_WORLD["regions"][region_id]
    area = region["areas"][area_id]

    pokemon_ids = area.get("pokemon_ids", [])
    if not pokemon_ids:
        await interaction.response.send_message("⚠ Nenhum Pokémon encontrado nesta área!", ephemeral=True)
        return

    pokemon_id = random.choice(pokemon_ids)
    wild_pokemon = await pokeapi.get_pokemon_data(pokemon_id)
    if not wild_pokemon:
        await interaction.response.send_message("⚠ Erro ao gerar Pokémon. Tente novamente.", ephemeral=True)
        return

    level = random.randint(area["min_level"], min(area["max_level"], max(5, trainer["level"] + 5)))
    wild_pokemon["level"] = level
    wild_pokemon["xp"] = 0
    wild_pokemon["max_hp"] = wild_pokemon["hp"] + (level * 2)
    wild_pokemon["hp"] = wild_pokemon["max_hp"]
    wild_pokemon["attack"] = wild_pokemon["attack"] + level
    wild_pokemon["defense"] = wild_pokemon["defense"] + level
    wild_pokemon["speed"] = wild_pokemon["speed"] + level
    wild_pokemon["nature"] = generate_nature()
    wild_pokemon["personality"] = generate_personality()
    wild_pokemon["potential"] = {}
    wild_pokemon["rarity"] = random.choices(
        list(area.get("rarity_weights", RARITY_CHANCES).keys()),
        weights=list(area.get("rarity_weights", RARITY_CHANCES).values())
    )[0]
    wild_pokemon["is_shiny"] = random.random() < 0.004096
    wild_pokemon["caught_region"] = region_id
    wild_pokemon["caught_area"] = area_id

    inventory = await db.get_inventory(user_id)
    balls = [item for item in inventory if item["item_type"] == "ball"]

    if not balls:
        embed = discord.Embed(
            title="✖ Sem Poké Balls",
            description="Você não tem Poké Balls! Compre na loja com `/shop`.",
            color=COLORS["error"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    sprite_url = wild_pokemon["shiny_sprite_url"] if wild_pokemon["is_shiny"] else wild_pokemon["sprite_url"]
    shiny_text = "✨ **SHINY** " if wild_pokemon["is_shiny"] else ""

    embed = discord.Embed(
        title=f"✦ Um Pokémon selvagem apareceu em {area['name']}!",
        description=f"""
{shiny_text}**{wild_pokemon['name']}** apareceu!

{get_rarity_emoji(wild_pokemon['rarity'])} Raridade: {format_rarity_name(wild_pokemon['rarity'])}
Tipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in wild_pokemon['types']])}
📊 Nível: {wild_pokemon['level']}

❤ HP: {wild_pokemon['hp']}/{wild_pokemon['max_hp']}
⚔ Ataque: {wild_pokemon['attack']}
🛡 Defesa: {wild_pokemon['defense']}
💨 Velocidade: {wild_pokemon['speed']}
        """,
        color=get_rarity_color(wild_pokemon["rarity"])
    )
    embed.set_image(url=sprite_url)

    view = CatchView(user_id, wild_pokemon, balls)
    await interaction.response.send_message(embed=embed, view=view)


class CatchView(ui.View):
    def __init__(self, user_id, wild_pokemon, balls):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.wild_pokemon = wild_pokemon
        self.balls = balls
        self.caught = False

    @ui.button(label="⚪ Poké Ball", style=discord.ButtonStyle.primary)
    async def pokeball_button(self, interaction: discord.Interaction, button: ui.Button):
        await self.try_catch(interaction, "pokeball", 1.0)

    @ui.button(label="🔵 Great Ball", style=discord.ButtonStyle.primary)
    async def greatball_button(self, interaction: discord.Interaction, button: ui.Button):
        await self.try_catch(interaction, "greatball", 1.5)

    @ui.button(label="🟡 Ultra Ball", style=discord.ButtonStyle.primary)
    async def ultraball_button(self, interaction: discord.Interaction, button: ui.Button):
        await self.try_catch(interaction, "ultraball", 2.0)

    @ui.button(label="🔴 Master Ball", style=discord.ButtonStyle.danger)
    async def masterball_button(self, interaction: discord.Interaction, button: ui.Button):
        await self.try_catch(interaction, "masterball", 255.0)

    async def try_catch(self, interaction, ball_type, multiplier):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua captura!", ephemeral=True)
            return
        if self.caught:
            await interaction.response.send_message("✖ Pokémon já capturado!", ephemeral=True)
            return
        has_ball = any(b["item_id"] == ball_type and b["quantity"] > 0 for b in self.balls)
        if not has_ball:
            await interaction.response.send_message(f"✖ Você não tem {ball_type}!", ephemeral=True)
            return
        await db.remove_item(self.user_id, "ball", ball_type, 1)

        embed = discord.Embed(title="✦ Capturando...", description="A Poké Ball balança...\n\n[░░░░░░░░░]", color=COLORS["premium"])
        await interaction.response.edit_message(embed=embed, view=None)
        await asyncio.sleep(1)
        embed.description = "A Poké Ball balança...\n\n[▓▓░░░░░░░]"
        await interaction.edit_original_response(embed=embed)
        await asyncio.sleep(1)
        embed.description = "A Poké Ball balança...\n\n[▓▓▓▓▓░░░░]"
        await interaction.edit_original_response(embed=embed)
        await asyncio.sleep(1)

        base_rate = BASE_CATCH_RATE
        rarity_mod = {"comum": 1.0, "raro": 0.7, "epico": 0.4, "lendario": 0.1, "mitico": 0.05}
        catch_chance = base_rate * multiplier * rarity_mod.get(self.wild_pokemon["rarity"], 1.0)
        if ball_type == "masterball" and self.wild_pokemon["rarity"] != "mitico":
            catch_chance = 1.0

        caught = random.random() < catch_chance

        if caught:
            self.caught = True
            self.wild_pokemon["xp"] = 0
            pokemon_id = await db.add_pokemon(self.user_id, self.wild_pokemon)
            trainer = await db.get_trainer(self.user_id)
            new_xp = trainer["xp"] + XP_PER_CATCH
            new_level = calculate_level_from_xp(new_xp)
            new_catches = trainer["total_catches"] + 1
            updates = {"xp": new_xp, "total_catches": new_catches}
            if new_level > trainer["level"]:
                updates["level"] = new_level
                updates["rank"] = get_rank(new_level)["name"]
            await db.update_trainer(self.user_id, **updates)
            await update_quest_progress(self.user_id, "catches", 1)
            await add_diary_entry(self.user_id, "catch", f"Capturou {self.wild_pokemon['name']}", 
                                 f"Capturou um {self.wild_pokemon['name']} nível {self.wild_pokemon['level']} em {get_region_name(self.wild_pokemon.get('caught_region', 'verdalia'))}")

            shiny_text = "✨ **SHINY** " if self.wild_pokemon["is_shiny"] else ""
            embed = discord.Embed(
                title="🎉 Capturado!",
                description=f"""
✦ ─────────────── ✦
{shiny_text}**{self.wild_pokemon['name']}** foi capturado!
✦ ─────────────── ✦

{get_rarity_emoji(self.wild_pokemon['rarity'])} {format_rarity_name(self.wild_pokemon['rarity'])}
Tipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in self.wild_pokemon['types']])}
📊 Nível: {self.wild_pokemon['level']}

✨ +{XP_PER_CATCH} XP de treinador
🎯 Total de capturas: {new_catches}
                """,
                color=COLORS["premium"]
            )
            embed.set_image(url=self.wild_pokemon["sprite_url"] if not self.wild_pokemon["is_shiny"] else self.wild_pokemon["shiny_sprite_url"])
            if new_level > trainer["level"]:
                embed.add_field(name="🎉 Level Up!", value=f"Você subiu para o nível **{new_level}**!", inline=False)
        else:
            embed = discord.Embed(
                title="✖ Escapou!",
                description=f"**{self.wild_pokemon['name']}** escapou da Poké Ball!\n\nO Pokémon fugiu para a floresta...",
                color=COLORS["error"]
            )
        await interaction.edit_original_response(embed=embed, view=None)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — BATALHAS
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="battle", description="Inicia uma batalha PvE contra um treinador NPC em Elyndra")
async def battle_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    team = await db.get_pokemons(user_id, in_team_only=True)
    if not team:
        await interaction.response.send_message("✖ Você não tem Pokémon no time!", ephemeral=True)
        return

    can_battle, remaining = await db.check_cooldown(user_id, "battle", 60)
    if not can_battle:
        embed = discord.Embed(
            title="⏳ Aguarde",
            description=f"Você precisa esperar **{format_time(remaining)}** para batalhar novamente.",
            color=COLORS["warning"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Gerar NPC baseado na região atual
    region_id = trainer.get("current_region", "verdalia")
    region = ELYNDRA_WORLD["regions"][region_id]
    area_id = trainer.get("current_area", "bosque_esmeralda")
    area = region["areas"][area_id]

    npc_names = ["Gary", "Misty", "Brock", "Lance", "Cynthia", "Steven", "Diantha", "Leon"]
    npc_name = random.choice(npc_names)
    npc_level = max(1, trainer["level"] + random.randint(-3, 5))

    npc_team = []
    for _ in range(random.randint(1, min(3, len(team)))):
        npc_pokemon = await pokeapi.get_random_pokemon(max_id=151)
        if npc_pokemon:
            npc_pokemon["level"] = max(1, npc_level + random.randint(-2, 2))
            npc_pokemon["max_hp"] = npc_pokemon["hp"] + (npc_pokemon["level"] * 2)
            npc_pokemon["hp"] = npc_pokemon["max_hp"]
            npc_pokemon["attack"] = npc_pokemon["attack"] + npc_pokemon["level"]
            npc_pokemon["defense"] = npc_pokemon["defense"] + npc_pokemon["level"]
            npc_pokemon["speed"] = npc_pokemon["speed"] + npc_pokemon["level"]
            npc_pokemon["nature"] = generate_nature()
            npc_pokemon["personality"] = generate_personality()
            npc_pokemon["moves"] = [get_random_move_for_type(npc_pokemon["types"][0]) for _ in range(4)]
            npc_team.append(npc_pokemon)

    battle = BattleSystem(interaction, team, npc_team, trainer, npc_name)
    await battle.start()


@bot.tree.command(name="battle_trainer", description="Desafia um treinador importante de Elyndra")
@app_commands.describe(trainer_name="Nome do treinador para desafiar")
async def battle_trainer_command(interaction: discord.Interaction, trainer_name: str):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    team = await db.get_pokemons(user_id, in_team_only=True)
    if not team:
        await interaction.response.send_message("✖ Você não tem Pokémon no time!", ephemeral=True)
        return

    # Encontrar treinador
    npc = None
    npc_id = None
    for tid, tdata in IMPORTANT_TRAINERS.items():
        if tdata["name"].lower() == trainer_name.lower():
            npc = tdata
            npc_id = tid
            break

    if not npc:
        available = ", ".join([t["name"] for t in IMPORTANT_TRAINERS.values()])
        await interaction.response.send_message(f"✖ Treinador não encontrado! Disponíveis: {available}", ephemeral=True)
        return

    # Verificar nível
    if trainer["level"] < npc["min_level"]:
        await interaction.response.send_message(f"✖ Você precisa estar no nível **{npc['min_level']}** para desafiar **{npc['name']}**!", ephemeral=True)
        return

    # Verificar se já derrotou
    badges = trainer.get("badges", [])
    badge_id = npc.get("rewards", {}).get("badge")
    if badge_id and badge_id in badges:
        await interaction.response.send_message(f"✖ Você já derrotou **{npc['name']}**!", ephemeral=True)
        return

    can_battle, remaining = await db.check_cooldown(user_id, "battle_trainer", 300)
    if not can_battle:
        embed = discord.Embed(title="⏳ Aguarde", description=f"Você precisa esperar **{format_time(remaining)}**.", color=COLORS["warning"])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Gerar time do NPC
    npc_team = []
    for _ in range(npc["team_size"]):
        pokemon_id = random.choice(npc["pokemon_pool"])
        npc_pokemon = await pokeapi.get_pokemon_data(pokemon_id)
        if npc_pokemon:
            level = random.randint(npc["min_level"], npc["max_level"])
            npc_pokemon["level"] = level
            npc_pokemon["max_hp"] = npc_pokemon["hp"] + (level * 2)
            npc_pokemon["hp"] = npc_pokemon["max_hp"]
            npc_pokemon["attack"] = npc_pokemon["attack"] + level
            npc_pokemon["defense"] = npc_pokemon["defense"] + level
            npc_pokemon["speed"] = npc_pokemon["speed"] + level
            npc_pokemon["nature"] = generate_nature()
            npc_pokemon["personality"] = generate_personality()
            npc_pokemon["moves"] = [get_random_move_for_type(npc_pokemon["types"][0]) for _ in range(4)]
            npc_team.append(npc_pokemon)

    battle = TrainerBattleSystem(interaction, team, npc_team, trainer, npc, npc_id)
    await battle.start()


class BattleSystem:
    def __init__(self, interaction, player_team, npc_team, trainer, npc_name):
        self.interaction = interaction
        self.player_team = [p.copy() for p in player_team]
        self.npc_team = [p.copy() for p in npc_team]
        self.trainer = trainer
        self.npc_name = npc_name
        self.current_player_pokemon = 0
        self.current_npc_pokemon = 0
        self.turn = 0
        self.battle_log = []

    async def start(self):
        player_pokemon = self.player_team[self.current_player_pokemon]
        npc_pokemon = self.npc_team[self.current_npc_pokemon]
        embed = discord.Embed(
            title="⚔ Batalha Iniciada!",
            description=f"""
✦ ─────────────── ✦
**{self.interaction.user.display_name}** vs **{self.npc_name}**
✦ ─────────────── ✦

🟢 {player_pokemon['name']} (Nv. {player_pokemon['level']})
VS
🔴 {npc_pokemon['name']} (Nv. {npc_pokemon['level']})

Prepare-se para batalhar!
            """,
            color=COLORS["premium"]
        )
        view = BattleView(self)
        await self.interaction.response.send_message(embed=embed, view=view)

    async def execute_turn(self, interaction, move_index):
        player_pokemon = self.player_team[self.current_player_pokemon]
        npc_pokemon = self.npc_team[self.current_npc_pokemon]
        player_first = player_pokemon["speed"] >= npc_pokemon["speed"]
        log_entries = []

        if player_first:
            await self.execute_attack(player_pokemon, npc_pokemon, move_index, log_entries, True)
            if npc_pokemon["hp"] > 0:
                npc_move = random.randint(0, len(npc_pokemon["moves"]) - 1)
                await self.execute_attack(npc_pokemon, player_pokemon, npc_move, log_entries, False)
        else:
            npc_move = random.randint(0, len(npc_pokemon["moves"]) - 1)
            await self.execute_attack(npc_pokemon, player_pokemon, npc_move, log_entries, False)
            if player_pokemon["hp"] > 0:
                await self.execute_attack(player_pokemon, npc_pokemon, move_index, log_entries, True)

        self.battle_log.extend(log_entries)
        self.turn += 1

        battle_over = False
        winner = None
        if player_pokemon["hp"] <= 0:
            if self.current_player_pokemon < len(self.player_team) - 1:
                self.current_player_pokemon += 1
                log_entries.append(f"🔄 {self.interaction.user.display_name} enviou {self.player_team[self.current_player_pokemon]['name']}!")
            else:
                battle_over = True
                winner = "npc"
        if npc_pokemon["hp"] <= 0:
            if self.current_npc_pokemon < len(self.npc_team) - 1:
                self.current_npc_pokemon += 1
                log_entries.append(f"🔄 {self.npc_name} enviou {self.npc_team[self.current_npc_pokemon]['name']}!")
            else:
                battle_over = True
                winner = "player"

        if battle_over:
            await self.end_battle(interaction, winner)
        else:
            await self.update_battle_display(interaction)

    async def execute_attack(self, attacker, defender, move_index, log_entries, is_player):
        move = attacker["moves"][move_index] if move_index < len(attacker["moves"]) else "Tackle"
        if is_dodge():
            log_entries.append(f"💨 {defender['name']} esquivou de {move}!")
            return
        attacker_type = attacker["types"][0] if attacker["types"] else "normal"
        effectiveness = calculate_type_effectiveness(attacker_type, defender["types"])
        is_crit = is_critical_hit()
        damage = calculate_damage(attacker, defender, 50, is_crit)
        damage = int(damage * effectiveness)
        defender["hp"] = max(0, defender["hp"] - damage)
        attacker_name = f"🟢 {attacker['name']}" if is_player else f"🔴 {attacker['name']}"
        crit_text = " 💥 CRÍTICO!" if is_crit else ""
        effect_text = get_effectiveness_text(effectiveness)
        log_entries.append(f"{attacker_name} usou **{move}**!{crit_text} {effect_text}\n→ {defender['name']} perdeu {damage} HP!")

    async def update_battle_display(self, interaction):
        player_pokemon = self.player_team[self.current_player_pokemon]
        npc_pokemon = self.npc_team[self.current_npc_pokemon]
        recent_log = "\n".join(self.battle_log[-5:]) if self.battle_log else "A batalha começou!"
        embed = discord.Embed(
            title=f"⚔ Turno {self.turn + 1}",
            description=f"""
✦ ─────────────── ✦
**{self.interaction.user.display_name}** vs **{self.npc_name}**
✦ ─────────────── ✦

🟢 **{player_pokemon['name']}** (Nv. {player_pokemon['level']})
{create_hp_bar(player_pokemon['hp'], player_pokemon['max_hp'])}

🔴 **{npc_pokemon['name']}** (Nv. {npc_pokemon['level']})
{create_hp_bar(npc_pokemon['hp'], npc_pokemon['max_hp'])}

✦ ─────────────── ✦
📜 Log:
{recent_log}
            """,
            color=COLORS["premium"]
        )
        view = BattleView(self)
        await interaction.response.edit_message(embed=embed, view=view)

    async def end_battle(self, interaction, winner):
        if winner == "player":
            xp_reward = XP_PER_BATTLE_WIN + (self.trainer["level"] * 5)
            coin_reward = random.randint(100, 300) + (self.trainer["level"] * 10)
            new_xp = self.trainer["xp"] + xp_reward
            new_level = calculate_level_from_xp(new_xp)
            new_wins = self.trainer["total_wins"] + 1
            new_streak = self.trainer["streak"] + 1
            new_battles = self.trainer["total_battles"] + 1
            updates = {"xp": new_xp, "total_wins": new_wins, "streak": new_streak, "total_battles": new_battles, "coins": self.trainer["coins"] + coin_reward}
            if new_level > self.trainer["level"]:
                updates["level"] = new_level
                updates["rank"] = get_rank(new_level)["name"]
            await db.update_trainer(self.interaction.user.id, **updates)
            await update_quest_progress(self.interaction.user.id, "wins", 1)
            await add_diary_entry(self.interaction.user.id, "battle_win", f"Venceu {self.npc_name}", f"Derrotou {self.npc_name} em batalha!")
            embed = discord.Embed(
                title="🏆 Vitória!",
                description=f"""
✦ ─────────────── ✦
**{self.interaction.user.display_name}** venceu!
✦ ─────────────── ✦

🏆 Você derrotou **{self.npc_name}**!

🎁 Recompensas:
✨ +{xp_reward} XP
💰 +{coin_reward} moedas
🔥 Streak: {new_streak}

Vitórias totais: {new_wins}
                """,
                color=COLORS["premium"]
            )
            if new_level > self.trainer["level"]:
                embed.add_field(name="🎉 Level Up!", value=f"Você subiu para o nível **{new_level}**!", inline=False)
        else:
            new_battles = self.trainer["total_battles"] + 1
            await db.update_trainer(self.interaction.user.id, total_battles=new_battles, streak=0)
            embed = discord.Embed(
                title="✖ Derrota",
                description=f"**{self.npc_name}** venceu a batalha...\n\nNão desista! Treine seus Pokémon e tente novamente!",
                color=COLORS["error"]
            )
        await interaction.response.edit_message(embed=embed, view=None)


class TrainerBattleSystem(BattleSystem):
    def __init__(self, interaction, player_team, npc_team, trainer, npc_data, npc_id):
        super().__init__(interaction, player_team, npc_team, trainer, npc_data["name"])
        self.npc_data = npc_data
        self.npc_id = npc_id

    async def end_battle(self, interaction, winner):
        if winner == "player":
            rewards = self.npc_data.get("rewards", {})
            xp_reward = rewards.get("xp", XP_PER_BATTLE_WIN)
            coin_reward = rewards.get("coins", 500)
            badge = rewards.get("badge")
            title = rewards.get("title")
            items = rewards.get("items", [])

            new_xp = self.trainer["xp"] + xp_reward
            new_level = calculate_level_from_xp(new_xp)
            new_wins = self.trainer["total_wins"] + 1
            new_streak = self.trainer["streak"] + 1
            new_battles = self.trainer["total_battles"] + 1
            new_coins = self.trainer["coins"] + coin_reward

            updates = {"xp": new_xp, "total_wins": new_wins, "streak": new_streak, "total_battles": new_battles, "coins": new_coins}
            if new_level > self.trainer["level"]:
                updates["level"] = new_level
                updates["rank"] = get_rank(new_level)["name"]

            # Adicionar badge
            if badge:
                badges = self.trainer.get("badges", [])
                if badge not in badges:
                    badges.append(badge)
                    updates["badges"] = badges

            # Adicionar título
            if title:
                titles = self.trainer.get("titles", [])
                if title not in titles:
                    titles.append(title)
                    updates["titles"] = titles
                    updates["active_title"] = title

            await db.update_trainer(self.interaction.user.id, **updates)

            # Dar itens
            for item in items:
                item_type = "ball" if item in ["pokeball", "greatball", "ultraball", "masterball"] else "item"
                await db.add_item(self.interaction.user.id, item_type, item, 1)

            await update_quest_progress(self.interaction.user.id, "wins", 1)
            await add_diary_entry(self.interaction.user.id, "gym_win", f"Derrotou {self.npc_data['name']}", 
                                 f"Venceu {self.npc_data['title']} {self.npc_data['name']} e ganhou a insígnia!")

            embed = discord.Embed(
                title="🏆 Vitória Épica!",
                description=f"""
✦ ─────────────── ✦
**{self.interaction.user.display_name}** derrotou **{self.npc_data['name']}**!
✦ ─────────────── ✦

{self.npc_data['dialogue']['defeat']}

🎁 Recompensas:
✨ +{xp_reward} XP
💰 +{coin_reward} moedas
{'🏅 Insígnia: ' + badge if badge else ''}
{'👑 Título: ' + title if title else ''}
📦 Itens: {', '.join(items)}

Vitórias totais: {new_wins}
                """,
                color=COLORS["premium"]
            )
            if new_level > self.trainer["level"]:
                embed.add_field(name="🎉 Level Up!", value=f"Você subiu para o nível **{new_level}**!", inline=False)

            # Verificar desbloqueio de região
            chapter = STORY_CHAPTERS.get(self.trainer.get("current_chapter", "capitulo_1"))
            if chapter and chapter.get("unlock_region"):
                unlock_embed = await unlock_region(self.interaction.user.id, chapter["unlock_region"])
                if unlock_embed:
                    await interaction.followup.send(embed=unlock_embed)
                    # Avançar capítulo
                    chapters = list(STORY_CHAPTERS.keys())
                    current_idx = chapters.index(self.trainer.get("current_chapter", "capitulo_1"))
                    if current_idx < len(chapters) - 1:
                        next_chapter = chapters[current_idx + 1]
                        await db.update_trainer(self.interaction.user.id, current_chapter=next_chapter)
                        next_chapter_data = STORY_CHAPTERS[next_chapter]
                        await db.add_quest(self.interaction.user.id, {
                            "name": next_chapter_data["name"],
                            "type": "story",
                            "description": next_chapter_data["description"],
                            "requirements": next_chapter_data["requirements"],
                            "reward": next_chapter_data["rewards"],
                            "progress": {}
                        })
        else:
            new_battles = self.trainer["total_battles"] + 1
            await db.update_trainer(self.interaction.user.id, total_battles=new_battles, streak=0)
            embed = discord.Embed(
                title="✖ Derrota",
                description=f"**{self.npc_data['name']}**: {self.npc_data['dialogue']['victory']}",
                color=COLORS["error"]
            )
        await interaction.response.edit_message(embed=embed, view=None)


class BattleView(ui.View):
    def __init__(self, battle_system):
        super().__init__(timeout=120)
        self.battle_system = battle_system

    @ui.button(label="⚔ Ataque 1", style=discord.ButtonStyle.primary)
    async def attack1(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.battle_system.interaction.user.id:
            await interaction.response.send_message("✖ Não é sua batalha!", ephemeral=True)
            return
        await self.battle_system.execute_turn(interaction, 0)

    @ui.button(label="⚔ Ataque 2", style=discord.ButtonStyle.primary)
    async def attack2(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.battle_system.interaction.user.id:
            await interaction.response.send_message("✖ Não é sua batalha!", ephemeral=True)
            return
        await self.battle_system.execute_turn(interaction, 1)

    @ui.button(label="⚔ Ataque 3", style=discord.ButtonStyle.primary)
    async def attack3(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.battle_system.interaction.user.id:
            await interaction.response.send_message("✖ Não é sua batalha!", ephemeral=True)
            return
        await self.battle_system.execute_turn(interaction, 2)

    @ui.button(label="⚔ Ataque 4", style=discord.ButtonStyle.primary)
    async def attack4(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.battle_system.interaction.user.id:
            await interaction.response.send_message("✖ Não é sua batalha!", ephemeral=True)
            return
        await self.battle_system.execute_turn(interaction, 3)

    @ui.button(label="🏃 Fugir", style=discord.ButtonStyle.danger)
    async def flee(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.battle_system.interaction.user.id:
            await interaction.response.send_message("✖ Não é sua batalha!", ephemeral=True)
            return
        embed = discord.Embed(title="🏃 Fuga", description="Você fugiu da batalha!", color=COLORS["warning"])
        await interaction.response.edit_message(embed=embed, view=None)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — LOJA E ECONOMIA
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="shop", description="Abre a loja do Pokémon World em Elyndra")
async def shop_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🏪 Loja Pokémon — Elyndra",
        description=f"""
✦ ─────────────── ✦
Bem-vindo à loja!
✦ ─────────────── ✦

💰 Suas moedas: **{format_number(trainer['coins'])}**

✦ ─── Poké Balls ─── ✦
        """,
        color=COLORS["premium"]
    )

    for item_id, item in SHOP_ITEMS.items():
        if item_id in ["pokeball", "greatball", "ultraball", "masterball"]:
            embed.add_field(name=f"{item['emoji']} {item['name']} — {format_number(item['price'])} 💰", value=item["description"], inline=False)

    embed.add_field(name="✦ ─── Itens ─── ✦", value="Poções, revives e itens de batalha", inline=False)
    for item_id, item in SHOP_ITEMS.items():
        if item_id not in ["pokeball", "greatball", "ultraball", "masterball", "mysterybox", "fire_stone", "water_stone", "thunder_stone", "dragon_scale", "ancient_egg"]:
            embed.add_field(name=f"{item['emoji']} {item['name']} — {format_number(item['price'])} 💰", value=item["description"], inline=True)

    embed.add_field(name="✦ ─── Pedras Evolutivas ─── ✦", value="", inline=False)
    for item_id in ["fire_stone", "water_stone", "thunder_stone", "dragon_scale"]:
        item = SHOP_ITEMS.get(item_id)
        if item:
            embed.add_field(name=f"{item['emoji']} {item['name']} — {format_number(item['price'])} 💰", value=item["description"], inline=True)

    embed.add_field(name="✦ ─── Especiais ─── ✦", value="", inline=False)
    mystery = SHOP_ITEMS.get("mysterybox")
    if mystery:
        embed.add_field(name=f"{mystery['emoji']} {mystery['name']} — {format_number(mystery['price'])} 💰", value=mystery["description"], inline=False)

    view = ShopView(user_id, trainer["coins"])
    await interaction.response.send_message(embed=embed, view=view)


class ShopView(ui.View):
    def __init__(self, user_id, coins):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.coins = coins

    @ui.select(placeholder="📦 Selecione um item para comprar", options=[
        discord.SelectOption(label="Poké Ball", value="pokeball", emoji="⚪", description="200 💰 — Bola básica"),
        discord.SelectOption(label="Great Ball", value="greatball", emoji="🔵", description="600 💰 — Melhor taxa"),
        discord.SelectOption(label="Ultra Ball", value="ultraball", emoji="🟡", description="1200 💰 — Excelente taxa"),
        discord.SelectOption(label="Master Ball", value="masterball", emoji="🔴", description="50000 💰 — Captura garantida"),
        discord.SelectOption(label="Poção", value="potion", emoji="🧪", description="300 💰 — Recupera 20 HP"),
        discord.SelectOption(label="Super Poção", value="superpotion", emoji="🧪", description="700 💰 — Recupera 50 HP"),
        discord.SelectOption(label="Hiper Poção", value="hyperpotion", emoji="🧪", description="1500 💰 — Recupera 200 HP"),
        discord.SelectOption(label="Poção Máxima", value="maxpotion", emoji="🧪", description="3000 💰 — Recupera todo HP"),
        discord.SelectOption(label="Reviver", value="revive", emoji="💊", description="2000 💰 — Revive Pokémon"),
        discord.SelectOption(label="Reviver Máximo", value="maxrevive", emoji="💊", description="5000 💰 — Revive com HP completo"),
        discord.SelectOption(label="X Ataque", value="xattack", emoji="⚔️", description="500 💰 — Aumenta ataque"),
        discord.SelectOption(label="X Defesa", value="xdefense", emoji="🛡️", description="500 💰 — Aumenta defesa"),
        discord.SelectOption(label="Doce Raro", value="rarecandy", emoji="🍬", description="3000 💰 — +1 nível"),
        discord.SelectOption(label="Pedra do Fogo", value="fire_stone", emoji="🔥", description="5000 💰 — Evolução"),
        discord.SelectOption(label="Pedra da Água", value="water_stone", emoji="💧", description="5000 💰 — Evolução"),
        discord.SelectOption(label="Pedra do Trovão", value="thunder_stone", emoji="⚡", description="5000 💰 — Evolução"),
        discord.SelectOption(label="Escama de Dragão", value="dragon_scale", emoji="🐉", description="8000 💰 — Evolução especial"),
        discord.SelectOption(label="Caixa Misteriosa", value="mysterybox", emoji="📦", description="1000 💰 — Surpresa!"),
    ])
    async def shop_select(self, interaction: discord.Interaction, select: ui.Select):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua compra!", ephemeral=True)
            return
        item_id = select.values[0]
        item = SHOP_ITEMS.get(item_id)
        if not item:
            await interaction.response.send_message("✖ Item não encontrado!", ephemeral=True)
            return
        trainer = await db.get_trainer(self.user_id)
        if trainer["coins"] < item["price"]:
            await interaction.response.send_message(f"✖ Moedas insuficientes!", ephemeral=True)
            return
        new_coins = trainer["coins"] - item["price"]
        await db.update_trainer(self.user_id, coins=new_coins)
        if item_id == "mysterybox":
            await self.open_mystery_box(interaction)
        else:
            item_type = "ball" if item_id in ["pokeball", "greatball", "ultraball", "masterball"] else "item"
            await db.add_item(self.user_id, item_type, item_id, 1)
            embed = discord.Embed(title="✔ Compra realizada!", description=f"Você comprou **{item['name']}**!\n\n💰 -{format_number(item['price'])} moedas\n📦 +1 {item['name']}\n\nSaldo: {format_number(new_coins)} 💰", color=COLORS["info"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
        await update_quest_progress(self.user_id, "shop_buy", 1)

    async def open_mystery_box(self, interaction):
        embed = discord.Embed(title="📦 Abrindo caixa...", description="[░░░░░░░░░]", color=COLORS["premium"])
        await interaction.response.send_message(embed=embed)
        for i in range(1, 6):
            await asyncio.sleep(0.5)
            filled = "▓" * i
            empty = "░" * (5 - i)
            embed.description = f"[{filled}{empty}]"
            await interaction.edit_original_response(embed=embed)
        prizes = [("coins", 0.4, {"min": 200, "max": 1000}), ("xp_card", 0.2, None), ("attack_card", 0.15, None), ("potion", 0.1, None), ("pokemon", 0.1, None), ("rarecandy", 0.05, None)]
        prize_type = random.choices([p[0] for p in prizes], weights=[p[1] for p in prizes])[0]
        if prize_type == "coins":
            amount = random.randint(200, 1000)
            trainer = await db.get_trainer(self.user_id)
            await db.update_trainer(self.user_id, coins=trainer["coins"] + amount)
            embed = discord.Embed(title="🎉 Prêmio!", description=f"💰 **{format_number(amount)} moedas!**", color=COLORS["premium"])
        elif prize_type == "pokemon":
            pokemon = await pokeapi.get_random_pokemon(max_id=151)
            if pokemon:
                pokemon["level"] = random.randint(5, 20)
                pokemon["max_hp"] = pokemon["hp"] + (pokemon["level"] * 2)
                pokemon["hp"] = pokemon["max_hp"]
                pokemon["rarity"] = random.choice(["comum", "raro", "epico"])
                pokemon["nature"] = generate_nature()
                pokemon["personality"] = generate_personality()
                pokemon["potential"] = {}
                await db.add_pokemon(self.user_id, pokemon)
                embed = discord.Embed(title="🎉 Pokémon encontrado!", description=f"{get_rarity_emoji(pokemon['rarity'])} **{pokemon['name']}** (Nv. {pokemon['level']})", color=get_rarity_color(pokemon["rarity"]))
                embed.set_image(url=pokemon["sprite_url"])
        else:
            item_names = {"xp_card": "Carta de XP", "attack_card": "Carta de Ataque", "potion": "Poção", "rarecandy": "Doce Raro"}
            await db.add_item(self.user_id, "item", prize_type, 1)
            embed = discord.Embed(title="🎉 Item encontrado!", description=f"📦 **{item_names.get(prize_type, prize_type)}**", color=COLORS["info"])
        await interaction.edit_original_response(embed=embed)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — DAILY, INVENTORY, LEADERBOARD
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="daily", description="Resgata sua recompensa diária em Elyndra")
async def daily_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    can_daily, remaining = await db.check_cooldown(user_id, "daily", 86400)
    if not can_daily:
        embed = discord.Embed(title="⏳ Recompensa diária", description=f"Você já resgatou hoje!\nAguarde **{format_time(remaining)}**.", color=COLORS["warning"])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    streak = trainer.get("streak", 0)
    streak_bonus = min(streak * 50, 500)
    total_coins = DAILY_COINS + streak_bonus
    total_xp = XP_PER_DAILY + (streak * 10)
    new_coins = trainer["coins"] + total_coins
    new_xp = trainer["xp"] + total_xp
    new_level = calculate_level_from_xp(new_xp)
    updates = {"coins": new_coins, "xp": new_xp, "last_daily": datetime.now().isoformat()}
    if new_level > trainer["level"]:
        updates["level"] = new_level
        updates["rank"] = get_rank(new_level)["name"]
    await db.update_trainer(user_id, **updates)

    existing_quests = await db.get_quests(user_id, completed=False)
    if not existing_quests:
        for quest in DAILY_QUESTS:
            await db.add_quest(user_id, quest)

    embed = discord.Embed(
        title="📅 Recompensa Diária — Elyndra",
        description=f"""
✦ ─────────────── ✦
Recompensas resgatadas!
✦ ─────────────── ✦

💰 **+{format_number(total_coins)}** moedas
✨ **+{total_xp}** XP
🔥 Streak: {streak} dias

Saldo: {format_number(new_coins)} 💰
        """,
        color=COLORS["premium"]
    )
    if new_level > trainer["level"]:
        embed.add_field(name="🎉 Level Up!", value=f"Você subiu para o nível **{new_level}**!", inline=False)

    quests = await db.get_quests(user_id, completed=False)
    if quests:
        quest_text = "\n".join([f"📜 {q['quest_name']}: {q['description']}" for q in quests[:3]])
        embed.add_field(name="Missões de Hoje", value=quest_text, inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="inventory", description="Mostra seu inventário em Elyndra")
async def inventory_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    inventory = await db.get_inventory(user_id)
    embed = discord.Embed(title="🎒 Inventário", description=f"💰 **{format_number(trainer['coins'])}** moedas", color=COLORS["info"])
    if not inventory:
        embed.add_field(name="Vazio", value="Seu inventário está vazio. Compre itens na loja!", inline=False)
    else:
        balls = [item for item in inventory if item["item_type"] == "ball"]
        items = [item for item in inventory if item["item_type"] == "item"]
        cards = [item for item in inventory if item["item_type"] == "card"]
        if balls:
            ball_text = "\n".join([f"{SHOP_ITEMS.get(b['item_id'], {}).get('emoji', '⚪')} {SHOP_ITEMS.get(b['item_id'], {}).get('name', b['item_id'])} x{b['quantity']}" for b in balls])
            embed.add_field(name="⚪ Poké Balls", value=ball_text, inline=False)
        if items:
            item_text = "\n".join([f"📦 {b['item_id'].replace('_', ' ').title()} x{b['quantity']}" for b in items])
            embed.add_field(name="🧪 Itens", value=item_text, inline=False)
        if cards:
            card_text = "\n".join([f"🃏 {UPGRADE_CARDS.get(b['item_id'], {}).get('name', b['item_id'])} x{b['quantity']}" for b in cards])
            embed.add_field(name="🃏 Cartas", value=card_text, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="leaderboard", description="Mostra o ranking dos melhores treinadores de Elyndra")
async def leaderboard_command(interaction: discord.Interaction):
    leaderboard = await db.get_leaderboard(10)
    if not leaderboard:
        embed = discord.Embed(title="📈 Ranking", description="Nenhum treinador no ranking ainda!", color=COLORS["warning"])
        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(title="📈 Ranking de Treinadores — Elyndra", description="Os melhores treinadores do continente!", color=COLORS["premium"])
    medals = ["🥇", "🥈", "🥉", "4.", "5.", "6.", "7.", "8.", "9.", "10."]
    for i, entry in enumerate(leaderboard):
        rank = get_rank(entry["level"])
        badges = entry.get("badges", [])
        badges_text = " ".join(["🏅" for _ in badges]) if badges else ""
        embed.add_field(
            name=f"{medals[i]} {entry['username']}",
            value=f"{rank['emoji']} {rank['name']} | ⭐ Nível {entry['level']}\n🎯 {entry['total_catches']} capturas | 🏆 {entry['total_wins']} vitórias {badges_text}",
            inline=False
        )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="help", description="Mostra todos os comandos disponíveis em Elyndra")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✦ Pokémon World — Elyndra — Comandos",
        description="""
Bem-vindo ao mundo de Elyndra! Um RPG completo de Pokémon dentro do Discord.

✦ ─── Início ─── ✦
`/start` — Inicia sua jornada
`/profile` — Seu perfil de treinador

✦ ─── Mundo ─── ✦
`/world` — Mapa de Elyndra
`/explore` — Explorar área atual
`/weather` — Ver clima atual

✦ ─── Pokémon ─── ✦
`/catch` — Capturar Pokémon selvagem
`/pokedex` — Ver seus Pokémon
`/team` — Gerenciar time
`/friendship` — Amizade com Pokémon
`/evolve` — Evoluir Pokémon

✦ ─── Batalhas ─── ✦
`/battle` — Batalhar contra NPC
`/battle_trainer` — Desafiar treinadores importantes
`/pvp` — Desafiar outro jogador
`/raid` — Participar de raid mundial

✦ ─── Economia ─── ✦
`/shop` — Loja de itens
`/inventory` — Seu inventário
`/daily` — Recompensa diária
`/market` — Mercado de jogadores

✦ ─── Social ─── ✦
`/leaderboard` — Ranking de treinadores
`/trade` — Trocar Pokémon
`/gift` — Presentear amigos
`/clan` — Sistema de clãs

✦ ─── Sistema ─── ✦
`/diary` — Diário de jornada
`/quests` — Missões ativas
`/help` — Esta ajuda

✦ ───────────────── ✦
Boa jornada, treinador! ⚔
        """,
        color=COLORS["premium"]
    )
    await interaction.response.send_message(embed=embed)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — AMIZADE E PERSONALIDADE
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="friendship", description="Interage com seus Pokémon para aumentar amizade")
async def friendship_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    team = await db.get_pokemons(user_id, in_team_only=True)
    if not team:
        await interaction.response.send_message("✖ Você não tem Pokémon no time!", ephemeral=True)
        return

    embed = discord.Embed(
        title="💝 Amizade com Pokémon",
        description="Escolha um Pokémon e uma ação para interagir!",
        color=COLORS["premium"]
    )

    view = FriendshipView(user_id, team)
    await interaction.response.send_message(embed=embed, view=view)


class FriendshipView(ui.View):
    def __init__(self, user_id, team):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.team = team

        options = []
        for p in team[:25]:
            friendship = p.get("friendship", 0)
            level = get_friendship_level(friendship)
            options.append(discord.SelectOption(
                label=f"{p['name']} (Nv.{p['level']})",
                value=str(p['id']),
                description=f"{level['emoji']} {level['name']} | Amizade: {friendship}",
                emoji=get_type_emoji(p['types'][0])
            ))

        select = ui.Select(placeholder="Escolha um Pokémon...", options=options[:25])
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua interação!", ephemeral=True)
            return

        select = interaction.data["components"][0]["components"][0]
        pokemon_id = int(select["values"][0])
        pokemon = await db.get_pokemon_by_id(pokemon_id)

        embed = discord.Embed(
            title=f"💝 {pokemon['name']}",
            description=f"""
{get_personality_emoji(pokemon.get('personality', 'agressivo'))} Personalidade: {get_personality_name(pokemon.get('personality', 'agressivo'))}
{create_friendship_bar(pokemon.get('friendship', 0))}

O que deseja fazer?
            """,
            color=COLORS["premium"]
        )
        view = FriendshipActionView(self.user_id, pokemon)
        await interaction.response.edit_message(embed=embed, view=view)


class FriendshipActionView(ui.View):
    def __init__(self, user_id, pokemon):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.pokemon = pokemon

    @ui.button(label="🍎 Alimentar", style=discord.ButtonStyle.primary)
    async def feed(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua interação!", ephemeral=True)
            return

        can_act, remaining = await db.check_cooldown(self.user_id, f"friendship_feed_{self.pokemon['id']}", 3600)
        if not can_act:
            await interaction.response.send_message(f"⏳ Aguarde **{format_time(remaining)}** para alimentar novamente.", ephemeral=True)
            return

        new_friendship = min(500, self.pokemon.get("friendship", 0) + 5)
        await db.update_pokemon(self.pokemon["id"], friendship=new_friendship)

        embed = discord.Embed(
            title="🍎 Alimentando...",
            description=f"Você deu uma fruta deliciosa para **{self.pokemon['name']}**!\n\n💝 Amizade +5!",
            color=COLORS["info"]
        )
        await interaction.response.edit_message(embed=embed, view=None)
        await update_quest_progress(self.user_id, "friendship_actions", 1)

    @ui.button(label="🎾 Brincar", style=discord.ButtonStyle.secondary)
    async def play(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua interação!", ephemeral=True)
            return

        can_act, remaining = await db.check_cooldown(self.user_id, f"friendship_play_{self.pokemon['id']}", 3600)
        if not can_act:
            await interaction.response.send_message(f"⏳ Aguarde **{format_time(remaining)}** para brincar novamente.", ephemeral=True)
            return

        new_friendship = min(500, self.pokemon.get("friendship", 0) + 8)
        await db.update_pokemon(self.pokemon["id"], friendship=new_friendship)

        embed = discord.Embed(
            title="🎾 Brincando...",
            description=f"Você brincou com **{self.pokemon['name']}**! Ele parece muito feliz!\n\n💝 Amizade +8!",
            color=COLORS["info"]
        )
        await interaction.response.edit_message(embed=embed, view=None)
        await update_quest_progress(self.user_id, "friendship_actions", 1)

    @ui.button(label="💪 Treinar", style=discord.ButtonStyle.secondary)
    async def train(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua interação!", ephemeral=True)
            return

        can_act, remaining = await db.check_cooldown(self.user_id, f"friendship_train_{self.pokemon['id']}", 7200)
        if not can_act:
            await interaction.response.send_message(f"⏳ Aguarde **{format_time(remaining)}** para treinar novamente.", ephemeral=True)
            return

        new_friendship = min(500, self.pokemon.get("friendship", 0) + 10)
        new_xp = self.pokemon.get("xp", 0) + 15
        await db.update_pokemon(self.pokemon["id"], friendship=new_friendship, xp=new_xp)

        embed = discord.Embed(
            title="💪 Treinando...",
            description=f"Você treinou com **{self.pokemon['name']}**!\n\n💝 Amizade +10!\n✨ XP +15!",
            color=COLORS["info"]
        )
        await interaction.response.edit_message(embed=embed, view=None)
        await update_quest_progress(self.user_id, "friendship_actions", 1)

    @ui.button(label="🤗 Carinho", style=discord.ButtonStyle.secondary)
    async def pet(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("✖ Não é sua interação!", ephemeral=True)
            return

        can_act, remaining = await db.check_cooldown(self.user_id, f"friendship_pet_{self.pokemon['id']}", 1800)
        if not can_act:
            await interaction.response.send_message(f"⏳ Aguarde **{format_time(remaining)}** para fazer carinho novamente.", ephemeral=True)
            return

        new_friendship = min(500, self.pokemon.get("friendship", 0) + 3)
        await db.update_pokemon(self.pokemon["id"], friendship=new_friendship)

        embed = discord.Embed(
            title="🤗 Carinho...",
            description=f"Você fez carinho em **{self.pokemon['name']}**!\n\n💝 Amizade +3!",
            color=COLORS["info"]
        )
        await interaction.response.edit_message(embed=embed, view=None)
        await update_quest_progress(self.user_id, "friendship_actions", 1)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — CLIMA E DIÁRIO
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="weather", description="Ver o clima atual de Elyndra")
async def weather_command(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    weather = world_state["current_weather"].get(guild_id, "sol")
    weather_data = WEATHER_SYSTEM.get(weather, WEATHER_SYSTEM["sol"])

    embed = discord.Embed(
        title=f"{weather_data['emoji']} Clima Atual — Elyndra",
        description=f"""
✦ ─────────────── ✦
**{weather_data['name']}**
✦ ─────────────── ✦

{weather_data['description']}

📊 Efeitos:
✅ Tipos fortalecidos: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in weather_data.get('type_bonus', [])])}
❌ Tipos enfraquecidos: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in weather_data.get('type_penalty', [])])}
🎯 Taxa de captura: {weather_data.get('catch_modifier', 1.0)}x
📈 Taxa de spawn: {weather_data.get('spawn_rate', 1.0)}x
        """,
        color=COLORS.get(weather, COLORS["info"])
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="diary", description="Ver seu diário de jornada em Elyndra")
async def diary_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    entries = await db.get_diary(user_id, limit=10)
    if not entries:
        embed = discord.Embed(title="📓 Diário de Jornada", description="Seu diário está vazio! Comece a explorar Elyndra!", color=COLORS["info"])
        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(title="📓 Diário de Jornada", description="Suas aventuras em Elyndra:", color=COLORS["premium"])
    for entry in entries[:10]:
        data = entry["entry_data"]
        embed.add_field(
            name=f"{data.get('title', 'Evento')}",
            value=f"{data.get('description', '')}\n🕐 {entry['entry_time'][:16]}",
            inline=False
        )
    await interaction.response.send_message(embed=embed)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — MISSÕES
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="quests", description="Ver suas missões ativas em Elyndra")
async def quests_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    quests = await db.get_quests(user_id, completed=False)
    if not quests:
        embed = discord.Embed(title="📜 Missões", description="Você não tem missões ativas! Use `/daily` para pegar missões diárias.", color=COLORS["info"])
        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(title="📜 Missões Ativas", description=f"Você tem **{len(quests)}** missões ativas:", color=COLORS["premium"])
    for quest in quests[:5]:
        req_type = list(quest["requirements"].keys())[0] if quest["requirements"] else ""
        req_val = quest["requirements"].get(req_type, 0)
        prog_val = quest["progress"].get(req_type, 0)
        embed.add_field(
            name=f"📜 {quest['quest_name']}",
            value=f"{quest['description']}\nProgresso: {prog_val}/{req_val}",
            inline=False
        )
    await interaction.response.send_message(embed=embed)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — PVP (CORRIGIDO)
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="pvp", description="Desafia outro jogador para uma batalha PvP em Elyndra")
@app_commands.describe(opponent="Jogador para desafiar")
async def pvp_command(interaction: discord.Interaction, opponent: discord.Member):
    if opponent.id == interaction.user.id:
        await interaction.response.send_message("✖ Você não pode desafiar a si mesmo!", ephemeral=True)
        return
    if opponent.bot:
        await interaction.response.send_message("✖ Não pode desafiar bots!", ephemeral=True)
        return

    challenger = await db.get_trainer(interaction.user.id)
    opponent_trainer = await db.get_trainer(opponent.id)
    if not challenger or not opponent_trainer:
        await interaction.response.send_message("✖ Ambos os jogadores precisam ter iniciado sua jornada!", ephemeral=True)
        return

    challenger_team = await db.get_pokemons(interaction.user.id, in_team_only=True)
    opponent_team = await db.get_pokemons(opponent.id, in_team_only=True)
    if not challenger_team or not opponent_team:
        await interaction.response.send_message("✖ Ambos os jogadores precisam ter Pokémon no time!", ephemeral=True)
        return

    embed = discord.Embed(
        title="⚔ Desafio PvP",
        description=f"✦ ─────────────── ✦\n**{interaction.user.display_name}** desafiou **{opponent.display_name}**!\n✦ ─────────────── ✦\n\n{opponent.mention}, aceita o desafio?",
        color=COLORS["premium"]
    )
    view = PvPChallengeView(interaction.user.id, opponent.id, challenger_team, opponent_team)
    await interaction.response.send_message(embed=embed, view=view)


class PvPChallengeView(ui.View):
    def __init__(self, challenger_id, opponent_id, challenger_team, opponent_team):
        super().__init__(timeout=60)
        self.challenger_id = challenger_id
        self.opponent_id = opponent_id
        self.challenger_team = challenger_team
        self.opponent_team = opponent_team

    @ui.button(label="✔ Aceitar", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.opponent_id:
            await interaction.response.send_message("✖ Não é seu desafio!", ephemeral=True)
            return
        battle = PvPBattleSystem(interaction, self.challenger_id, self.opponent_id, self.challenger_team, self.opponent_team)
        await battle.start()

    @ui.button(label="✖ Recusar", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.opponent_id:
            await interaction.response.send_message("✖ Não é seu desafio!", ephemeral=True)
            return
        embed = discord.Embed(title="✖ Desafio recusado", description="O desafio foi recusado.", color=COLORS["error"])
        await interaction.response.edit_message(embed=embed, view=None)


class PvPBattleSystem:
    def __init__(self, interaction, challenger_id, opponent_id, challenger_team, opponent_team):
        self.interaction = interaction
        self.challenger_id = challenger_id
        self.opponent_id = opponent_id
        self.challenger_team = [p.copy() for p in challenger_team]
        self.opponent_team = [p.copy() for p in opponent_team]
        self.current_challenger_pokemon = 0
        self.current_opponent_pokemon = 0
        self.turn = 0
        self.battle_log = []
        self.current_turn_player = challenger_id

    async def start(self):
        challenger_pokemon = self.challenger_team[self.current_challenger_pokemon]
        opponent_pokemon = self.opponent_team[self.current_opponent_pokemon]
        embed = discord.Embed(
            title="⚔ Batalha PvP Iniciada!",
            description=f"✦ ─────────────── ✦\n<@{self.challenger_id}> vs <@{self.opponent_id}>\n✦ ─────────────── ✦\n\n🟢 {challenger_pokemon['name']} (Nv. {challenger_pokemon['level']})\nVS\n🔴 {opponent_pokemon['name']} (Nv. {opponent_pokemon['level']})\n\nVez de: <@{self.current_turn_player}>",
            color=COLORS["premium"]
        )
        view = PvPBattleView(self)
        await self.interaction.response.edit_message(embed=embed, view=view)

    async def execute_turn(self, interaction, move_index, player_id):
        if player_id != self.current_turn_player:
            await interaction.response.send_message("✖ Não é sua vez!", ephemeral=True)
            return
        challenger_pokemon = self.challenger_team[self.current_challenger_pokemon]
        opponent_pokemon = self.opponent_team[self.current_opponent_pokemon]
        log_entries = []
        if player_id == self.challenger_id:
            await self.execute_attack(challenger_pokemon, opponent_pokemon, move_index, log_entries, True)
            if opponent_pokemon["hp"] > 0:
                self.current_turn_player = self.opponent_id
            else:
                if self.current_opponent_pokemon < len(self.opponent_team) - 1:
                    self.current_opponent_pokemon += 1
                    log_entries.append(f"🔄 Oponente enviou {self.opponent_team[self.current_opponent_pokemon]['name']}!")
                else:
                    await self.end_battle(interaction, self.challenger_id)
                    return
        else:
            await self.execute_attack(opponent_pokemon, challenger_pokemon, move_index, log_entries, False)
            if challenger_pokemon["hp"] > 0:
                self.current_turn_player = self.challenger_id
            else:
                if self.current_challenger_pokemon < len(self.challenger_team) - 1:
                    self.current_challenger_pokemon += 1
                    log_entries.append(f"🔄 Desafiante enviou {self.challenger_team[self.current_challenger_pokemon]['name']}!")
                else:
                    await self.end_battle(interaction, self.opponent_id)
                    return
        self.battle_log.extend(log_entries)
        self.turn += 1
        await self.update_battle_display(interaction)

    async def execute_attack(self, attacker, defender, move_index, log_entries, is_challenger):
        move = attacker["moves"][move_index] if move_index < len(attacker["moves"]) else "Tackle"
        if is_dodge():
            log_entries.append(f"💨 {defender['name']} esquivou de {move}!")
            return
        attacker_type = attacker["types"][0] if attacker["types"] else "normal"
        effectiveness = calculate_type_effectiveness(attacker_type, defender["types"])
        is_crit = is_critical_hit()
        damage = calculate_damage(attacker, defender, 50, is_crit)
        damage = int(damage * effectiveness)
        defender["hp"] = max(0, defender["hp"] - damage)
        attacker_name = f"🟢 {attacker['name']}" if is_challenger else f"🔴 {attacker['name']}"
        crit_text = " 💥 CRÍTICO!" if is_crit else ""
        effect_text = get_effectiveness_text(effectiveness)
        log_entries.append(f"{attacker_name} usou **{move}**!{crit_text} {effect_text}\n→ {defender['name']} perdeu {damage} HP!")

    async def update_battle_display(self, interaction):
        challenger_pokemon = self.challenger_team[self.current_challenger_pokemon]
        opponent_pokemon = self.opponent_team[self.current_opponent_pokemon]
        recent_log = "\n".join(self.battle_log[-5:]) if self.battle_log else "A batalha começou!"
        embed = discord.Embed(
            title=f"⚔ Turno {self.turn + 1}",
            description=f"""
✦ ─────────────── ✦
<@{self.challenger_id}> vs <@{self.opponent_id}>
✦ ─────────────── ✦

🟢 **{challenger_pokemon['name']}** (Nv. {challenger_pokemon['level']})
{create_hp_bar(challenger_pokemon['hp'], challenger_pokemon['max_hp'])}

🔴 **{opponent_pokemon['name']}** (Nv. {opponent_pokemon['level']})
{create_hp_bar(opponent_pokemon['hp'], opponent_pokemon['max_hp'])}

✦ ─────────────── ✦
📜 Log:
{recent_log}

Vez de: <@{self.current_turn_player}>
            """,
            color=COLORS["premium"]
        )
        view = PvPBattleView(self)
        await interaction.response.edit_message(embed=embed, view=view)

    async def end_battle(self, interaction, winner_id):
        winner_name = "Desafiante" if winner_id == self.challenger_id else "Oponente"
        xp_reward = XP_PER_BATTLE_WIN
        coin_reward = random.randint(200, 500)
        winner_trainer = await db.get_trainer(winner_id)
        if winner_trainer:
            new_xp = winner_trainer["xp"] + xp_reward
            new_wins = winner_trainer["total_wins"] + 1
            new_streak = winner_trainer["streak"] + 1
            new_battles = winner_trainer["total_battles"] + 1
            new_coins = winner_trainer["coins"] + coin_reward
            updates = {"xp": new_xp, "total_wins": new_wins, "streak": new_streak, "total_battles": new_battles, "coins": new_coins}
            new_level = calculate_level_from_xp(new_xp)
            if new_level > winner_trainer["level"]:
                updates["level"] = new_level
                updates["rank"] = get_rank(new_level)["name"]
            await db.update_trainer(winner_id, **updates)
        loser_id = self.opponent_id if winner_id == self.challenger_id else self.challenger_id
        loser_trainer = await db.get_trainer(loser_id)
        if loser_trainer:
            await db.update_trainer(loser_id, total_battles=loser_trainer["total_battles"] + 1, streak=0)
        embed = discord.Embed(
            title="🏆 Batalha PvP Finalizada!",
            description=f"✦ ─────────────── ✦\n**{winner_name}** venceu!\n✦ ─────────────── ✦\n\n🎁 Recompensas para o vencedor:\n✨ +{xp_reward} XP\n💰 +{coin_reward} moedas",
            color=COLORS["premium"]
        )
        await interaction.response.edit_message(embed=embed, view=None)


class PvPBattleView(ui.View):
    def __init__(self, battle_system):
        super().__init__(timeout=120)
        self.battle_system = battle_system

    @ui.button(label="⚔ Ataque 1", style=discord.ButtonStyle.primary)
    async def attack1(self, interaction: discord.Interaction, button: ui.Button):
        await self.battle_system.execute_turn(interaction, 0, interaction.user.id)

    @ui.button(label="⚔ Ataque 2", style=discord.ButtonStyle.primary)
    async def attack2(self, interaction: discord.Interaction, button: ui.Button):
        await self.battle_system.execute_turn(interaction, 1, interaction.user.id)

    @ui.button(label="⚔ Ataque 3", style=discord.ButtonStyle.primary)
    async def attack3(self, interaction: discord.Interaction, button: ui.Button):
        await self.battle_system.execute_turn(interaction, 2, interaction.user.id)

    @ui.button(label="⚔ Ataque 4", style=discord.ButtonStyle.primary)
    async def attack4(self, interaction: discord.Interaction, button: ui.Button):
        await self.battle_system.execute_turn(interaction, 3, interaction.user.id)

    @ui.button(label="🏃 Fugir", style=discord.ButtonStyle.danger)
    async def flee(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id not in [self.battle_system.challenger_id, self.battle_system.opponent_id]:
            await interaction.response.send_message("✖ Não é sua batalha!", ephemeral=True)
            return
        embed = discord.Embed(title="🏃 Fuga", description="A batalha foi encerrada.", color=COLORS["warning"])
        await interaction.response.edit_message(embed=embed, view=None)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — RAID MUNDIAL
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="raid", description="Participa de uma raid mundial em Elyndra")
async def raid_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    active_raids = await db.get_active_raids()
    if not active_raids:
        embed = discord.Embed(title="🌋 Nenhuma Raid Ativa", description="Não há raids ativas no momento. Volte mais tarde!", color=COLORS["warning"])
        await interaction.response.send_message(embed=embed)
        return

    raid = active_raids[0]
    boss = RAID_BOSSES.get(raid["boss_id"], {})

    embed = discord.Embed(
        title=f"🌋 Raid Mundial — {boss.get('name', 'Desconhecido')}",
        description=f"""
✦ ─────────────── ✦
{boss.get('emoji', '🌋')} **{boss.get('name', 'Desconhecido')}**
✦ ─────────────── ✦

{boss.get('description', '')}

❤ HP Restante: {format_number(boss.get('hp', 0) - raid['total_damage'])}/{format_number(boss.get('hp', 0))}
⚔ Ataque: {boss.get('attack', 0)}
🛡 Defesa: {boss.get('defense', 0)}

👥 Participantes: {len(raid.get('participants', []))}

Use `/raid_attack` para atacar!
        """,
        color=COLORS["error"]
    )
    await interaction.response.send_message(embed=embed)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — CLÃ
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="clan", description="Sistema de clãs de Elyndra")
@app_commands.describe(action="Ação: create, join, leave, info, donate")
async def clan_command(interaction: discord.Interaction, action: str, value: str = None):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    if action == "create" and value:
        # Criar clã
        clan_id = await db.create_clan(value, value[:3].upper(), f"Clã {value}", user_id)
        await db.update_trainer(user_id, clan_id=clan_id, clan_role="leader")
        embed = discord.Embed(title="👥 Clã Criado!", description=f"Clã **{value}** criado com sucesso!", color=COLORS["premium"])
        await interaction.response.send_message(embed=embed)
    elif action == "info":
        clan_id = trainer.get("clan_id")
        if not clan_id:
            await interaction.response.send_message("✖ Você não está em um clã!", ephemeral=True)
            return
        clan = await db.get_clan(clan_id)
        if not clan:
            await interaction.response.send_message("✖ Clã não encontrado!", ephemeral=True)
            return
        embed = discord.Embed(title=f"{clan['emblem']} {clan['name']}", description=f"**Tag:** {clan['tag']}\n**Membros:** {len(clan.get('members', []))}\n**Banco:** {format_number(clan.get('bank_coins', 0))} 💰", color=COLORS["premium"])
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("✖ Ação inválida! Use: create, join, leave, info, donate", ephemeral=True)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — MERCADO
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="market", description="Mercado de jogadores de Elyndra")
async def market_command(interaction: discord.Interaction):
    listings = await db.get_market_listings(sold=False)
    if not listings:
        embed = discord.Embed(title="💹 Mercado Mundial", description="Nenhum item à venda no momento.", color=COLORS["info"])
        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(title="💹 Mercado Mundial", description="Itens à venda:", color=COLORS["premium"])
    for listing in listings[:10]:
        item_name = SHOP_ITEMS.get(listing["item_id"], {}).get("name", listing["item_id"])
        embed.add_field(name=f"{item_name} — {format_number(listing['price'])} 💰", value=f"Vendedor: <@{listing['seller_id']}>", inline=False)
    await interaction.response.send_message(embed=embed)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — PRESENTE E TROCA (CORRIGIDOS)
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="gift", description="Presenteia outro jogador com moedas em Elyndra")
@app_commands.describe(user="Jogador para presentear", amount="Quantidade de moedas")
async def gift_command(interaction: discord.Interaction, user: discord.Member, amount: int):
    if amount <= 0:
        await interaction.response.send_message("✖ Quantidade inválida!", ephemeral=True)
        return
    sender = await db.get_trainer(interaction.user.id)
    receiver = await db.get_trainer(user.id)
    if not sender or not receiver:
        await interaction.response.send_message("✖ Ambos os jogadores precisam ter iniciado a jornada!", ephemeral=True)
        return
    if sender["coins"] < amount:
        await interaction.response.send_message(f"✖ Você não tem {format_number(amount)} moedas!", ephemeral=True)
        return
    await db.update_trainer(interaction.user.id, coins=sender["coins"] - amount)
    await db.update_trainer(user.id, coins=receiver["coins"] + amount)
    embed = discord.Embed(
        title="🎁 Presente enviado!",
        description=f"✦ ─────────────── ✦\n**{interaction.user.display_name}** presenteou **{user.display_name}**!\n✦ ─────────────── ✦\n\n💰 **{format_number(amount)}** moedas enviadas!",
        color=COLORS["premium"]
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="trade", description="Inicia uma troca de Pokémon com outro jogador em Elyndra")
@app_commands.describe(user="Jogador para trocar")
async def trade_command(interaction: discord.Interaction, user: discord.Member):
    if user.id == interaction.user.id:
        await interaction.response.send_message("✖ Não pode trocar com si mesmo!", ephemeral=True)
        return
    if user.bot:
        await interaction.response.send_message("✖ Não pode trocar com bots!", ephemeral=True)
        return
    trader1 = await db.get_trainer(interaction.user.id)
    trader2 = await db.get_trainer(user.id)
    if not trader1 or not trader2:
        await interaction.response.send_message("✖ Ambos os jogadores precisam ter iniciado a jornada!", ephemeral=True)
        return
    embed = discord.Embed(
        title="🤝 Troca de Pokémon",
        description=f"✦ ─────────────── ✦\n**{interaction.user.display_name}** quer trocar com **{user.display_name}**!\n✦ ─────────────── ✦\n\n{user.mention}, aceita a troca?",
        color=COLORS["premium"]
    )
    view = TradeView(interaction.user.id, user.id)
    await interaction.response.send_message(embed=embed, view=view)


class TradeView(ui.View):
    def __init__(self, trader1_id, trader2_id):
        super().__init__(timeout=120)
        self.trader1_id = trader1_id
        self.trader2_id = trader2_id

    @ui.button(label="✔ Aceitar", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.trader2_id:
            await interaction.response.send_message("✖ Não é sua troca!", ephemeral=True)
            return
        embed = discord.Embed(title="🤝 Troca aceita!", description="Use `/pokedex` para escolher qual Pokémon trocar. (Sistema em desenvolvimento)", color=COLORS["info"])
        await interaction.response.edit_message(embed=embed, view=None)

    @ui.button(label="✖ Recusar", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.trader2_id:
            await interaction.response.send_message("✖ Não é sua troca!", ephemeral=True)
            return
        embed = discord.Embed(title="✖ Troca recusada", description="A troca foi recusada.", color=COLORS["error"])
        await interaction.response.edit_message(embed=embed, view=None)


# ═══════════════════════════════════════════════════════════════
# COMANDOS — ADMIN
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="admin_spawn_channel", description="[Admin] Define o canal de spawns")
@app_commands.describe(channel="Canal para spawns")
async def admin_spawn_channel_command(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("✖ Apenas administradores!", ephemeral=True)
        return
    world_state["spawn_channels"][interaction.guild_id] = channel.id
    embed = discord.Embed(title="✔ Canal Configurado", description=f"Canal de spawns definido para {channel.mention}", color=COLORS["info"])
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="admin_force_weather", description="[Admin] Força o clima atual")
@app_commands.describe(weather="Clima: sol, chuva, tempestade, neve, nevoa")
async def admin_force_weather_command(interaction: discord.Interaction, weather: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("✖ Apenas administradores!", ephemeral=True)
        return
    if weather not in WEATHER_SYSTEM:
        await interaction.response.send_message(f"✖ Clima inválido! Opções: {', '.join(WEATHER_SYSTEM.keys())}", ephemeral=True)
        return
    world_state["current_weather"][interaction.guild_id] = weather
    embed = discord.Embed(title=f"{WEATHER_SYSTEM[weather]['emoji']} Clima Alterado", description=f"Clima forçado para **{WEATHER_SYSTEM[weather]['name']}**", color=COLORS["info"])
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="admin_force_spawn", description="[Admin] Força um spawn imediato")
async def admin_force_spawn_command(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("✖ Apenas administradores!", ephemeral=True)
        return
    await interaction.response.send_message("🌩 Forçando spawn...", ephemeral=True)
    # Trigger spawn manually
    await wild_spawn_loop()


# ═══════════════════════════════════════════════════════════════
# INICIAR BOT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ ERRO: Variável DISCORD_TOKEN não encontrada!")
        print("Configure a variável de ambiente DISCORD_TOKEN no Railway.")
        exit(1)
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")
