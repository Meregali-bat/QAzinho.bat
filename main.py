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
import json
import pandas as pd
import aiohttp
import io

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
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

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

@bot.tree.command(name="anydesk", description='anydesk do computador do suporte')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def anydesk(interaction: discord.Interaction):
    response = supabase.table("AnydeskSuporte").select("Anydesk, Password, Type").execute()
    decoded_response = decode_data(response.data)

    # Deferir a resposta para evitar o tempo limite
    await interaction.response.defer(ephemeral=True)

    for item in decoded_response:
        usuario_formatado = (
            f"## 🢡{item['Type']}🢠\n"
            f"## 🢡Anydesk🢠\n```{item['Anydesk']}```\n"
            f"## 🢡Password🢠\n```{item['Password']}```"
        )
        await interaction.followup.send(usuario_formatado, ephemeral=True)

@bot.tree.command(name="incidente", description='Layout de incidente da API')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Incidente(interaction: discord.Interaction):
    response = supabase.table("IncidenteAPI").select("LayoutIncApi").execute()
    IncidenteFormatado = "\n\n".join([f"```{item['LayoutIncApi']}```" for item in response.data])
    await interaction.response.send_message(IncidenteFormatado, ephemeral=True)

@bot.tree.command(name="incidenteapp", description='Layout de incidente do APP')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def IncidenteApp(interaction: discord.Interaction):
    response = supabase.table("IncidenteAPP").select("LayoutIncApp").execute()
    IncidenteFormatado = "\n\n".join([f"```{item['LayoutIncApp']}```" for item in response.data])
    await interaction.response.send_message(IncidenteFormatado)
    
@bot.tree.command(name="superusuario", description='Login e senha do superusuário')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def SuperUsuario(interaction: discord.Interaction):
    response = supabase.table("SuperUsuario").select("login, password").execute()
    decoded_response = decode_data(response.data)
    if response.data:
        # Formatar a resposta para uma string legível, pulando a coluna ID
        formatted_response = "\n\n".join([f"# 🢡SuperUsuário🢠\n ## 🢡Login🢠\n```{item['login']}```\n## 🢡Senha🢠\n```{item['password']}```" for item in decoded_response])
    else:
        formatted_response = "Nenhum dado encontrado."

    await interaction.response.send_message(formatted_response)
    
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

@bot.tree.command(name="cvbottero", description='Login de adm para o CV Bottero')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def CvBottero(interaction: discord.Interaction):
    response = supabase.table("CvBottero").select("Link, Login, Password").execute()
    decoded_response = decode_data(response.data)
    usuario_formatado = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n## 🢡Login🢠\n```{item['Login']}```\n## 🢡Password🢠\n```{item['Password']}```" for item in decoded_response])
    await interaction.response.send_message(usuario_formatado)

@bot.tree.command(name="cvredecore", description='Login de adm para o CV Redecore')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def CvRedecore(interaction: discord.Interaction):
    response = supabase.table("CvRedecore").select("Link, Login, Password").execute()
    decoded_response = decode_data(response.data)
    usuario_formatado = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n## 🢡Login🢠\n```{item['Login']}```\n## 🢡Password🢠\n```{item['Password']}```" for item in decoded_response])
    await interaction.response.send_message(usuario_formatado)

@bot.tree.command(name="acessomentor", description='Login do Mentor')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def AcessoMentor(interaction: discord.Interaction):
    response = supabase.table("AcessoMentor").select("Link, Login, Password").execute()
    decoded_response = decode_data(response.data)
    usuario_formatado = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n## 🢡Login🢠\n```{item['Login']}```\n## 🢡Password🢠\n```{item['Password']}```" for item in decoded_response])
    await interaction.response.send_message(usuario_formatado)

@bot.tree.command(name="cvtoque", description='Login de adm para o CV Toque')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def CvToque(interaction: discord.Interaction):
    response = supabase.table("CvToque").select("Link, Login, Password").execute()
    decoded_response = decode_data(response.data)
    usuario_formatado = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n## 🢡Login🢠\n```{item['Login']}```\n## 🢡Password🢠\n```{item['Password']}```" for item in decoded_response])
    await interaction.response.send_message(usuario_formatado)

@bot.tree.command(name="manual", description='link para o manual de sobrevivência')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Manual(interaction: discord.Interaction):
    response = supabase.table("Manual").select("Link").execute()
    response_formatada = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n" for item in response.data])
    await interaction.response.send_message(response_formatada)

@bot.tree.command(name="zap4you", description='Login do Zap4You')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Zap4You(interaction: discord.Interaction):
    response = supabase.table("Zap4You").select("Link, Login").execute()
    decoded_user = decode_data(response.data)
    usuario_formatado = "\n\n".join([f"## 🢡Link🢠\n<{item['Link']}>\n## 🢡Login🢠\n```{item['Login']}```" for item in decoded_user])
    await interaction.response.send_message(usuario_formatado)

@bot.tree.command(name="plantao", description='Data e responsável pelo plantão mais próximo')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Plantao(interaction: discord.Interaction):
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

    await interaction.response.send_message(formatted_response)
    
@bot.tree.command(name="plantoesmes", description='Plantões até o final do mês')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def PlantoesMes(interaction: discord.Interaction):
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
        
        dados_formatados.sort(key=lambda x: x['DataInicio'])

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

    await interaction.response.send_message(formatted_response)

