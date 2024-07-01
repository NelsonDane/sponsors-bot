import discord
from discord import app_commands
from discord.ext import tasks
from config import GUILD_ID, GH_SPONSORS_ROLE_ID, BOT_TOKEN, GH_REPOS, GH_SPONSORS_URL, DISCORD_ROLES_LIST
import emoji

from db import EdgeDB
from gh import update_sponsors, update_contributors
from web import generate_uri

EMOJIS = emoji.EMOJI_DATA

def update_db():
    db = EdgeDB()
    update_sponsors(db)
    update_contributors(db)

def get_roles_from_contributor_repos(contributed_to_repos):
    # Get roles from the repos the user has contributed to
    roles = []
    for repo in contributed_to_repos:
        for gh_repo in GH_REPOS:
            if gh_repo["LINK"] == repo:
                roles.append(gh_repo["REPO_ROLE_ID"]["define"])
    return roles

def get_roles_from_message(roles_message):
    # Get roles from the roles message
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
    return roles

def get_required_roles_from_message(roles_message_id):
    # Get required roles for the message
    for DISCORD_ROLES in DISCORD_ROLES_LIST:
        if int(DISCORD_ROLES["ROLES_MESSAGE_ID"]) == roles_message_id:
            required_roles = DISCORD_ROLES["REQUIRED_ROLES"]
    return required_roles

async def roles_message_refresh():
    # Make sure all roles are added to the roles message so users can react to them
    for DISCORD_ROLES in DISCORD_ROLES_LIST:
        channel = await client.fetch_channel(int(DISCORD_ROLES["ROLES_CHANNEL_ID"]))
        roles_message = await channel.fetch_message(int(DISCORD_ROLES["ROLES_MESSAGE_ID"]))
        roles = get_roles_from_message(roles_message.content)
        for role in roles:
            await roles_message.add_reaction(role["emoji"])
        for reaction in roles_message.reactions:
            if reaction.emoji not in [role["emoji"] for role in roles]:
                await roles_message.remove_reaction(reaction.emoji, client.user)
    print("Roles message refreshed")

async def send_temp_message(channel_id, message, time=60):
    # Send a temporary message to a channel
    channel = await client.fetch_channel(channel_id)
    temp_message = await channel.send(message)
    await temp_message.delete(delay=time)

async def role_message_control(payload, remove_role=False):
    # Add/remove roles based on reactions and required roles
    message_ids = [int(DISCORD_ROLES["ROLES_MESSAGE_ID"]) for DISCORD_ROLES in DISCORD_ROLES_LIST]
    if payload.message_id in message_ids and payload.user_id != client.user.id:
        required_roles = get_required_roles_from_message(payload.message_id)
        channel = await client.fetch_channel(payload.channel_id)
        roles_message = await channel.fetch_message(int(payload.message_id))
        roles = get_roles_from_message(roles_message.content)
        if payload.emoji.name in [role["emoji"] for role in roles]:
            role = [x for x in roles if x["emoji"] == payload.emoji.name][0]
            guild = client.get_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)
            member_role_ids = [role.id for role in member.roles]
            if not remove_role:
                intersection = set(member_role_ids).intersection(set(required_roles))
                if not intersection:
                    await send_temp_message(payload.channel_id, f"{member.mention}: You do not have the required roles to get the {role['name']} role. Please run /verify")
                    await roles_message.remove_reaction(payload.emoji, member)
                    remove_role = True
            server_roles = await guild.fetch_roles()
            server_role = discord.utils.get(server_roles, name=role["name"])
            if server_role:
                if remove_role:
                    await member.remove_roles(server_role)
                    print(f"Removed role {server_role.name} from {member.display_name}")
                else:
                    await member.add_roles(server_role)
                    print(f"Gave role {server_role.name} to {member.display_name}")
                    # Send welcome message
                    welcome_channel_id = int(role["channel_link"].split("/")[-1])
                    welcome_channel = await client.fetch_channel(welcome_channel_id)
                    await send_temp_message(welcome_channel_id, f"Welcome to the channel, {member.mention}!")

async def give_old_reaction_roles():
    # Give roles to users who have reacted to the roles message while the bot was offline
    for DISCORD_ROLES in DISCORD_ROLES_LIST:
        channel = await client.fetch_channel(int(DISCORD_ROLES["ROLES_CHANNEL_ID"]))
        roles_message = await channel.fetch_message(int(DISCORD_ROLES["ROLES_MESSAGE_ID"]))
        roles_dict = get_roles_from_message(roles_message.content)
        for reaction in roles_message.reactions:
            reaction_users = [user async for user in reaction.users()]
            if client.user in reaction_users:
                for user in reaction_users:
                    if user != client.user:
                        fetched_user = await client.fetch_user(user.id)
                        member = await client.get_guild(GUILD_ID).fetch_member(fetched_user.id)
                        user_roles = [role.id for role in member.roles]
                        for role_item in roles_dict:
                            if role_item["emoji"] == reaction.emoji:
                                role_in_question = role_item["name"]
                                role_in_question = discord.utils.get(member.guild.roles, name=role_in_question)
                        intersection = set(user_roles).intersection(set(DISCORD_ROLES["REQUIRED_ROLES"]))
                        if intersection:
                            await member.add_roles(role_in_question)
                        else:
                            print(f"{member.display_name} does not have required roles for {role_in_question}. Removing role.")
                            await member.remove_roles(role_in_question)
                            await reaction.remove(member)
    print("Old reactions updated")

