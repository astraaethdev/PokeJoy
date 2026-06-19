"""
Pokémon World - Bot Discord
"""
import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
import asyncio
import random
from datetime import datetime

from config import (
    DISCORD_TOKEN, BOT_NAME, COLORS, XP_COOLDOWN_SECONDS, XP_PER_MESSAGE,
    XP_PER_CATCH, XP_PER_BATTLE_WIN, XP_PER_DAILY, DAILY_COINS,
    STARTING_COINS, SHOP_ITEMS, UPGRADE_CARDS, DAILY_QUESTS,
    RARITY_CHANCES, MAX_TEAM_SIZE, BASE_CATCH_RATE
)
from database import db
from pokeapi import pokeapi
from utils import (
    calculate_xp_for_level, calculate_level_from_xp, get_rank,
    create_hp_bar, create_xp_bar, get_type_emoji, get_rarity_emoji,
    get_rarity_color, format_rarity_name, calculate_type_effectiveness,
    get_effectiveness_text, calculate_damage, is_critical_hit, is_dodge,
    generate_nature, format_number, format_time, get_random_move_for_type
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await db.init()
    await bot.tree.sync()
    print(f"✦ {BOT_NAME} online como {bot.user.name}")
    print(f"✦ ID: {bot.user.id}")
    print(f"✦ Servidores: {len(bot.guilds)}")
    daily_quest_reset.start()
    cleanup_battles.start()

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
    await bot.process_commands(message)

@tasks.loop(hours=24)
async def daily_quest_reset():
    pass

@tasks.loop(minutes=5)
async def cleanup_battles():
    pass

# === COMANDOS ===

@bot.tree.command(name="start", description="Inicia sua jornada como treinador Pokémon")
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
        starter_pokemon["max_hp"] = starter_pokemon["hp"] + 10
        starter_pokemon["hp"] = starter_pokemon["max_hp"]
        starter_pokemon["attack"] = starter_pokemon["attack"] + 5
        starter_pokemon["defense"] = starter_pokemon["defense"] + 5
        starter_pokemon["speed"] = starter_pokemon["speed"] + 5
        starter_pokemon["rarity"] = "comum"
        starter_pokemon["nature"] = generate_nature()
        starter_pokemon["potential"] = {}
        starter_pokemon["is_shiny"] = False

        pokemon_id = await db.add_pokemon(user_id, starter_pokemon)
        await db.update_pokemon(pokemon_id, is_in_team=1, team_position=0)

    await db.add_item(user_id, "ball", "pokeball", 10)
    await db.add_item(user_id, "potion", "potion", 5)

    embed = discord.Embed(
        title="✦ Bem-vindo ao Pokémon World",
        description=f"""
Olá, **{interaction.user.display_name}**!

Sua jornada como treinador começou! Você recebeu:

☆ Pokémon inicial: **{starter_pokemon['name']}** (Nível 5)
⚪ 10 Poké Balls
🧪 5 Poções
💰 {STARTING_COINS} moedas

✦ Comandos essenciais:
→ `/profile` — Ver seu perfil
→ `/pokedex` — Ver seus Pokémon
→ `/catch` — Capturar Pokémon
→ `/battle` — Batalhar
→ `/shop` — Loja
→ `/help` — Ajuda completa

Boa sorte em sua jornada! ⚔
        """,
        color=COLORS["premium"]
    )
    embed.set_thumbnail(url=starter_pokemon["sprite_url"])
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="profile", description="Mostra seu perfil de treinador")
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

    embed = discord.Embed(title=f"✦ {interaction.user.display_name}", color=COLORS["premium"])
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    embed.add_field(
        name="📊 Informações",
        value=f"""
{rank['emoji']} **Rank:** {rank['name']}
⭐ **Nível:** {trainer['level']}
{xp_bar}
💰 **Moedas:** {format_number(trainer['coins'])}
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
        """,
        inline=True
    )

    if team:
        team_text = "\n".join([
            f"{i+1}. {get_type_emoji(p['types'][0])} **{p['name']}** (Nv. {p['level']}) {'✨' if p['is_shiny'] else ''}"
            for i, p in enumerate(team[:6])
        ])
        embed.add_field(name="⚔ Time Atual", value=team_text, inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="pokedex", description="Ver seus Pokémon capturados")
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
            description="Você ainda não capturou nenhum Pokémon!\nUse `/catch` para começar.",
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
        value = f"""
{get_rarity_emoji(pokemon['rarity'])} {format_rarity_name(pokemon['rarity'])}{shiny_text}{team_text}
Tipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in pokemon['types']])}
❤ {pokemon['hp']}/{pokemon['max_hp']} | ⚔ {pokemon['attack']} | 🛡 {pokemon['defense']} | 💨 {pokemon['speed']}
📊 Nível {pokemon['level']} | ✨ {pokemon['xp']} XP
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
            value = f"""
{get_rarity_emoji(pokemon['rarity'])} {format_rarity_name(pokemon['rarity'])}{shiny_text}{team_text}
Tipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in pokemon['types']])}
❤ {pokemon['hp']}/{pokemon['max_hp']} | ⚔ {pokemon['attack']} | 🛡 {pokemon['defense']} | 💨 {pokemon['speed']}
📊 Nível {pokemon['level']} | ✨ {pokemon['xp']} XP
            """
            embed.add_field(
                name=f"#{pokemon['pokedex_number']} {pokemon['name']}{shiny_text}",
                value=value,
                inline=False
            )

        await interaction.response.edit_message(embed=embed, view=self)


@bot.tree.command(name="catch", description="Tenta capturar um Pokémon selvagem")
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

    wild_pokemon = await pokeapi.get_random_pokemon(max_id=151, rarity_weights=RARITY_CHANCES)
    if not wild_pokemon:
        await interaction.response.send_message("⚠ Erro ao gerar Pokémon. Tente novamente.", ephemeral=True)
        return

    level = random.randint(1, max(5, trainer["level"] + 5))
    wild_pokemon["level"] = level
    wild_pokemon["max_hp"] = wild_pokemon["hp"] + (level * 2)
    wild_pokemon["hp"] = wild_pokemon["max_hp"]
    wild_pokemon["attack"] = wild_pokemon["attack"] + level
    wild_pokemon["defense"] = wild_pokemon["defense"] + level
    wild_pokemon["speed"] = wild_pokemon["speed"] + level
    wild_pokemon["nature"] = generate_nature()
    wild_pokemon["potential"] = {}

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
        title="✦ Um Pokémon selvagem apareceu!",
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

        embed = discord.Embed(
            title="✦ Capturando...",
            description="A Poké Ball balança...\n\n[░░░░░░░░░]",
            color=COLORS["premium"]
        )
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
                embed.add_field(
                    name="🎉 Level Up!",
                    value=f"Você subiu para o nível **{new_level}**!\nNovo rank: **{get_rank(new_level)['name']}** {get_rank(new_level)['emoji']}",
                    inline=False
                )
        else:
            embed = discord.Embed(
                title="✖ Escapou!",
                description=f"**{self.wild_pokemon['name']}** escapou da Poké Ball!\n\nO Pokémon fugiu para a floresta...",
                color=COLORS["error"]
            )

        await interaction.edit_original_response(embed=embed, view=None)


@bot.tree.command(name="battle", description="Inicia uma batalha PvE contra um treinador NPC")
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
            npc_pokemon["moves"] = [get_random_move_for_type(npc_pokemon["types"][0]) for _ in range(4)]
            npc_team.append(npc_pokemon)

    battle = BattleSystem(interaction, team, npc_team, trainer, npc_name)
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

        log_entries.append(
            f"{attacker_name} usou **{move}**!{crit_text} {effect_text}\n"
            f"→ {defender['name']} perdeu {damage} HP!"
        )

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

            updates = {
                "xp": new_xp,
                "total_wins": new_wins,
                "streak": new_streak,
                "total_battles": new_battles,
                "coins": self.trainer["coins"] + coin_reward
            }
            if new_level > self.trainer["level"]:
                updates["level"] = new_level
                updates["rank"] = get_rank(new_level)["name"]

            await db.update_trainer(self.interaction.user.id, **updates)

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
                embed.add_field(
                    name="🎉 Level Up!",
                    value=f"Você subiu para o nível **{new_level}**!\nNovo rank: **{get_rank(new_level)['name']}** {get_rank(new_level)['emoji']}",
                    inline=False
                )
        else:
            new_battles = self.trainer["total_battles"] + 1
            await db.update_trainer(
                self.interaction.user.id,
                total_battles=new_battles,
                streak=0
            )

            embed = discord.Embed(
                title="✖ Derrota",
                description=f"**{self.npc_name}** venceu a batalha...\n\nNão desista! Treine seus Pokémon e tente novamente!\n\n✨ +{XP_PER_BATTLE_WIN // 2} XP (participação)\n🔥 Streak resetado",
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


@bot.tree.command(name="shop", description="Abre a loja do Pokémon World")
async def shop_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🏪 Loja Pokémon",
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
            embed.add_field(
                name=f"{item['emoji']} {item['name']} — {format_number(item['price'])} 💰",
                value=item["description"],
                inline=False
            )

    embed.add_field(name="✦ ─── Itens ─── ✦", value="Poções, revives e itens de batalha", inline=False)

    for item_id, item in SHOP_ITEMS.items():
        if item_id not in ["pokeball", "greatball", "ultraball", "masterball", "mysterybox"]:
            embed.add_field(
                name=f"{item['emoji']} {item['name']} — {format_number(item['price'])} 💰",
                value=item["description"],
                inline=True
            )

    embed.add_field(name="✦ ─── Especiais ─── ✦", value="", inline=False)
    mystery = SHOP_ITEMS.get("mysterybox")
    if mystery:
        embed.add_field(
            name=f"{mystery['emoji']} {mystery['name']} — {format_number(mystery['price'])} 💰",
            value=mystery["description"],
            inline=False
        )

    view = ShopView(user_id, trainer["coins"])
    await interaction.response.send_message(embed=embed, view=view)


class ShopView(ui.View):
    def __init__(self, user_id, coins):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.coins = coins

    @ui.select(
        placeholder="📦 Selecione um item para comprar",
        options=[
            discord.SelectOption(label="Poké Ball", value="pokeball", emoji="⚪", description="200 💰 — Bola básica"),
            discord.SelectOption(label="Great Ball", value="greatball", emoji="🔵", description="600 💰 — Melhor taxa"),
            discord.SelectOption(label="Ultra Ball", value="ultraball", emoji="🟡", description="1200 💰 — Excelente taxa"),
            discord.SelectOption(label="Master Ball", value="masterball", emoji="🔴", description="50000 💰 — Captura garantida"),
            discord.SelectOption(label="Poção", value="potion", emoji="🧪", description="300 💰 — Recupera 20 HP"),
            discord.SelectOption(label="Super Poção", value="superpotion", emoji="🧪", description="700 💰 — Recupera 50 HP"),
            discord.SelectOption(label="Hiper Poção", value="hyperpotion", emoji="🧪", description="1500 💰 — Recupera 200 HP"),
            discord.SelectOption(label="Reviver", value="revive", emoji="💊", description="2000 💰 — Revive Pokémon"),
            discord.SelectOption(label="Doce Raro", value="rarecandy", emoji="🍬", description="3000 💰 — +1 nível"),
            discord.SelectOption(label="Caixa Misteriosa", value="mysterybox", emoji="📦", description="1000 💰 — Surpresa!"),
        ]
    )
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
            await interaction.response.send_message(
                f"✖ Moedas insuficientes! Você tem {format_number(trainer['coins'])} 💰, precisa de {format_number(item['price'])} 💰.",
                ephemeral=True
            )
            return

        new_coins = trainer["coins"] - item["price"]
        await db.update_trainer(self.user_id, coins=new_coins)

        if item_id == "mysterybox":
            await self.open_mystery_box(interaction)
        else:
            if item_id in ["pokeball", "greatball", "ultraball", "masterball"]:
                await db.add_item(self.user_id, "ball", item_id, 1)
            else:
                await db.add_item(self.user_id, "item", item_id, 1)

            embed = discord.Embed(
                title="✔ Compra realizada!",
                description=f"Você comprou **{item['name']}**!\n\n💰 -{format_number(item['price'])} moedas\n📦 +1 {item['name']}\n\nSaldo restante: {format_number(new_coins)} 💰",
                color=COLORS["info"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def open_mystery_box(self, interaction):
        embed = discord.Embed(title="📦 Abrindo caixa...", description="[░░░░░░░░░]", color=COLORS["premium"])
        await interaction.response.send_message(embed=embed)

        await asyncio.sleep(0.5)
        embed.description = "[▓░░░░░░░░]"
        await interaction.edit_original_response(embed=embed)
        await asyncio.sleep(0.5)
        embed.description = "[▓▓▓░░░░░░]"
        await interaction.edit_original_response(embed=embed)
        await asyncio.sleep(0.5)
        embed.description = "[▓▓▓▓▓▓░░░]"
        await interaction.edit_original_response(embed=embed)
        await asyncio.sleep(0.5)
        embed.description = "[▓▓▓▓▓▓▓▓▓]"
        await interaction.edit_original_response(embed=embed)
        await asyncio.sleep(0.5)

        prizes = [
            ("coins", 0.4, {"min": 200, "max": 1000}),
            ("xp_card", 0.2, None),
            ("attack_card", 0.15, None),
            ("potion", 0.1, None),
            ("pokemon", 0.1, None),
            ("rarecandy", 0.05, None),
        ]

        prize_type = random.choices([p[0] for p in prizes], weights=[p[1] for p in prizes])[0]

        if prize_type == "coins":
            amount = random.randint(200, 1000)
            trainer = await db.get_trainer(self.user_id)
            await db.update_trainer(self.user_id, coins=trainer["coins"] + amount)

            embed = discord.Embed(
                title="🎉 Prêmio!",
                description=f"✦ ─────────────── ✦\nVocê encontrou:\n✦ ─────────────── ✦\n\n💰 **{format_number(amount)} moedas!**\n\nParabéns!",
                color=COLORS["premium"]
            )

        elif prize_type == "pokemon":
            pokemon = await pokeapi.get_random_pokemon(max_id=151)
            if pokemon:
                pokemon["level"] = random.randint(5, 20)
                pokemon["max_hp"] = pokemon["hp"] + (pokemon["level"] * 2)
                pokemon["hp"] = pokemon["max_hp"]
                pokemon["rarity"] = random.choice(["comum", "raro", "epico"])
                pokemon["nature"] = generate_nature()
                pokemon["potential"] = {}
                await db.add_pokemon(self.user_id, pokemon)

                embed = discord.Embed(
                    title="🎉 Pokémon encontrado!",
                    description=f"✦ ─────────────── ✦\nVocê encontrou:\n✦ ─────────────── ✦\n\n{get_rarity_emoji(pokemon['rarity'])} **{pokemon['name']}** (Nv. {pokemon['level']})\n\nTipo: {', '.join([get_type_emoji(t) + ' ' + t.capitalize() for t in pokemon['types']])}",
                    color=get_rarity_color(pokemon["rarity"])
                )
                embed.set_image(url=pokemon["sprite_url"])

        else:
            item_names = {"xp_card": "Carta de XP", "attack_card": "Carta de Ataque", "potion": "Poção", "rarecandy": "Doce Raro"}
            await db.add_item(self.user_id, "item", prize_type, 1)

            embed = discord.Embed(
                title="🎉 Item encontrado!",
                description=f"✦ ─────────────── ✦\nVocê encontrou:\n✦ ─────────────── ✦\n\n📦 **{item_names.get(prize_type, prize_type)}**\n\nParabéns!",
                color=COLORS["info"]
            )

        await interaction.edit_original_response(embed=embed)


@bot.tree.command(name="daily", description="Resgata sua recompensa diária")
async def daily_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    can_daily, remaining = await db.check_cooldown(user_id, "daily", 86400)
    if not can_daily:
        embed = discord.Embed(
            title="⏳ Recompensa diária",
            description=f"Você já resgatou hoje!\nAguarde **{format_time(remaining)}**.",
            color=COLORS["warning"]
        )
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
        title="📅 Recompensa Diária",
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


@bot.tree.command(name="inventory", description="Mostra seu inventário")
async def inventory_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer = await db.get_trainer(user_id)
    if not trainer:
        await interaction.response.send_message("✖ Use `/start` primeiro!", ephemeral=True)
        return

    inventory = await db.get_inventory(user_id)

    embed = discord.Embed(
        title="🎒 Inventário",
        description=f"💰 **{format_number(trainer['coins'])}** moedas",
        color=COLORS["info"]
    )

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


@bot.tree.command(name="leaderboard", description="Mostra o ranking dos melhores treinadores")
async def leaderboard_command(interaction: discord.Interaction):
    leaderboard = await db.get_leaderboard(10)
    if not leaderboard:
        embed = discord.Embed(title="📈 Ranking", description="Nenhum treinador no ranking ainda!", color=COLORS["warning"])
        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(title="📈 Ranking de Treinadores", description="Os melhores treinadores do servidor!", color=COLORS["premium"])
    medals = ["🥇", "🥈", "🥉", "4.", "5.", "6.", "7.", "8.", "9.", "10."]

    for i, entry in enumerate(leaderboard):
        rank = get_rank(entry["level"])
        embed.add_field(
            name=f"{medals[i]} {entry['username']}",
            value=f"{rank['emoji']} {rank['name']} | ⭐ Nível {entry['level']}\n🎯 {entry['total_catches']} capturas | 🏆 {entry['total_wins']} vitórias",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="help", description="Mostra todos os comandos disponíveis")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✦ Pokémon World — Comandos",
        description="""
