import discord
import os
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
import string
import git
import locale
from babel.dates import format_date
import base64

from Functions.command_error import command_error
from Functions.new_member import new_member
from Functions.decode_data import decode_data
from Functions.canal_especifico import canal_especifico
from Functions.delete_messages import delete_bot_and_command_messages, delete_superusuario
from Functions.get_scripts import get_scripts_type
from Database.database import supabase
from Functions.generate_cpf import generate_cpf

load_dotenv()

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

# Comandos automáticos
@tasks.loop(seconds=20)
async def clear_channel():
    channel = discord.utils.get(bot.get_all_channels(), name='𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
    channelSuperUsuario = discord.utils.get(bot.get_all_channels(), name='𝕾𝖚𝖕𝖊𝖗𝖀𝖘𝖚𝖆𝖗𝖎𝖔🔧') 
    if channel:
        await delete_bot_and_command_messages(channel)
    if channelSuperUsuario:
        await delete_superusuario(channelSuperUsuario, bot)

@bot.event
async def on_member_join(member):
    await new_member(member)

@bot.event
async def on_command_error(ctx, error):
    await command_error(ctx, error)

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
        nova_senha_codificada = base64.b64encode(nova_senha.encode()).decode()
        response = supabase.table("SuperUsuario").update({"password": nova_senha_codificada}).eq("id", 1).execute()
    
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
                    decoded_response = decode_data(response.data)
                    usuario_formatado = "\n\n".join([f"## 🢡Login🢠\n```{item['login']}```\n## 🢡Password🢠\n```{item['password']}```" for item in decoded_response])
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