import discord
from functools import wraps

def canal_especifico(nome_canal):
    def decorator(func):
        @wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            canal_especifico_obj = discord.utils.get(interaction.guild.text_channels, name=nome_canal)
            if interaction.channel.name != nome_canal:
                await interaction.response.send_message(f'Comandos só devem ser utilizados no canal {canal_especifico_obj.mention}.', ephemeral=True)
                return
            return await func(interaction, *args, **kwargs)
        return wrapper
    return decorator