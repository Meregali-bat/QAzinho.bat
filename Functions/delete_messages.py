import discord
import asyncio
from datetime import datetime, timedelta, timezone

async def delete_bot_and_command_messages(channel):
    now = datetime.now(timezone.utc)
    async for message in channel.history(limit=100):
            message_age = now - message.created_at
            if message_age > timedelta(minutes=5):
                try:
                    await message.delete()
                    await asyncio.sleep(1)
                except discord.errors.HTTPException as e:
                    if e.status == 429:
                        retry_after = e.retry_after
                        print(f"Rate limited. Retrying in {retry_after} seconds.")
                        await asyncio.sleep(retry_after)
                        
async def delete_superusuario(channel,bot):
    now = datetime.now(timezone.utc)
    channel = discord.utils.get(bot.get_all_channels(), name='𝕾𝖚𝖕𝖊𝖗𝖀𝖘𝖚𝖆𝖗𝖎𝖔🔧')
    async for message in channel.history(limit=100):
            message_age = now - message.created_at
            if message_age > timedelta(days=3):
                try:
                    await message.delete()
                    await asyncio.sleep(1)
                except discord.errors.HTTPException as e:
                    if e.status == 429:
                        retry_after = e.retry_after
                        print(f"Rate limited. Retrying in {retry_after} seconds.")
                        await asyncio.sleep(retry_after)