import discord
from discord.ext import commands
import asyncio
import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 123456789012345678  # Replace with your guild ID
VERIFICATION_CHANNEL_NAME = "verification"
PLAYER_ROLE_NAME = "player"

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

def get_valid_nicknames_from_pins(pins):
    valid_nicks = set()
    for msg in pins:
        for line in msg.content.splitlines():
            nickname = line.strip()
            if nickname:
                valid_nicks.add(nickname.lower())
    return valid_nicks

@bot.event
async def on_member_join(member):
    await asyncio.sleep(1)  # Slight delay for Discord to register them fully
    guild = member.guild
    verification_channel = discord.utils.get(guild.text_channels, name=VERIFICATION_CHANNEL_NAME)

    if not verification_channel:
        print("Verification channel not found.")
        return

    pinned_messages = await verification_channel.pins()
    valid_nicknames = get_valid_nicknames_from_pins(pinned_messages)

    # Get the last message from this member in that channel
    async for msg in verification_channel.history(limit=20):
        if msg.author == member:
            submitted_nick = msg.content.strip().lower()
            break
    else:
        return  # No message from the user found

    # Check if it's valid and not already taken
    if submitted_nick in valid_nicknames:
        taken = any(m.display_name.lower() == submitted_nick for m in guild.members if m != member)
        if not taken:
            role = discord.utils.get(guild.roles, name=PLAYER_ROLE_NAME)
            try:
                await member.edit(nick=submitted_nick)
                if role:
                    await member.add_roles(role)
                print(f"Verified {member.name} as {submitted_nick}")
            except discord.Forbidden:
                print("Missing permissions to change nickname or assign role.")
