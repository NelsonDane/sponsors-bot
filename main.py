import discord
from discord import app_commands
from dotenv import load_dotenv
import os

from db import EdgeDB
from gh import update_sponsors, update_contributors
from web import generate_uri

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

def update_db():
    db = EdgeDB()
    update_sponsors(db)
    update_contributors(db)    

if __name__ == "__main__":
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    @tree.command(
        name="test",
        description="Test command",
        guild=discord.Object(id=GUILD_ID)
    )
    async def test_command(interaction: discord.Interaction):
        update_db()
        db = EdgeDB()
        if db.get_sponsor_by_discord_id(interaction.user.id):
            await interaction.response.send_message("You are a sponsor!", ephemeral=True)
        else:
            # Make new private thread
            thread = await interaction.channel.create_thread(name=f"{interaction.user.display_name}'s Thread", auto_archive_duration=60)
            await thread.add_user(interaction.user)
            await thread.send(f"Welcome to the server <@{interaction.user.id}>! Let's verify your sponsor/contributor status so you can access your project channel.")
            await thread.send(f"Please connect your GitHub account in Discord connections (no need to have it visible on your profile!) Once that is done, please follow this link: {generate_uri()}")

    @client.event
    async def on_ready():
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Logged in as {client.user}")

    # Start stuff
    client.run(TOKEN)
