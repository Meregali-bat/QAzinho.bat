# command_error.py
import discord
from discord.ext import commands

async def command_error(ctx, error):
    canal_especifico = '𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖'
    canal_especifico_obj = discord.utils.get(ctx.guild.text_channels, name=canal_especifico)
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Comando não reconhecido. Por favor, use um comando válido. \n\
Utilize !Comandos no canal {canal_especifico_obj.mention} para ver os comandos válidos', delete_after=10)
        await ctx.message.delete()