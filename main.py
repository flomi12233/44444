import discord
from discord.ext import commands
from discord import app_commands, Interaction, ui
import os

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
MOD_CHANNEL_ID = int(os.getenv("MOD_CHANNEL_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

class VerifyForm(ui.Modal, title="Void-Verify | Форма верификации"):

    age = ui.TextInput(label="Сколько вам лет?", placeholder="Например: 18", required=True)
    nickname = ui.TextInput(label="Ваш ник", placeholder="Например: DarkWolf", required=True)
    realname = ui.TextInput(label="Ваше имя", placeholder="Например: Иван", required=True)
    rules = ui.TextInput(label="Вы знаете правила? (да/нет)", placeholder="да или нет", required=True)

    async def on_submit(self, interaction: Interaction):
        embed = discord.Embed(
            title="📩 Void-Verify | Новая заявка на верификацию",
            color=discord.Color.purple()
        )
        embed.add_field(name="Возраст", value=self.age.value, inline=False)
        embed.add_field(name="Ник", value=self.nickname.value, inline=False)
        embed.add_field(name="Имя", value=self.realname.value, inline=False)
        embed.add_field(name="Знает правила", value=self.rules.value, inline=False)
        embed.set_footer(text=f"Заявка от {interaction.user} • Void-Verify")

        view = ModerationButtons(interaction.user)

        mod_channel = bot.get_channel(MOD_CHANNEL_ID)
        if mod_channel:
            await mod_channel.send(embed=embed, view=view)
            await interaction.response.send_message("✅ Ваша заявка отправлена на рассмотрение модераторам.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Ошибка: модераторский канал не найден.", ephemeral=True)

class ModerationButtons(ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    @ui.button(label="✅ Принять", style=discord.ButtonStyle.success)
    async def accept(self, interaction: Interaction, button: ui.Button):
        guild = interaction.guild
        role = guild.get_role(ROLE_ID)
        member = guild.get_member(self.user.id)

        if not role:
            await interaction.response.send_message("❌ Роль не найдена.", ephemeral=True)
            return

        if not member:
            await interaction.response.send_message("❌ Пользователь не найден на сервере.", ephemeral=True)
            return

        try:
            await member.add_roles(role)
            await interaction.response.send_message(
                f"✅ {self.user.mention} был верифицирован и получил роль **{role.name}**.",
                ephemeral=False
            )
        except discord.Forbidden:
            await interaction.response.send_message("❌ У бота нет прав выдать эту роль.", ephemeral=True)

    @ui.button(label="❌ Отклонить", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_message(
            f"❌ {self.user.mention}, ваша заявка была отклонена модератором {interaction.user.mention}.",
            ephemeral=False
        )

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    await bot.change_presence(
        activity=discord.Game(name="ожидает заявки... | /verify"),
        status=discord.Status.online
    )
    print(f"Void-Verify запущен как {bot.user}!")

@bot.tree.command(name="verify", description="Пройти верификацию", guild=discord.Object(id=GUILD_ID))
async def verify_command(interaction: Interaction):
    await interaction.response.send_modal(VerifyForm())

bot.run(TOKEN)
