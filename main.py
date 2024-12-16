import discord
import os
from discord.ext import commands, tasks
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageOps
import aiohttp
import io
from supabase import create_client, Client
from datetime import datetime, timedelta, timezone
from functools import wraps
import asyncio
import random
import string
import git
import locale
from babel.dates import format_date
import base64

load_dotenv()

# Consume supabase database
supabase_url: str = os.getenv('SUPABASE_URL')
supabase_key: str = os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)


repo = git.Repo(search_parent_directories=True)
current_branch = repo.active_branch.name


# Create a Discord client instance and set the command prefix
intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

# Set the confirmation message when the bot is ready
@bot.event
async def on_ready():
    clear_channel.start()
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
                        
async def delete_superusuario(channel):
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
             
def write_to_sql_file(script, filename="script.sql"):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(script)
    return filename
                        
async def get_scripts_type(Type1):
    response = supabase.table('Scripts').select("Type2, Scripts").eq("Type1", Type1).execute()
    if response.data:
        # Formatar a resposta
        formatted_responses = []
        for item in response.data:
            type2 = item['Type2']
            script = item['Scripts']
            formatted_response = f"**{type2}**:\n```sql\n{script}\n```"

            if len(formatted_response) > 2000:
                filename = write_to_sql_file(script)
                formatted_responses.append((None, filename))
            else:
                formatted_responses.append((formatted_response, None))
        
        return formatted_responses
    else:
        return [("Nenhum script encontrado para os tipos fornecidos.", None)]
    

def decode_data(data):
    decoded_data = []
    for item in data:
        decoded_item = {}
        for key, value in item.items():
            if isinstance(value, str):
                try:
                    decoded_value = base64.b64decode(value).decode('utf-8')
                except (base64.binascii.Error, UnicodeDecodeError):
                    decoded_value = value
                decoded_item[key] = decoded_value
            else:
                decoded_item[key] = value
        decoded_data.append(decoded_item)
    return decoded_data

# Comandos automáticos
@tasks.loop(seconds=20)
async def clear_channel():
    channel = discord.utils.get(bot.get_all_channels(), name='𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
    channelSuperUsuario = discord.utils.get(bot.get_all_channels(), name='𝕾𝖚𝖕𝖊𝖗𝖀𝖘𝖚𝖆𝖗𝖎𝖔🔧') 
    if channel:
        await delete_bot_and_command_messages(channel)
    if channelSuperUsuario:
        await delete_superusuario(channelSuperUsuario)

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='ℍ𝕠𝕣𝕒𝔻𝕠ℂ𝕒𝕗𝕖☕')
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
        bg_image = Image.open('./Assets/background2.png')

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
    canal_especifico = '𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖'
    canal_especifico_obj = discord.utils.get(ctx.guild.text_channels, name=canal_especifico)
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Comando não reconhecido. Por favor, use um comando válido. \n\
Utilize !Comandos no canal {canal_especifico_obj.mention} para ver os comandos válidos', delete_after=10)
        await ctx.message.delete()

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        response = '```Os comandos disponíveis são:\n\
!AcessoMentor\n\
!Anydesk\n\
!BancoUse\n\
!CPF\n\
!CvBottero\n\
!CvRedecore\n\
!CvToque\n\
!Incidente\n\
!IncidenteApp\n\
!Manual\n\
!Plantao\n\
!Plantoes\n\
!PlantoesMes\n\
!Senha\n\
!SnapPdv\n\
!SnapPrint\n\
!SuperUsuario\n\
!Tema```'
        await message.channel.send(response)
    
    # Processar outros comandos normalmente
    await bot.process_commands(message)

#Comandos manuais
@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Anydesk(ctx):
    response = supabase.table("AnydeskSuporte").select("Anydesk, Password").execute()
    decoded_response = decode_data(response.data)
    usuario_formatado = "\n\n".join([
        f"## 🢡Anydesk🢠\n```{item['Anydesk']}```\n## 🢡Password🢠\n```{item['Password']}```"
        for item in decoded_response
    ])
    await ctx.send(usuario_formatado)

    

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Incidente(ctx):
    response = supabase.table("IncidenteAPI").select("LayoutIncApi").execute()
    IncidenteFormatado = "\n\n".join([f"```{item['LayoutIncApi']}```" for item in response.data])
    await ctx.send(IncidenteFormatado)

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def IncidenteApp(ctx):
    response = supabase.table("IncidenteAPP").select("LayoutIncApp").execute()
    IncidenteFormatado = "\n\n".join([f"```{item['LayoutIncApp']}```" for item in response.data])
    await ctx.send(IncidenteFormatado)
    
