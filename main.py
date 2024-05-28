import discord
from discord import app_commands
from dotenv import load_dotenv
import os
import emoji

from db import EdgeDB
from gh import update_sponsors, update_contributors
from web import generate_uri


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
SPONSOR_ROLE_ID = os.getenv("SPONSOR_ROLE_ID")
CONTRIBUTOR_ROLE_ID = os.getenv("CONTRIBUTOR_ROLE_ID")
ROLES_CHANNEL_ID = os.getenv("ROLES_CHANNEL_ID")
ROLES_MESSAGE_ID = os.getenv("ROLES_MESSAGE_ID")

EMOJIS = emoji.EMOJI_DATA

def update_db():
    db = EdgeDB()
    update_sponsors(db)
    update_contributors(db)    

def is_sponsor(user_id):
    db = EdgeDB()
    user = db.get_sponsor_by_discord_id(user_id)
    return user and user.is_currently_sponsoring

def is_contributor(user_id):
    db = EdgeDB()
    user = db.get_sponsor_by_discord_id(user_id)
    return user and user.is_contributor

def build_roles(roles_message):
    roles_message = roles_message.split("*")[1:]
    roles = []
    for role in roles_message:
        role = role.split("\n")[0]
        role = ''.join(role.split())
        role_dict = {
            "emoji": role[0],
            "name": str(role[1:]).lower()
        }
        roles.append(role_dict)
    print(f"Fetched roles: {roles}")
    return roles

if __name__ == "__main__":
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    @client.event
    async def on_raw_reaction_add(payload):
        if payload.message_id == int(ROLES_MESSAGE_ID):
            channel = await client.fetch_channel(int(ROLES_CHANNEL_ID))
            roles_message = await channel.fetch_message(int(ROLES_MESSAGE_ID))
            roles_message = roles_message.content
            roles = build_roles(roles_message)
            for role in roles:
                if role["emoji"] == payload.emoji.name:
                    if not (is_sponsor(payload.user_id) or is_contributor(payload.user_id)):
                        print(f"{payload.member.display_name} is not a sponsor or contributor")
                        return
                    guild = client.get_guild(payload.guild_id)
                    server_roles = await guild.fetch_roles()
                    role = discord.utils.get(server_roles, name=role["name"])
                    if role:
                        member = await guild.fetch_member(payload.user_id)
                        await member.add_roles(role)
                        print(f"Gave role {role.name} to {member.display_name}")
                    else:
                        print(f"Role {role['name']} not found")

    @client.event
    async def on_raw_reaction_remove(payload):
        if payload.message_id == int(ROLES_MESSAGE_ID):
            channel = await client.fetch_channel(int(ROLES_CHANNEL_ID))
            roles_message = await channel.fetch_message(int(ROLES_MESSAGE_ID))
            roles_message = roles_message.content
            roles = build_roles(roles_message)
            for role in roles:
                if role["emoji"] == payload.emoji.name:
                    if not (is_sponsor(payload.user_id) or is_contributor(payload.user_id)):
                        print(f"{payload.member.display_name} is not a sponsor or contributor")
                        return
                    guild = client.get_guild(payload.guild_id)
                    server_roles = await guild.fetch_roles()
                    role = discord.utils.get(server_roles, name=role["name"])
                    if role:
                        member = await guild.fetch_member(payload.user_id)
                        await member.remove_roles(role)
                        print(f"Removed role {role.name} from {member.display_name}")
                    else:
                        print(f"Role {role['name']} not found")

    @tree.command(
        name="verify",
        description="Verify your sponsor/contributor status",
        guild=discord.Object(id=GUILD_ID)
    )
    async def verify_command(interaction: discord.Interaction):
        update_db()
        db = EdgeDB()
        user = db.get_sponsor_by_discord_id(interaction.user.id)
        discord_display_name = interaction.user.display_name
        if user:
            if user.is_currently_sponsoring:
                await interaction.user.add_roles(discord.Object(id=SPONSOR_ROLE_ID))
                await interaction.response.send_message("You are a sponsor!", ephemeral=True)
                print(f"Gave sponsor role to {discord_display_name}")
            else:
                await interaction.user.remove_roles(discord.Object(id=SPONSOR_ROLE_ID))
                print(f"Removed sponsor role from {discord_display_name}")
            if user.is_contributor:
                await interaction.user.add_roles(discord.Object(id=CONTRIBUTOR_ROLE_ID))
                await interaction.response.send_message("You are a contributor!", ephemeral=True)
                print(f"Gave contributor role to {discord_display_name}")
            else:
                await interaction.user.remove_roles(discord.Object(id=CONTRIBUTOR_ROLE_ID))
                print(f"Removed contributor role from {discord_display_name}")
        else:
            # Make new private thread
            thread = await interaction.channel.create_thread(name=f"{discord_display_name}'s Thread", auto_archive_duration=10)
            await thread.add_user(interaction.user)
            await thread.send(f"Welcome to the server <@{interaction.user.id}>! Let's verify your sponsor/contributor status so you can access your project channel.")
            await thread.send(f"Please connect your GitHub account in Discord connections (no need to have it visible on your profile!) Once that is done, please follow this link: {generate_uri()}")
            await interaction.response.send_message("I have created a private thread for you to verify your sponsor/contributor status.", ephemeral=True)
            await thread.send("Please run /verify once you have connected your GitHub account.")

    @client.event
    async def on_ready():
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Logged in as {client.user}")
        update_db()

    # Start stuff
    client.run(TOKEN)