import discord
from discord.ext import commands
import random
import string
from Functions.generate_cpf import generate_cpf

class CPFView(discord.ui.View):
    def __init__(self, original_user):
        super().__init__(timeout=None)
        self.original_user = original_user

    @discord.ui.button(label="Gerar Novo CPF", style=discord.ButtonStyle.primary)
    async def generate_new_cpf(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_cpf = generate_cpf()
        formatted_cpf = f"{new_cpf[:3]}.{new_cpf[3:6]}.{new_cpf[6:9]}-{new_cpf[9:]}"
        await interaction.response.send_message(content=formatted_cpf, view=self)

    @discord.ui.button(label="Encerrar", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.original_user:
            await interaction.response.send_message("Você não tem permissão para interagir com este botão.", ephemeral=True)
            return
        await interaction.channel.purge(limit=None, check=lambda m: m.author == interaction.client.user)
