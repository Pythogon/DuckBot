import discord

import config as c
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self._last_member = None
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")