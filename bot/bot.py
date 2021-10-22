import discord

import config as c # README for example config
import cogs # bot/cogs/ package

from discord.ext import commands

class Bot(commands.Bot):
    async def on_ready(self):
        print("Bot ready.") # Log restart
        await bot.change_presence(activity = discord.Activity(name = f"these sick moves | v{c.version}", type = discord.ActivityType.watching)) # Set status
    
    async def on_message(self, message):
        if message.author.bot: return # Reject bot user
        return await bot.process_commands(message) # Process commands

bot = Bot(command_prefix = c.prefix)
bot.add_cog(cogs.Count(bot))
bot.add_cog(cogs.General(bot))
bot.run(c.token)