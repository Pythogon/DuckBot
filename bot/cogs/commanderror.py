import discord
import config as c
from discord.ext import commands   

class Commanderror(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Error messages
        try:
            print(f"Exception in {ctx.command}: {error.with_traceback()}")
        except:
            print(f"Exception in {ctx.command}: {error}")

        embed = discord.Embed(title = "An error has occured!", color = 0x000000).set_footer(text = c.embed_footer_text).set_thumbnail(url = ctx.me.avatar_url)

        if isinstance(error, commands.MissingRequiredArgument):
            embed.add_field(name = f"You are missing a required argument.", value = "If the error persists, please contact Ash.")

        else:
            embed.add_field(name = error, value = "If the error persists, please contact Ash.")
        
        return await ctx.send(embed = embed)