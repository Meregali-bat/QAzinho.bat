from discord import ButtonStyle
from discord.ui import Button, View
from Functions.make_archives import write_to_sql_file
from Database.database import supabase
import discord

type_to_style = {
    "SnapPdv": ButtonStyle.blurple,
    "BancoUse": ButtonStyle.green,
    "Tema": ButtonStyle.blurple,
    "SnapPrint": ButtonStyle.red,
    "CV": ButtonStyle.red,
    # Adicione mais mapeamentos conforme necessário
}

type_to_emoji = {
    "SnapPdv": "🛒",
    "BancoUse": "🪑",
    "Tema": "🖼️",
    "SnapPrint": "🖨️",
    "CV": "🛍️",  
    # Adicione mais mapeamentos conforme necessário
}

type2_to_style = {
    "Vendas": ButtonStyle.blurple,
    "ValeGas": ButtonStyle.red,
    "F360": ButtonStyle.green,
    "Campanhas": ButtonStyle.green,
    "NFCe": ButtonStyle.red,
    "XML": ButtonStyle.red,
    "TemaBottero": ButtonStyle.red,
    "TemaMercado": ButtonStyle.blurple,
    "Consulta": ButtonStyle.blurple,
    "Correcoes": ButtonStyle.green,
    "CV": ButtonStyle.red,
    # Adicione mais mapeamentos conforme necessário
}

type2_to_emoji = {
    "Vendas": "🛍️",
    "ValeGas": "☢️",
    "F360": "🖥️",
    "Campanhas": "💰",
    "NFCe": "📃",
    "XML": "📁",
    "TemaBottero": "👢",
    "TemaMercado": "🛒",
    "Consulta": "🔎",
    "Correcoes": "📝",
    "CV": "🛍️",  
    # Adicione mais mapeamentos conforme necessário
}

async def delete_previous_messages(interaction: discord.Interaction):
    messages = [message async for message in interaction.channel.history(limit=100)]
    for message in messages:
        if message.author == interaction.client.user and (interaction.message is None or message.id != interaction.message.id):
            await message.delete()

async def show_scripts_buttons(interaction: discord.Interaction):
    await delete_previous_messages(interaction)
    select = supabase.table("Scripts").select("*").execute()
    view = View()
    type1_dict = {}
    original_user = interaction.user

    for Type1 in select.data:
        type1_value = Type1['Type1']
        if type1_value not in type1_dict:
            button_style = type_to_style.get(type1_value, ButtonStyle.gray)
            button_emoji = type_to_emoji.get(type1_value, "📓")
            buttonType1 = Button(label=type1_value, style=button_style, emoji=button_emoji)

            async def button_callback(interaction: discord.Interaction, type1=type1_value):
                if interaction.user != original_user:
                    await interaction.response.send_message("Você não tem permissão para interagir com este botão.", ephemeral=True)
                    return
                await delete_previous_messages(interaction)
                selectbasedonType1 = supabase.table("Scripts").select("*").eq("Type1", type1).execute()
                view = View()

                back_button = Button(label="Voltar", style=ButtonStyle.secondary, emoji="↩️")

                async def back_callback(interaction: discord.Interaction):
                    if interaction.user != original_user:
                        await interaction.response.send_message("Você não tem permissão para interagir com este botão.", ephemeral=True)
                        return
                    await show_scripts_buttons(interaction)

                async def delete_history(interaction: discord.Interaction):
                    if interaction.user != original_user:
                        await interaction.response.send_message("Você não tem permissão para interagir com este botão.", ephemeral=True)
                        return
                    await interaction.channel.purge(limit=None, check=lambda m: m.author == interaction.client.user)

                back_button.callback = back_callback
                view.add_item(back_button)

                type2_dict = {}
                for Type2 in selectbasedonType1.data:
                    type2_value = Type2['Type2']
                    if type2_value not in type2_dict:
                        type2_dict[type2_value] = []
                    type2_dict[type2_value].append(Type2['Scripts'])

                for type2_value, scripts in type2_dict.items():
                    button_style = type2_to_style.get(type2_value, ButtonStyle.gray)
                    button_emoji = type2_to_emoji.get(type2_value, "📓")
                    buttonType2 = Button(label=type2_value, style=button_style, emoji=button_emoji)

                    async def type2_callback(interaction: discord.Interaction, type1=type1, type2=type2_value, scripts=scripts):
                        if interaction.user != original_user:
                            await interaction.response.send_message("Você não tem permissão para interagir com este botão.", ephemeral=True)
                            return
                        await delete_previous_messages(interaction)
                        first_message = True
                        for script in scripts:
                            formatted_script = f"\n```sql\n{script}\n```"
                            if len(formatted_script) > 2000:
                                filename = write_to_sql_file(formatted_script)
                                if first_message:
                                    await interaction.response.send_message(file=discord.File(filename))
                                    first_message = False
                                else:
                                    await interaction.followup.send(file=discord.File(filename))
                            else:
                                if first_message:
                                    await interaction.response.send_message(formatted_script)
                                    first_message = False
                                else:
                                    await interaction.followup.send(formatted_script)

                        view = View()
                        back_button = Button(label="Voltar", style=ButtonStyle.secondary, emoji="↩️")
                        delete_button = Button(label="Encerrar", style=ButtonStyle.danger, emoji="✖️")
                        back_button.callback = back_callback
                        delete_button.callback = delete_history
                        view.add_item(back_button)
                        view.add_item(delete_button)
                        await interaction.followup.send("Scripts enviados.", view=view)

                    buttonType2.callback = type2_callback
                    view.add_item(buttonType2)

                await interaction.response.edit_message(content="Aqui estão os scripts:", view=view)

            buttonType1.callback = button_callback
            type1_dict[type1_value] = buttonType1
            view.add_item(buttonType1)

    await interaction.response.send_message("Aqui estão os scripts:", view=view)