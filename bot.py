"""
Pokémon World - Bot Discord
RPG de Pokémon completo para Discord
"""
import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
import asyncio
import json
import random
from datetime import datetime, timedelta

from config import (
    DISCORD_TOKEN, BOT_NAME, COLORS, EMOJIS, XP_COOLDOWN_SECONDS, XP_PER_MESSAGE,
    XP_PER_CATCH, XP_PER_BATTLE_WIN, XP_PER_QUEST, XP_PER_DAILY, DAILY_COINS,
    STARTING_COINS, SHOP_ITEMS, UPGRADE_CARDS, DAILY_QUESTS, SPECIALIZATIONS,
    RARITY_CHANCES, MAX_TEAM_SIZE, BASE_CATCH_RATE
)
from database import db
from pokeapi import pokeapi
from utils import (
    calculate_xp_for_level, calculate_level_from_xp, get_rank, create_progress_bar,
    create_hp_bar, create_xp_bar, get_type_emoji, get_rarity_emoji, get_rarity_color,
    format_rarity_name, calculate_type_effectiveness, get_effectiveness_text,
    calculate_damage, is_critical_hit, is_dodge, generate_nature, format_number,
    format_time, get_pokemon_card_description, create_box_animation,
    get_random_move_for_type
)

# INTENTS E BOT
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# EVENTOS

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

# TAREFAS PERIODICAS

@tasks.loop(hours=24)
async def daily_quest_reset():
    pass

@tasks.loop(minutes=5)
async def cleanup_battles():
    pass