@bot.tree.command(name="plantoes", description='Todos os plantões cadastrados até o momento')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Plantoes(interaction: discord.Interaction):
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

        # Ordenar a lista por DataInicio
        dados_formatados.sort(key=lambda x: x['DataInicio'])

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

    await interaction.response.send_message(formatted_response)

@bot.tree.command(name="senha", description='Gera uma senha aleatoria de 10 digitos')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Senha(interaction: discord.Interaction):
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    await interaction.response.send_message(random_string)
    
@bot.tree.command(name="cpf", description='Gera um CPF válido')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def CPF(interaction: discord.Interaction):
    # Gerar um CPF válido
    random_cpf = generate_cpf()
    # Formatar o CPF
    formatted_cpf = f"{random_cpf[:3]}.{random_cpf[3:6]}.{random_cpf[6:9]}-{random_cpf[9:]}"
    
    await interaction.response.send_message(formatted_cpf)

@bot.tree.command(name="snappdv", description='Scripts usados no SnapPdv')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def SnapPdv(interaction: discord.Interaction):
    Type1 = 'SnapPdv'
    scripts = await get_scripts_type(Type1)

    first_response = True
    for script, filename in scripts:
        if filename:
            if os.path.exists(filename):
                try:
                    if first_response:
                        await interaction.response.send_message(file=discord.File(filename))
                        first_response = False
                    else:
                        await interaction.followup.send(file=discord.File(filename))
                finally:
                    os.remove(filename)
        else:
            if first_response:
                await interaction.response.send_message(script)
                first_response = False
            else:
                await interaction.followup.send(script)

@bot.tree.command(name="bancouse", description='Scripts usados no Banco do USE')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def BancoUse(interaction: discord.Interaction):
    Type1 = 'BancoUse'
    scripts = await get_scripts_type(Type1)

    first_response = True
    for script, filename in scripts:
        if filename:
            if os.path.exists(filename):
                try:
                    if first_response:
                        await interaction.response.send_message(file=discord.File(filename))
                        first_response = False
                    else:
                        await interaction.followup.send(file=discord.File(filename))
                finally:
                    os.remove(filename)
        else:
            if first_response:
                await interaction.response.send_message(script)
                first_response = False
            else:
                await interaction.followup.send(script)

@bot.tree.command(name="snapprint", description='Scripts usados no SnapPrint')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def SnapPrint(interaction: discord.Interaction):
    Type1 = 'SnapPrint'
    scripts = await get_scripts_type(Type1)

    first_response = True
    for script, filename in scripts:
        if filename:
            if os.path.exists(filename):
                try:
                    if first_response:
                        await interaction.response.send_message(file=discord.File(filename))
                        first_response = False
                    else:
                        await interaction.followup.send(file=discord.File(filename))
                finally:
                    os.remove(filename)
        else:
            if first_response:
                await interaction.response.send_message(script)
                first_response = False
            else:
                await interaction.followup.send(script)

@bot.tree.command(name="tema", description='Temas do SnapPDV')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Tema(interaction: discord.Interaction):
    Type1 = 'Tema'
    scripts = await get_scripts_type(Type1)

    first_response = True
    for script, filename in scripts:
        if filename:
            if os.path.exists(filename):
                try:
                    if first_response:
                        await interaction.response.send_message(file=discord.File(filename))
                        first_response = False
                    else:
                        await interaction.followup.send(file=discord.File(filename))
                finally:
                    os.remove(filename)
        else:
            if first_response:
                await interaction.response.send_message(script)
                first_response = False
            else:
                await interaction.followup.send(script)

@bot.tree.command(name="lojasbottero", description="mostra uma planilha com as lojas botteros separando por franqueadas ou não")
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def LojasBottero(interaction: discord.Interaction):
    response = supabase.table("LojasBottero").select("*").execute()
    data = response.data
    
    franqueados = [item for item in data if item.get('FRANQUEADO') == True]
    nao_franqueados = [item for item in data if item.get('FRANQUEADO') == False]

    json_data = json.dumps({
        "nao_franqueados": nao_franqueados,
        "franqueados": franqueados
    }, indent=4, ensure_ascii=False)

    with open("lojas_bottero.json", "w", encoding="utf-8") as f:
        f.write(json_data)

    await interaction.response.send_message("Aqui está a lista de lojas Bottero:", file=discord.File("lojas_bottero.json"))

    os.remove("lojas_bottero.json")
    
@bot.tree.command(name="qualita", description='Imagem dos contatos da qualitá')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def Qualita(interaction: discord.Interaction):
    response = supabase.table("Qualita").select("link").execute()
    links = [item['link'] for item in response.data]

    async with aiohttp.ClientSession() as session:
        for link in links:
            async with session.get(link) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    await interaction.response.send_message(file=discord.File(fp=io.BytesIO(data), filename="image.png"))
                else:
                    await interaction.response.send_message(f"Falha ao baixar a imagem: {link}")

@bot.event
async def on_ready():
    clear_channel.start()
    print(f'Bot conectado como {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Sincronizados {len(synced)} comandos')
    except Exception as e:
        print(f'Erro ao sincronizar comandos: {e}')

if current_branch == 'Master':
    TOKEN = bot.run(os.getenv('TOKEN'))
else:
    TOKEN = bot.run(os.getenv('TOKEN_TESTE'))