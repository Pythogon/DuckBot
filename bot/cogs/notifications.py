import datetime
import discord
import time

import config as c
import datastoragefunctions as dsf

from discord.ext import commands, tasks # Utilising discord.ext.tasks to loop asynchronously

indices = {
        "MON": 0,
        "TUE": 1,
        "WED": 2,
        "THU": 3,
        "FRI": 4,
        "SAT": 5,
        "SUN": 6
    }

def day_to_index(day):
    day = day.upper()
    return indices.get(day, None)

def index_to_day(index: int):
    for d, i in indices.items():
        if i == index:
            return d
    return None

class Notifications(commands.Cog):
    """
    Cog for scheduling user notifications to a weekly schedule
    """
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.day_notifier.start()
    
    def cog_unload(self):
        self.day_notifier.cancel()

    @tasks.loop(minutes = 30)
    async def day_notifier(self):
        """
        Notifier loop for executing every day
        """
        await self.bot.wait_until_ready() # Because we're using send and get_channel later
        print("Running cogs.Notifications.day_notifier() loop") # System notification
        all_data = dsf.dataStorageRead()
        notifications_data = all_data["day-notifications"] # Abbreviate
        if (time.time() - notifications_data["last-time"]) < 86400: # 86400 seconds in a day
            return print("cogs.Notifications.day_notifier() terminated: not been 86400s")

        day = datetime.datetime.today().weekday() # Get weekday index for schedule lookup
        if notifications_data["schedule"][day] == []:
            return print("cogs.Notifications.day_notifier() terminated: no-one to mention") # Cancel out on days where there's no-one to notify
        
        out_string = ""
        for user_id in notifications_data["schedule"][day]:
            out_string += f"<@{user_id}>\n" # Build output string
        out_string += notifications_data["message"] # Fetch notification message

        channel = self.bot.get_channel(c.notification_channel) 
        await channel.send(out_string) # Send notification message to config.notification_channel

        all_data["day-notifications"]["last-time"] = round(time.time()) # Change last time that loop executed successfully
        dsf.dataStorageWrite(all_data) # Save to database
        print(f"cogs.Notifications.day_notifier() complete. output: {out_string}")
        
    @commands.group()
    async def dayschedule(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Correct usage is {c.prefix}schedule add|list|remove.")

    @dayschedule.command(name = "add")
    async def day_schedule_add(self, ctx, day_string, user: discord.User):
        print(f"User {ctx.author.id} used schedule add. args: {day_string}, {user.id}")
        all_data = dsf.dataStorageRead()

        day_index = day_to_index(day_string) # take 3 letter day code and convert into index for notifications schedule
        if day_index is None:
            return await ctx.send("You have entered an invalid day. Valid days: MON, TUE, WED, THU, FRI, SAT, SUN.") # Catch invalid day
        if user.id in all_data["day-notifications"]["schedule"][day_index]:
            return await ctx.send("That user is already assigned to this day.") # Duplicate entries into schedule day would make dupe pings

        all_data["day-notifications"]["schedule"][day_index].append(user.id) # Add user id to schedule day array for easier mentioning
        dsf.dataStorageWrite(all_data) # Save to database
        return await ctx.send(f"Success! {user.name} has been assigned to {day_string.upper()}.")

    @dayschedule.command(name = "list")
    async def day_schedule_list(self, ctx): 
        print(f"User {ctx.author.id} used schedule list. args: None")
        schedule_data = dsf.dataStorageRead()["day-notifications"]["schedule"] # Abbreviate
        out_string = "Notification schedule:\n"

        for x in range(len(schedule_data)):
            if schedule_data[x] == []: continue # Skip empty schedule days

            day = index_to_day(x) # Formatting
            out_string += f"__**{day}**__\n"
            for user in schedule_data[x]:
                out_string += f"<@{user}>"
            out_string += "\n"

        await ctx.send(out_string)

    @dayschedule.command(name = "remove")
    async def day_schedule_remove(self, ctx, day_string, user: discord.User):
        print(f"User {ctx.author.id} used schedule remove. args: {day_string}, {user.id}")
        all_data = dsf.dataStorageRead() # Data read from database

        day_index = day_to_index(day_string) # convert day code to index
        if day_index is None:
            return await ctx.send("You have entered an invalid day. Valid days: MON, TUE, WED, THU, FRI, SAT, SUN.") # Catch invalid day
        if user.id not in all_data["day-notifications"]["schedule"][day_index]: 
            return await ctx.send("That user is not assigned to this day.") # Attempting to remove a user who doesn't exist may cause problems
        all_data["day-notifications"]["schedule"][day_index].remove(user.id) # Remove user from schedule
        dsf.dataStorageWrite(all_data)
        await ctx.send(f"Success! {user.name} has been removed from {day_string.upper()}")