Bem-vindo ao Pokémon World! Um RPG completo de Pokémon dentro do Discord.

✦ ─── Início ─── ✦
`/start` — Inicia sua jornada
`/profile` — Seu perfil de treinador

✦ ─── Pokémon ─── ✦
`/catch` — Capturar Pokémon selvagem
`/pokedex` — Ver seus Pokémon
`/team` — Gerenciar time

✦ ─── Batalhas ─── ✦
`/battle` — Batalhar contra NPC
`/pvp` — Desafiar outro jogador

✦ ─── Economia ─── ✦
`/shop` — Loja de itens
`/inventory` — Seu inventário
`/daily` — Recompensa diária

✦ ─── Social ─── ✦
`/leaderboard` — Ranking de treinadores
`/trade` — Trocar Pokémon
`/gift` — Presentear amigos

✦ ─── Sistema ─── ✦
`/help` — Esta ajuda

✦ ───────────────── ✦
Boa jornada, treinador! ⚔
        """,
        color=COLORS["premium"]
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="pvp", description="Desafia outro jogador para uma batalha PvP")
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
            description=f"✦ ─────────────── ✦\n**{winner_name}** venceu!\n✦ ─────────────── ✦\n\n🎁 Recompensas para o vencedor:\n✨ +{xp_reward} XP\n💰 +{coin_reward} moedas\n\nParabéns aos dois pela batalha épica!",
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


@bot.tree.command(name="gift", description="Presenteia outro jogador com moedas")
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
        description=f"✦ ─────────────── ✦\n**{interaction.user.display_name}** presenteou **{user.display_name}**!\n✦ ─────────────── ✦\n\n💰 **{format_number(amount)}** moedas enviadas!\n\nSaldo restante: {format_number(sender['coins'] - amount)} 💰",
        color=COLORS["premium"]
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="trade", description="Inicia uma troca de Pokémon com outro jogador")
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


# === INICIAR BOT ===

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ ERRO: Variável DISCORD_TOKEN não encontrada!")
        print("Configure a variável de ambiente DISCORD_TOKEN no Railway.")
        exit(1)

    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")
