import discord
from discord.ext import commands
import random
import string

class SenhaView(discord.ui.View):
    def __init__(self, original_user):
        super().__init__(timeout=None)
        self.original_user = original_user

    @discord.ui.button(label="Gerar Nova Senha", style=discord.ButtonStyle.primary)
    async def generate_new_password(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        await interaction.response.edit_message(content=new_password, view=self)

    @discord.ui.button(label="Encerrar", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.original_user:
            await interaction.response.send_message("Você não tem permissão para interagir com este botão.", ephemeral=True)
            return
        await interaction.message.delete()