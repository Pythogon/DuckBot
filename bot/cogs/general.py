import discord
import config as c
import datastoragefunctions as dsf

from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self._last_member = None
    
    @commands.command()
    async def help(self, ctx):
        """
        Custom help command, default looks shabby.
        """
        p = c.prefix # Abbreviation to save time 
        embed = discord.Embed(title = "Help menu", description = "<> indicates a required argument.", color = c.embed_color) \
        .set_thumbnail(url = ctx.me.avatar_url) \
        .add_field(name = "Commands", value = f"""{p}help: Shows this message.
{p}metrics <user>: See stored information about a user.
{p}ping: Check if the bot is connected.
{p}record: Check the current counting channel record.""", inline = False) \
        .add_field(name = "Counting channel", value = f"""This bot provides a counting channel. This channel can be located at <#{c.counting_channel}>. To use the counting channel, you just need to type the number after the last number sent to the channel. Your message will be automatically deleted.""", inline = False) \
        .add_field(name = "Starboard", value = f"""This bot also provides a starboard for you to use! The starboard channel can be found at <#{c.star_channel}>. To get a message onto the starboard channel, just react with a ⭐! If the message gets {c.star_quota} ⭐s, it will be automatically put onto the starboard.""", inline = False) \
        .set_footer(text = c.embed_footer_text) # Very large help embed
        
        await ctx.send(embed = embed)
    
    @commands.command()
    async def metrics(self, ctx, user: discord.User):
        userdata = dsf.userStorage("r", user.id)
        embed = discord.Embed(title = f"Metrics for {user}", color = c.embed_color) \
        .set_thumbnail(url = user.avatar_url) \
        .add_field(name = "Counting", value = f"""Total number of messages in the counting channel: **{userdata["count"]["number"]}**
Number of times failed in the counting channel: **{userdata["count"]["fails"]}**""", inline = False) \
        .add_field(name = "Starboard", value = f"Total number of messages added to the starboard: **{userdata['starboard']['number']}**", inline = False) \
        .set_footer(text = c.embed_footer_text) # Metric fetching embed
        await ctx.send(embed = embed)

    @commands.command()
    async def ping(self, ctx):
        """
        Checks if the bot is connected.
        """
        await ctx.send("Pong!")