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
import aiohttp
import io

from Functions.command_error import command_error
from Functions.new_member import new_member
from Functions.decode_data import decode_data
from Functions.canal_especifico import canal_especifico
from Functions.delete_messages import delete_bot_and_command_messages, delete_superusuario
from Functions.get_scripts import show_scripts_buttons
from Functions.Incidentes import show_incidentes_buttons
from Database.database import supabase
from Functions.generate_cpf import generate_cpf
from Functions.AcessosInternos import show_type1_buttons

load_dotenv()

repo = git.Repo(search_parent_directories=True)
current_branch = repo.active_branch.name

# Create a Discord client instance and set the command prefix
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

#Classes
from Classes.SenhaView import SenhaView
from Classes.CPFView import CPFView

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

@bot.tree.command(name="incidentes", description='Layouts de incidentes')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def incidentes(interaction: discord.Interaction):
    await show_incidentes_buttons(interaction)

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
    view = SenhaView(interaction.user)
    await interaction.response.send_message(random_string, view=view)
    
@bot.tree.command(name="cpf", description='Gera um CPF válido')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def CPF(interaction: discord.Interaction):
    # Gerar um CPF válido
    random_cpf = generate_cpf()
    # Formatar o CPF
    formatted_cpf = f"{random_cpf[:3]}.{random_cpf[3:6]}.{random_cpf[6:9]}-{random_cpf[9:]}"
    
    view = CPFView(interaction.user)
    await interaction.response.send_message(formatted_cpf, view=view)

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

@bot.tree.command(name="scripts", description='Scripts gerais')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def get_scripts(interaction: discord.Interaction):
    await show_scripts_buttons(interaction)

@bot.tree.command(name="acessosinternos", description='Acessos Internos')
@canal_especifico('𝕮𝖔𝖒𝖆𝖓𝖉𝖔𝖘🤖')
async def AcessosInternos(interaction: discord.Interaction):
    await show_type1_buttons(interaction)

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