@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def SuperUsuario(ctx):
    response = supabase.table("SuperUsuario").select("login, password").execute()
    decoded_response = decode_data(response.data)
    if response.data:
        # Formatar a resposta para uma string legível, pulando a coluna ID
        formatted_response = "\n\n".join([f"# 🢡SuperUsuário🢠\n ## 🢡Login🢠\n```{item['login']}```\n## 🢡Senha🢠\n```{item['password']}```" for item in decoded_response])
    else:
        formatted_response = "Nenhum dado encontrado."

    await ctx.send(formatted_response)
    
@bot.command()
async def UpdateHash(ctx, nova_senha: str):
    canal_especifico = 'adm'
    canal_especifico_obj = discord.utils.get(ctx.guild.text_channels, name=canal_especifico)
    if ctx.channel.name != canal_especifico:
        await ctx.send(f'Este comando só deve ser utilizado no canal: {canal_especifico_obj.mention}.',delete_after=5)
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
        canal_aviso = discord.utils.get(ctx.guild.text_channels, name='𝕾𝖚𝖕𝖊𝖗𝖀𝖘𝖚𝖆𝖗𝖎𝖔🔧')
        
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
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def CvBottero(ctx):
    response = supabase.table("CvBottero").select("Link, Login, Password").execute()
    decoded_response = decode_data(response.data)
    usuario_formatado = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n## 🢡Login🢠\n```{item['Login']}```\n## 🢡Password🢠\n```{item['Password']}```" for item in decoded_response])
    await ctx.send(usuario_formatado)

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def CvRedecore(ctx):
    response = supabase.table("CvRedecore").select("Link, Login, Password").execute()
    decoded_response = decode_data(response.data)
    usuario_formatado = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n## 🢡Login🢠\n```{item['Login']}```\n## 🢡Password🢠\n```{item['Password']}```" for item in decoded_response])
    await ctx.send(usuario_formatado)

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def AcessoMentor(ctx):
    response = supabase.table("AcessoMentor").select("Link, Login, Password").execute()
    decoded_response = decode_data(response.data)
    usuario_formatado = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n## 🢡Login🢠\n```{item['Login']}```\n## 🢡Password🢠\n```{item['Password']}```" for item in decoded_response])
    await ctx.send(usuario_formatado)

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def CvToque(ctx):
    response = supabase.table("CvToque").select("Link, Login, Password").execute()
    decoded_response = decode_data(response.data)
    usuario_formatado = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n## 🢡Login🢠\n```{item['Login']}```\n## 🢡Password🢠\n```{item['Password']}```" for item in decoded_response])
    await ctx.send(usuario_formatado)

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Manual(ctx):
    response = supabase.table("Manual").select("Link").execute()
    reponse_formatada = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n" for item in response.data])
    await ctx.send(reponse_formatada)

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Zap4You(ctx):
    response = supabase.table("Zap4You").select("Link, Login").execute()
    usuario_formatado = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n## 🢡Login🢠\n```{item['Login']}```" for item in response.data])
    await ctx.send(usuario_formatado)

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
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
    

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def PlantoesMes(ctx):
    response = supabase.table("Plantoes").select("DataInicio, DataFinal, Responsavel").execute()
    if response.data:
        
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        
        # Converter as datas para objetos datetime e calcular a diferença em relação ao dia atual
        hoje = datetime.today()
        ultimo_dia_mes = datetime(hoje.year, hoje.month, 1) + timedelta(days=32)
        ultimo_dia_mes = ultimo_dia_mes.replace(day=1) - timedelta(days=1)
        
        dados_formatados = [
            {
                "DataInicio": datetime.strptime(item['DataInicio'], '%Y-%m-%d'),
                "DataFinal": datetime.strptime(item['DataFinal'], '%Y-%m-%d'),
                "Responsavel": item['Responsavel']
            }
            for item in response.data
            if datetime.strptime(item['DataFinal'], '%Y-%m-%d') <= ultimo_dia_mes
        ]

        if dados_formatados:
            # Formatar a resposta
            formatted_response = "\n\n".join([
                f"**Início: **{format_date(item['DataInicio'], format='full', locale='pt_BR')}\n"
                f"**Fim: **{format_date(item['DataFinal'], format='full', locale='pt_BR')}\n"
                f"**Responsável: ** *->{item['Responsavel']}<-*"
                for item in dados_formatados
            ])
        else:
            formatted_response = "Nenhum plantão encontrado até o final do mês."
    else:
        formatted_response = "Nenhum dado encontrado."

    await ctx.send(formatted_response)

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Plantoes(ctx):
    response = supabase.table("Plantoes").select("DataInicio, DataFinal, Responsavel").execute()
    if response.data:
        
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        
        # Converter as datas para objetos datetime e calcular a diferença em relação ao dia atual
        hoje = datetime.today()
        
        dados_formatados = [
            {
                "DataInicio": datetime.strptime(item['DataInicio'], '%Y-%m-%d'),
                "DataFinal": datetime.strptime(item['DataFinal'], '%Y-%m-%d'),
                "Responsavel": item['Responsavel']
            }
            for item in response.data
            if datetime.strptime(item['DataFinal'], '%Y-%m-%d') >= hoje
        ]

        if dados_formatados:
            # Formatar a resposta
            formatted_response = "\n\n".join([
                f"**Início: **{format_date(item['DataInicio'], format='full', locale='pt_BR')}\n"
                f"**Fim: **{format_date(item['DataFinal'], format='full', locale='pt_BR')}\n"
                f"**Responsável: ** *->{item['Responsavel']}<-*"
                for item in dados_formatados
            ])
        else:
            formatted_response = "Nenhum plantão encontrado até o final do mês."
    else:
        formatted_response = "Nenhum dado encontrado."

    await ctx.send(formatted_response)    

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Senha(ctx):
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    await ctx.send(random_string)
    