async def update_sponsors_and_contributors():
    # Update sponsors and contributors from DB
    db = EdgeDB()
    users = [member async for member in client.get_guild(GUILD_ID).fetch_members()]
    for user in users:
        sponsor_remove = True
        contributor_remove = True
        found = db.get_sponsor_by_discord_id(user.id)
        if found:
            if found.is_currently_sponsoring:
                sponsor_remove = False
            if found.is_contributor:
                contributor_remove = False
        user_roles = [role.id for role in user.roles]
        if sponsor_remove:
            if GH_SPONSORS_ROLE_ID in user_roles:
                # Remove sponsor role
                await user.remove_roles(discord.Object(id=GH_SPONSORS_ROLE_ID))
                print(f"Removed sponsor role from {user.display_name}")
        else:
            if GH_SPONSORS_ROLE_ID not in user_roles:
                # Add sponsor role
                await user.add_roles(discord.Object(id=GH_SPONSORS_ROLE_ID))
                print(f"Gave sponsor role to {user.display_name}")
        if contributor_remove:
            # Remove all contributor roles
            roles = (x["REPO_ROLE_ID"]["define"] for x in GH_REPOS)
            for role in roles:
                if role in user_roles:
                    await user.remove_roles(discord.Object(id=role))
                    print(f"Removed roles from {user.display_name}")
        else:
            # Add contributor roles
            roles = get_roles_from_contributor_repos(found.contributed_to_repos)
            for role in roles:
                if role not in user_roles:
                    await user.add_roles(discord.Object(id=role))
                    print(f"Gave contributor role to {user.display_name}")
    print("Sponsors and contributors updated")
    await give_old_reaction_roles()

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    intents.members = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    @client.event
    async def on_raw_message_edit(payload):
        message_ids = [int(DISCORD_ROLES["ROLES_MESSAGE_ID"]) for DISCORD_ROLES in DISCORD_ROLES_LIST]
        if payload.message_id in message_ids:
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
        channel_ids = [int(DISCORD_ROLES["ROLES_CHANNEL_ID"]) for DISCORD_ROLES in DISCORD_ROLES_LIST]
        if interaction.channel_id not in channel_ids:
            await interaction.response.send_message("This command cannot be used in this channel.", ephemeral=True)
            return
        await interaction.response.send_message("Starting the verification...", ephemeral=True)
        update_db()
        db = EdgeDB()
        user = db.get_sponsor_by_discord_id(interaction.user.id)
        discord_display_name = interaction.user.display_name
        if user:
            await interaction.followup.send("You were found, checking your status...", ephemeral=True)
            if user.is_currently_sponsoring:
                await interaction.user.add_roles(discord.Object(id=GH_SPONSORS_ROLE_ID))
                await interaction.followup.send("Awesome, you are a sponsor! I have given you your roles", ephemeral=True)
                print(f"Gave sponsor role to {discord_display_name}")
            else:
                await interaction.user.remove_roles(discord.Object(id=GH_SPONSORS_ROLE_ID))
                await interaction.followup.send(f"You are not a sponsor. You can become one here: {GH_SPONSORS_URL}", ephemeral=True)
                print(f"Removed sponsor role from {discord_display_name}")
            if user.is_contributor:
                roles = get_roles_from_contributor_repos(user.contributed_to_repos)
                for role in roles:
                    await interaction.user.add_roles(discord.Object(id=role))
                await interaction.followup.send("Thanks, you are a GitHub contributor! I have given you your roles", ephemeral=True)
                print(f"Gave contributor role to {discord_display_name}")
            else:
                roles = (x["REPO_ROLE_ID"] for x in GH_REPOS.values())
                for role in roles:
                    await interaction.user.remove_roles(discord.Object(id=role))
                print(f"Removed contributor role from {discord_display_name}")
            # Clean up old threads
            for thread in interaction.channel.threads:
                if thread.name == f"{discord_display_name}'s Thread":
                    await thread.delete()
                    print(f"Deleted thread {thread.name}")
        else:
            await interaction.followup.send("I have created a private thread for you to verify your sponsor/contributor status.", ephemeral=True)
            # Make new private thread
            thread_name = f"{discord_display_name}'s Thread"
            user_thread = None
            # Check if user already has a thread
            if interaction.channel.threads:
                for thread in interaction.channel.threads:
                    if thread.name == thread_name:
                        user_thread = thread
                        break
            if user_thread is None:
                user_thread = await interaction.channel.create_thread(name=thread_name, auto_archive_duration=60)
            await user_thread.add_user(interaction.user)
            await user_thread.send(f"Welcome to the server <@{interaction.user.id}>! Let's verify your sponsor/contributor status so you can access your project channel.")
            await user_thread.send(f"Please connect your GitHub account in Discord connections (no need to have it visible on your profile!) Once that is done, please follow this link: {generate_uri()}")
            await user_thread.send("Please run /verify in the other channel again once you have connected your GitHub account.")

    @tree.command(
        name="prune",
        description="Prune old sponsors",
        guild=discord.Object(id=GUILD_ID)
    )
    async def prune_command(interaction: discord.Interaction):
        await interaction.response.send_message("Pruning old sponsors...", ephemeral=True)
        await update_sponsors_and_contributors()
        await interaction.followup.send("Old sponsors pruned", ephemeral=True)

    @tasks.loop(hours=1)
    async def update_db_loop():
        update_db()
        print("Database auto-updated")

    @tasks.loop(minutes=5)
    async def update_sponsors_loop():
        await update_sponsors_and_contributors()

    @client.event
    async def on_ready():
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Logged in as {client.user}")
        update_db()
        await roles_message_refresh()
        try:
            update_db_loop.start()
            update_sponsors_loop.start()
        except RuntimeError:
            # Loop already running
            pass

    # Start stuff
    client.run(BOT_TOKEN)
