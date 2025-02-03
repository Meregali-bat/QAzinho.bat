from discord import ButtonStyle
from discord.ui import Button, View
from Database.database import supabase
from Functions.decode_data import decode_data
import discord

type_to_style = {
    "Cv": ButtonStyle.blurple,  # Azul
    "Anydesk": ButtonStyle.red,  # Vermelho
    "Acesso": ButtonStyle.green,  # Verde
    "Manual": ButtonStyle.blurple,  # Azul
    
    # Adicione type1 novos quando precisar
}

type_to_emoji = {
    "Cv": "📱",  # Emoji para Cv
    "Anydesk": "🖥️",  # Emoji para Anydesk
    "Acesso": "🔑",  # Emoji para Acesso
    "Manual": "📚",  # Emoji para Manual

}

type2_to_style = {
    "Snapcontrol": ButtonStyle.blurple,  # Azul,
    "BancoUse": ButtonStyle.red,  # Vermelho
    "Mentor": ButtonStyle.green,  # Verde
    "Zap4You": ButtonStyle.green,
    "Bottero": ButtonStyle.blurple,
    "Redecore": ButtonStyle.blurple,
    "Toque": ButtonStyle.blurple,
    "Clickup": ButtonStyle.blurple,  # Azul,
    # Adicione type2 novos quando precisar
}

type2_to_emoji = {
    "Snapcontrol": "™️",
    "BancoUse": "🪑",
    "Mentor": "🧠",
    "Zap4You": "📨",
    "Bottero": "👢",
    "Redecore": "🏠",
    "Toque": "🏗️",
    "Clickup": "🆙",
    # Adicione type1 novos quando precisar
}

async def delete_previous_messages(interaction: discord.Interaction):
    messages = [message async for message in interaction.channel.history(limit=100)]
    for message in messages:
        if message.author == interaction.client.user and (interaction.message is None or message.id != interaction.message.id):
            await message.delete()


async def show_type1_buttons(interaction: discord.Interaction):
    await delete_previous_messages(interaction)
    select = supabase.table("AcessosInternos").select("*").execute()
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
                selectbasedonType1 = supabase.table("AcessosInternos").select("*").eq("Type1", type1).execute()
                view = View()

                back_button = Button(label="Voltar", style=ButtonStyle.secondary, emoji="↩️")

                async def back_callback(interaction: discord.Interaction):
                    if interaction.user != original_user:
                        await interaction.response.send_message("Você não tem permissão para interagir com este botão.", ephemeral=True)
                        return
                    await show_type1_buttons(interaction)

                async def delete_history(interaction: discord.Interaction):
                    if interaction.user != original_user:
                        await interaction.response.send_message("Você não tem permissão para interagir com este botão.", ephemeral=True)
                        return
                    await interaction.channel.purge(limit=None, check=lambda m: m.author == interaction.client.user)

                back_button.callback = back_callback
                view.add_item(back_button)

                for Type2 in selectbasedonType1.data:
                    type2_value = Type2['Type2']
                    button_style = type2_to_style.get(type2_value, ButtonStyle.gray)
                    button_emoji = type2_to_emoji.get(type2_value, "📓")
                    buttonType2 = Button(label=type2_value, style=button_style, emoji=button_emoji)

                    async def type2_callback(interaction: discord.Interaction, type1=type1, type2=type2_value):
                        if interaction.user != original_user:
                            await interaction.response.send_message("Você não tem permissão para interagir com este botão.", ephemeral=True)
                            return
                        await delete_previous_messages(interaction)
                        response = supabase.table("AcessosInternos").select("Link, Login, Password").eq("Type1", type1).eq("Type2", type2).execute()
                        decoded_user = decode_data(response.data)
                        usuario_formatado = "\n\n".join([
                            "\n".join([
                                f"## 🢡Link🢠\n<{item['Link']}>" if item.get('Link') else "",
                                f"## 🢡Login🢠\n```{item['Login']}```" if item.get('Login') else "",
                                f"## 🢡Password🢠\n```{item.get('Password', 'N/A')}```" if item.get('Password') else ""
                            ]).strip()
                            for item in decoded_user
                        ])
                        view = View()
                        back_button = Button(label="Voltar", style=ButtonStyle.secondary, emoji="↩️")
                        delete_button = Button(label="Encerrar", style=ButtonStyle.danger, emoji="✖️")
                        back_button.callback = back_callback
                        delete_button.callback = delete_history
                        view.add_item(back_button)
                        view.add_item(delete_button)
                        await interaction.response.send_message(usuario_formatado, view=view)

                    buttonType2.callback = type2_callback
                    view.add_item(buttonType2)

                await interaction.response.edit_message(content="Aqui estão os acessos internos:", view=view)

            buttonType1.callback = button_callback
            type1_dict[type1_value] = buttonType1
            view.add_item(buttonType1)

    await interaction.response.send_message("Aqui estão os acessos internos:", view=view)