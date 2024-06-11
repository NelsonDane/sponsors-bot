import discord
from discord import app_commands
from discord.ext import tasks
from config import GUILD_ID, GH_SPONSORS_ROLE_ID, GH_OVERRIDE_ROLE_ID, ROLES_CHANNEL_ID, ROLES_MESSAGE_ID, REQUIRED_ROLES, BOT_TOKEN, GH_REPOS
import emoji

from db import EdgeDB
from gh import update_sponsors, update_contributors
from web import generate_uri

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

def get_roles_from_contributor_repos(contributed_to_repos):
    roles = []
    for repo in contributed_to_repos:
        for gh_repo in GH_REPOS:
            if gh_repo["LINK"] == repo:
                roles.append(gh_repo["REPO_ROLE_ID"]["define"])
    return roles

def get_roles_from_message(roles_message):
    roles_message = roles_message.split("*")[1:]
    roles = []
    for role in roles_message:
        role = role.split("\n")[0]
        role = ''.join(role.split())
        # Emoji name (Channel link)
        role_dict = {
            "emoji": role[0],
            "name": str(role[1:].split("(")[0]).lower(),
            "channel_link": str(role[1:].split("(")[1][:-1])
        }
        roles.append(role_dict)
    print(f"Fetched roles: {roles}")
    return roles

async def roles_message_refresh():
    channel = await client.fetch_channel(int(ROLES_CHANNEL_ID))
    roles_message = await channel.fetch_message(int(ROLES_MESSAGE_ID))
    roles_message_text = roles_message.content
    roles = get_roles_from_message(roles_message_text)
    reactions = roles_message.reactions
    for role in roles:
        await roles_message.add_reaction(role["emoji"])
        print(f"Added reaction {role['emoji']}")
    for reaction in reactions:
        if reaction.emoji not in [role["emoji"] for role in roles]:
            await roles_message.remove_reaction(reaction.emoji, client.user)
            print(f"Removed reaction {reaction.emoji}")
    print("Roles message refreshed")

async def role_message_control(payload, remove_role=False):
    if payload.message_id == int(ROLES_MESSAGE_ID) and payload.user_id != client.user.id:
        channel = await client.fetch_channel(int(ROLES_CHANNEL_ID))
        roles_message = await channel.fetch_message(int(ROLES_MESSAGE_ID))
        roles_message = roles_message.content
        roles = get_roles_from_message(roles_message)
        for role in roles:
            if role["emoji"] == payload.emoji.name:
                if not (is_sponsor(payload.user_id) or is_contributor(payload.user_id)):
                    print(f"{payload.member.display_name} is not a sponsor or contributor")
                    return
                guild = client.get_guild(payload.guild_id)
                server_roles = await guild.fetch_roles()
                server_role = discord.utils.get(server_roles, name=role["name"])
                if server_role:
                    member = await guild.fetch_member(payload.user_id)
                    if remove_role:
                        await member.remove_roles(server_role)
                        print(f"Removed role {server_role.name} from {member.display_name}")
                    else:
                        await member.add_roles(server_role)
                        print(f"Gave role {server_role.name} to {member.display_name}")
                else:
                    print(f"Role {role['name']} not found")

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    @client.event
    async def on_raw_message_edit(payload):
        if payload.channel_id == int(ROLES_CHANNEL_ID) and payload.message_id == int(ROLES_MESSAGE_ID):
            await roles_message_refresh()

    @client.event
    async def on_raw_reaction_add(payload):
        await role_message_control(payload)

    @client.event
    async def on_raw_reaction_remove(payload):
        await role_message_control(payload, remove_role=True)

    @tree.command(
        name="ping",
        description="Ping the bot",
        guild=discord.Object(id=GUILD_ID)
    )
    async def ping_command(interaction: discord.Interaction):
        await interaction.response.send_message("Pong!", ephemeral=True)

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
                await interaction.user.add_roles(discord.Object(id=GH_SPONSORS_ROLE_ID))
                await interaction.response.send_message("Awesome, you are a sponsor! I have given you your roles", ephemeral=True)
                print(f"Gave sponsor role to {discord_display_name}")
            else:
                await interaction.user.remove_roles(discord.Object(id=GH_SPONSORS_ROLE_ID))
                print(f"Removed sponsor role from {discord_display_name}")
            if user.is_contributor:
                roles = get_roles_from_contributor_repos(user.contributed_to_repos)
                for role in roles:
                    await interaction.user.add_roles(discord.Object(id=role))
                await interaction.response.send_message("Thanks, you are a GitHub contributor! I have given you your roles", ephemeral=True)
                print(f"Gave contributor role to {discord_display_name}")
            else:
                roles = (x["REPO_ROLE_ID"] for x in GH_REPOS.values())
                for role in roles:
                    await interaction.user.remove_roles(discord.Object(id=role))
                print(f"Removed contributor role from {discord_display_name}")
        else:
            await interaction.response.send_message("I have created a private thread for you to verify your sponsor/contributor status.", ephemeral=True)
            # Make new private thread
            thread_name = f"{discord_display_name}'s Thread"
            threads = await interaction.channel.threads
            for thread in threads:
                if thread.name == thread_name:
                    user_thread = thread
                    break
                else:
                    user_thread = await interaction.channel.create_thread(name=thread_name, auto_archive_duration=60)
            await user_thread.add_user(interaction.user)
            await user_thread.send(f"Welcome to the server <@{interaction.user.id}>! Let's verify your sponsor/contributor status so you can access your project channel.")
            await user_thread.send(f"Please connect your GitHub account in Discord connections (no need to have it visible on your profile!) Once that is done, please follow this link: {generate_uri()}")
            await user_thread.send("Please run /verify once you have connected your GitHub account.")

    @tasks.loop(hours=1)
    async def update_db_loop():
        update_db()
        print("Database updated")

    @client.event
    async def on_ready():
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Logged in as {client.user}")
        update_db()
        await roles_message_refresh()
        try:
            update_db_loop.start()
        except RuntimeError:
            print("Loop already running")

    # Start stuff
    client.run(BOT_TOKEN)
