import discord
import config as c
import datastoragefunctions as dsf

from discord.ext import commands


class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, p: discord.RawReactionActionEvent):
        """
        Starboard reaction add handler, inspired by https://github.com/Pythogon/PhaseBot
        """
        channel = self.bot.get_channel(p.channel_id)  # Fetching event channel and message
        message = await channel.fetch_message(p.message_id)

        # Checks #
        if p.emoji.name != "⭐":
            return  # Only looking for :star:
        if message.author.bot:
            return  # Bots cannot be added to starboard
        if discord.utils.get(message.reactions, me=True, emoji="🌟"):
            return # :star2: is indicator of prior starboard, prevents stars from being spammed on
        reactions = discord.utils.get(message.reactions, emoji="⭐")
        if reactions.count != c.star_quota:
            return  # Cannot starboard if wrong amount of reactions

        # Starring #
        s_channel = self.bot.get_channel(c.star_channel)  # Get star channel for send later
        userdata = dsf.userstorage("r", message.author.id)
        if message.content == "":
            message_content = str(message.attachments[0])  # Prevents error when sending attachments
        else:
            message_content = message.content

        embed = discord.Embed(title=f"{message.author}'s message in #{channel} just got starred!", color=c.embed_color) \
            .add_field(name="Message content", value=message_content, inline=False) \
            .add_field(name="Link to message", value=message.jump_url, inline=False) \
            .set_footer(text=c.embed_footer_text)  # Generate starboard embed
        await s_channel.send(embed=embed)

        userdata["starboard"]["number"] += 1  # Increment starboard number
        dsf.userstorage("w", message.author.id, data=userdata)  # Save user data to database

        await message.add_reaction("🌟")  # Let this function know the bot has already processed this message
