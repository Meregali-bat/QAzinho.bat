# Import the required modules
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageOps
import aiohttp
import io
from supabase import create_client, Client
from datetime import datetime
from functools import wraps

load_dotenv()

# Consume supabase database
supabase_url: str = os.getenv('SUPABASE_URL')
supabase_key: str = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Create a Discord client instance and set the command prefix
intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

# Set the confirmation message when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

#Funcões

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

# Comandos automáticos
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='hora_do_café')
    if channel:
        # Download the user's avatar
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as response:
                avatar_bytes = await response.read()

        # Open the avatar image
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")

        # Resize the avatar to fit the background
        avatar_size = (100, 100)
        avatar = avatar.resize(avatar_size)

        # Create a circular mask
        mask = Image.new("L", avatar_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + avatar_size, fill=255)

        # Apply the mask to the avatar
        avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        avatar.putalpha(mask)

        # Create a new image with a white border around the circular avatar
        border_size = 4
        border_avatar_size = (avatar_size[0] + 2 * border_size, avatar_size[1] + 2 * border_size)
        border_avatar = Image.new("RGBA", border_avatar_size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(border_avatar)
        draw.ellipse((0, 0) + border_avatar_size, fill=(255, 255, 255, 255))
        border_avatar.paste(avatar, (border_size, border_size), avatar)

        # Open the background image
        bg_image = Image.open('background2.png')

        # Calculate the position to center the avatar on the background
        bg_width, bg_height = bg_image.size
        avatar_width, avatar_height = border_avatar.size
        position = (
            (bg_width - avatar_width) // 2,
            (bg_height - avatar_height) // 2
        )

        # Paste the avatar with border onto the background
        bg_image.paste(border_avatar, position, border_avatar)

        # Add text to the image
        draw = ImageDraw.Draw(bg_image)
        font = ImageFont.truetype("arial.ttf", 20)
        text = f'Bem-vindo, {member.name}, novo suporte do grupo W2A!'
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_position = (
            (bg_width - text_width) // 2,
            position[1] + avatar_height + 10
        )
        draw.text(text_position, text, (255, 255, 255), font=font)

        # Save the image to a BytesIO object
        with io.BytesIO() as image_binary:
            bg_image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await channel.send(file=discord.File(fp=image_binary, filename='welcome.png'))

@bot.event
async def on_command_error(ctx, error):
    canal_especifico = 'qazinho-comandos'
    canal_especifico_obj = discord.utils.get(ctx.guild.text_channels, name=canal_especifico)
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Comando não reconhecido. Por favor, use um comando válido. \n\
Utilize !Comandos no canal {canal_especifico_obj.mention} para ver os comandos válidos', delete_after=10)
        await ctx.message.delete()

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        response = '```Os comandos disponíveis são:\n\
!AnydeskSuporte\n\
!Comandos\n\
!CvBottero\n\
!CvToque\n\
!Incidente\n\
!IncidenteApp\n\
!Logs\n\
!Manual\n\
!SuperUsuario\n\
!TemaBottero\n\
!TemaMercado```'
        await message.channel.send(response)
    
    # Processar outros comandos normalmente
    await bot.process_commands(message)

#Comandos manuais
@bot.command()
@canal_especifico('qazinho-comandos')
async def Anydesk(ctx):
    response = supabase.table("AnydeskSuporte").select("Anydesk, Password").execute()
    usuario_formatado = "\n\n".join([f"## 🢡Anydesk🢠\n```{item['Anydesk']}```\n## 🢡Password🢠\n```{item['Password']}```" for item in response.data])
    await ctx.send(usuario_formatado)
    

@bot.command()
@canal_especifico('qazinho-comandos')
async def Incidente(ctx):
    response = supabase.table("IncidenteAPI").select("LayoutIncApi").execute()
    IncidenteFormatado = "\n\n".join([f"```{item['LayoutIncApi']}```" for item in response.data])
    await ctx.send(IncidenteFormatado)

@bot.command()
@canal_especifico('qazinho-comandos')
async def IncidenteApp(ctx):
    response = supabase.table("IncidenteAPP").select("LayoutIncApp").execute()
    IncidenteFormatado = "\n\n".join([f"```{item['LayoutIncApp']}```" for item in response.data])
    await ctx.send(IncidenteFormatado)
    
@bot.command()
@canal_especifico('qazinho-comandos')
async def TemaMercado(ctx):
    response = ' ```sql\n\
update CONFIGURACOES \n\
set CONFIGURACOES.TEMAPDV = "Market" ```'
    await ctx.send(response)

@bot.command()
@canal_especifico('qazinho-comandos')
async def TemaBottero(ctx):
    response = ' ```sql\n\
update CONFIGURACOES \n\
set CONFIGURACOES.TEMAPDV = "Botterocampanha" ```'
    await ctx.send(response)

@bot.command()
@canal_especifico('qazinho-comandos')
async def Logs(ctx):  
    response = ' ```sql\n\
select *\n\
from logs l\n\
order by id desc\n\
limit 100 ```'
    await ctx.send(response)

@bot.command()
@canal_especifico('qazinho-comandos')
async def SuperUsuario(ctx):
    response = supabase.table("SuperUsuario").select("login, password").execute()
    if response.data:
        # Formatar a resposta para uma string legível, pulando a coluna ID
        formatted_response = "\n\n".join([f"# 🢡SuperUsuário🢠\n ## 🢡Login🢠\n```{item['login']}```\n## 🢡Senha🢠\n```{item['password']}```" for item in response.data])
    else:
        formatted_response = "Nenhum dado encontrado."

    await ctx.send(formatted_response)
    
@bot.command()
async def UpdateHash(ctx, nova_senha: str):
    # Atualizar a coluna password na linha de id 1
    canal_especifico = 'adm'
    canal_especifico_obj = discord.utils.get(ctx.guild.text_channels, name=canal_especifico)
    if ctx.channel.name != canal_especifico:
        await ctx.send(f'Comandos só devem ser utilizados no canal {canal_especifico_obj.mention}.',delete_after=5)
        await ctx.message.delete()
        return
    else:  
        response = supabase.table("SuperUsuario").update({"password": nova_senha}).eq("id", 1).execute()
    
    if response.data:
        # Enviar mensagem de confirmação no canal onde a atualização foi feita
        await ctx.send("Senha atualizada com sucesso.")
        
        # Obter o cargo específico
        cargo_especifico = discord.utils.get(ctx.guild.roles, name='CX') 
        # Obter o canal de aviso
        canal_aviso = discord.utils.get(ctx.guild.text_channels, name='superusuario')
        
        if canal_aviso:
            if cargo_especifico:
                usuario = supabase.table("SuperUsuario").select("login, password").execute()
                if usuario:
                    usuario_formatado = "\n\n".join([f"## 🢡Login🢠\n```{item['login']}```\n## 🢡Password🢠\n```{item['password']}```" for item in response.data])
                await canal_aviso.send(f"{cargo_especifico.mention} \n# 🢡SuperUsuário Atualizado🢠\n\n{usuario_formatado}")
            else:
                await canal_aviso.send("A senha foi alterada com sucesso, mas o cargo específico não foi encontrado.")
        else:
            await ctx.send("Senha atualizada com sucesso, mas o canal de aviso não foi encontrado.")
    else:
        await ctx.send(f"Erro ao atualizar a senha: {response}")

@bot.command()
@canal_especifico('qazinho-comandos')
async def CvBottero(ctx):
    response = supabase.table("CvBottero").select("Link, Login, Password").execute()
    usuario_formatado = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n## 🢡Login🢠\n```{item['Login']}```\n## 🢡Password🢠\n```{item['Password']}```" for item in response.data])
    await ctx.send(usuario_formatado)
        
@bot.command()
@canal_especifico('qazinho-comandos')
async def CvToque(ctx):
    response = supabase.table("CvToque").select("Link, Login, Password").execute()
    usuario_formatado = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n## 🢡Login🢠\n```{item['Login']}```\n## 🢡Password🢠\n```{item['Password']}```" for item in response.data])
    await ctx.send(usuario_formatado)

@bot.command()
@canal_especifico('qazinho-comandos')
async def Manual(ctx):
    response = 'https://app.clickup.com/9011563714/v/dc/8cj3362-1771/8cj3362-1791'
    await ctx.send(f'Link: <{response}>')

@bot.command()
@canal_especifico('qazinho-comandos')
async def Plantao(ctx):
    response = supabase.table("Plantoes").select("DataInicio, DataFinal, Responsavel").execute()
    if response.data:
        # Converter as datas para objetos datetime e calcular a diferença em relação ao dia atual
        hoje = datetime.today()
        dados_formatados = [
            {
                "DataInicio": datetime.strptime(item['DataInicio'], '%Y-%m-%d'),
                "DataFinal": datetime.strptime(item['DataFinal'], '%Y-%m-%d'),
                "Responsavel": item['Responsavel']
            }
            for item in response.data
        ]
        # Encontrar a data mais próxima do dia atual
        dados_formatados.sort(key=lambda x: abs((x["DataInicio"] - hoje).days))
        proximo_plantao = dados_formatados[0]

        # Formatar a resposta
        formatted_response = (
            f"**Sexta-Feira: **{proximo_plantao['DataInicio'].strftime('%d/%m/%Y')}\n"
            f"Até\n**Domingo: **{proximo_plantao['DataFinal'].strftime('%d/%m/%Y')}\n"
            f"**Responsável: ** *->{proximo_plantao['Responsavel']}<-*"
        )
    else:
        formatted_response = "Nenhum dado encontrado."

    await ctx.send(formatted_response)
    
bot.run(os.getenv('TOKEN'))