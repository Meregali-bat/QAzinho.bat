import discord
from functools import wraps

def canal_especifico(nome_canal):
    def decorator(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            canal_especifico_obj = discord.utils.get(ctx.guild.text_channels, name=nome_canal)
            if ctx.channel.name != nome_canal:
                await ctx.send(f'Comandos só devem ser utilizados no canal {canal_especifico_obj.mention}.', delete_after=5)
                await ctx.message.delete()
                return
            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator