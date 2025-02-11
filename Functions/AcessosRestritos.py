from discord import ButtonStyle
from discord.ui import Button, View
from Database.database import supabase
from Functions.decode_data import decode_data
import discord

type_to_style = {
    "GitHub": ButtonStyle.blurple,  # Azul
}

type_to_emoji = {
    "GitHub": "🐙", 
}

async def delete_previous_messages(interaction: discord.Interaction):
    messages = [message async for message in interaction.channel.history(limit=100)]
    for message in messages:
        if message.author == interaction.client.user and (interaction.message is None or message.id != interaction.message.id):
            await message.delete()

async def show_type1_buttonsRestrito(interaction: discord.Interaction):
    # Verificação de cargo
    required_role_name = "HEAD-CX"  
    user_roles = [role.name for role in interaction.user.roles]
    if required_role_name not in user_roles:
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
        return

    await delete_previous_messages(interaction)
    select = supabase.table("AcessosRestritos").select("*").execute()
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
                response = supabase.table("AcessosRestritos").select("Link, Login, Password").eq("Type1", type1).execute()
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

                async def back_callback(interaction: discord.Interaction):
                    if interaction.user != original_user:
                        await interaction.response.send_message("Você não tem permissão para interagir com este botão.", ephemeral=True)
                        return
                    await show_type1_buttonsRestrito(interaction)

                back_button.callback = back_callback

                view.add_item(back_button)
                await interaction.response.send_message(usuario_formatado, view=view, ephemeral=True)

            buttonType1.callback = button_callback
            type1_dict[type1_value] = buttonType1
            view.add_item(buttonType1)

    await interaction.response.send_message("Aqui estão os acessos internos:", view=view, ephemeral=True)