@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def CPF(ctx):
    def generate_cpf():
        # Gerar os primeiros 9 dígitos aleatórios
        cpf = [random.randint(0, 9) for _ in range(9)]

        # Calcular o primeiro dígito verificador
        sum1 = sum((cpf[i] * (10 - i) for i in range(9)))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
        cpf.append(digit1)

        # Calcular o segundo dígito verificador
        sum2 = sum((cpf[i] * (11 - i) for i in range(10)))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
        cpf.append(digit2)

        return ''.join(map(str, cpf))

    # Gerar um CPF válido
    random_cpf = generate_cpf()
    
    # Formatar o CPF
    formatted_cpf = f"{random_cpf[:3]}.{random_cpf[3:6]}.{random_cpf[6:9]}-{random_cpf[9:]}"
    
    await ctx.send(formatted_cpf)

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def SnapPdv(ctx):
    Type1 = 'SnapPdv'
    scripts = await get_scripts_type(Type1)

    for script, filename in scripts:
        if filename:
            if os.path.exists(filename):
                try:
                    await ctx.send(file=discord.File(filename))
                finally:
                    os.remove(filename)
        else:
            await ctx.send(script)

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def BancoUse(ctx):
    Type1 = 'BancoUse'
    scripts = await get_scripts_type(Type1)

    for script, filename in scripts:
        if filename:
            if os.path.exists(filename):
                try:
                    await ctx.send(file=discord.File(filename))
                finally:
                    os.remove(filename)
        else:
            await ctx.send(script)

@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def SnapPrint(ctx):
    Type1 = 'SnapPrint'
    scripts = await get_scripts_type(Type1)

    for script, filename in scripts:
        if filename:
            if os.path.exists(filename):
                try:
                    await ctx.send(file=discord.File(filename))
                finally:
                    os.remove(filename)
        else:
            await ctx.send(script)

    
@bot.command()
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Tema(ctx):
    Type1 = 'Tema'
    scripts = await get_scripts_type(Type1)

    for script, filename in scripts:
        if filename:
            if os.path.exists(filename):
                try:
                    await ctx.send(file=discord.File(filename))
                finally:
                    os.remove(filename)
        else:
            await ctx.send(script)

        
if current_branch == 'Master':
    TOKEN = bot.run(os.getenv('TOKEN'))
else:
    TOKEN = bot.run(os.getenv('TOKEN_TESTE'))