import discord

import config as c
from discord.ext import commands

class Count(commands.Cog):
    """
    Cog for counting channel functionality.
    """
    def __init__(self, bot):
        self.bot = bot 
        self._last_member = None
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Function for handling counting channel messages and functions
        """
        if message.author.bot: return # Bots could interfere
        if message.channel.id != c.counting_channel: return # This handler is only for counting channel