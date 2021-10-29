import datetime
import discord
import time

import config as c
import datastoragefunctions as dsf

from discord.ext import commands, tasks # Utilising discord.ext.tasks to loop asynchronously

class Notifications(commands.Cog):
    """
    Cog for scheduling user notifications to a weekly schedule
    """
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.notifier.start()
    
    def cog_unload(self):
        self.notifier.cancel()

    @tasks.loop(minutes = 30)
    async def notifier(self):
        """
        Notifier loop for executing every day
        """
        await self.bot.wait_until_ready()
        print("Running cogs.Notifications.notifier() loop") # System notification
        all_data = dsf.dataStorageRead()
        notifications_data = all_data["notifications"]
        if (time.time() - notifications_data["last-time"]) < 86400: # 86400 seconds in a day
            return print("cogs.Notifications.notifier() terminated: not been 86400s")

        day = datetime.datetime.today().weekday() # Get weekday index for schedule lookup
        if notifications_data["schedule"][day] == []:
            return print("cogs.Notifications.notifier() terminated: no-one to mention")
        
        out_string = ""
        for user_id in notifications_data["schedule"][day]:
            out_string += f"<@{user_id}>\n"
        out_string += notifications_data["message"]

        channel = self.bot.get_channel(c.notification_channel)
        await channel.send(out_string)

        all_data["notifications"]["last-time"] = round(time.time())
        dsf.dataStorageWrite(all_data)
        print(f"cogs.Notifications.notifier() complete. output: {out_string}")
        
