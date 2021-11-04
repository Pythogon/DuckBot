import datetime
import discord
import re
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
        self.notifier.start() # Run loop
    
    def cog_unload(self):
        self.notifier.cancel()

    @tasks.loop(minutes = 30)
    async def notifier(self):
        """
        Notifier loop for executing every day & every week
        """
        await self.bot.wait_until_ready() # Because we're using send and get_channel later
        print("Running cogs.Notifications.notifier() loop") # System notification
        all_data = dsf.dataStorageRead()
        channel = self.bot.get_channel(c.notification_channel)

        while True:
            """
            Week scheduler
            """
            print("cogs.Notifications.notifier(): running week-notifications subscript")
            week_notif_data = all_data["week-notifications"]

            if (time.time() - week_notif_data["last-time"]) < 86400:
                print("cogs.Notifications.notifier(): week-notifications terminated: already run today") # Only need to test day once a day
                break

            if datetime.datetime.today().weekday() != 0:
                week_notif_data["last-time"] = round(time.time()) # Attempt for today over
                all_data["week-notifications"] = week_notif_data
                print("cogs.Notifications.notifier(): week-notifications terminated: not MON")
                break

            who = week_notif_data["last-index"] + 1 # Get index
            week_notif_data["last-index"] += 1 # Increment last-index
            week_notif_data["last-time"] = round(time.time()) # Attempt for today

            if who == len(week_notif_data["schedule"]): # Wraparound
                who = 0 
                week_notif_data["last-index"] = 0
            
            print(who)
            out_string = f"<@{week_notif_data['schedule'][who]}>\n{week_notif_data['message']}"
            await channel.send(out_string)
            all_data["week-notifications"] = week_notif_data
            print(f"cogs.Notifications.notifier() week-notifications complete. output = {out_string}")
            break

        while True:
            """
            Day scheduler
            """
            print("cogs.Notifications.notifier(): running day-notifications subscript")
            notifications_data = all_data["day-notifications"] # Abbreviate
            if (time.time() - notifications_data["last-time"]) < 86400: # 86400 seconds in a day
                print("cogs.Notifications.notifier(): day-notifications terminated: already run today")
                break
    
            day = datetime.datetime.today().weekday() # Get weekday index for schedule lookup
            if notifications_data["schedule"][day] == []:
                print("cogs.Notifications.notifier(): day-notifications terminated: no-one to mention") # Cancel out on days where there's no-one to notify
                break
        
            out_string = ""
            for user_id in notifications_data["schedule"][day]:
                out_string += f"<@{user_id}>\n" # Build output string
            out_string += notifications_data["message"] # Fetch notification message

            await channel.send(out_string) # Send notification message to config.notification_channel

            all_data["day-notifications"]["last-time"] = round(time.time()) # Change last time that loop executed successfully
            print(f"cogs.Notifications.day_notifier(): day-notifications complete. output: {out_string}")
            break
        print("cogs.Notifications.notifier() loop complete")
        dsf.dataStorageWrite(all_data) # Save to database
            
    @commands.group()
    async def dayschedule(self, ctx):
        if ctx.invoked_subcommand is None:
            print(f"User {ctx.author.id} used dayschedule list. args: None")
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

    @dayschedule.command(name = "add")
    async def day_schedule_add(self, ctx, day_string, user: discord.User):
        print(f"User {ctx.author.id} used dayschedule add. args: {day_string}, {user.id}")
        all_data = dsf.dataStorageRead()

        day_index = day_to_index(day_string) # take 3 letter day code and convert into index for notifications schedule
        if day_index is None:
            return await ctx.send("You have entered an invalid day. Valid days: MON, TUE, WED, THU, FRI, SAT, SUN.") # Catch invalid day
        if user.id in all_data["day-notifications"]["schedule"][day_index]:
            return await ctx.send("That user is already assigned to this day.") # Duplicate entries into schedule day would make dupe pings

        all_data["day-notifications"]["schedule"][day_index].append(user.id) # Add user id to schedule day array for easier mentioning
        dsf.dataStorageWrite(all_data) # Save to database
        return await ctx.send(f"Success! {user.name} has been assigned to {day_string.upper()}.")

    @dayschedule.command(name = "remove")
    async def day_schedule_remove(self, ctx, day_string, user: discord.User):
        print(f"User {ctx.author.id} used dayschedule remove. args: {day_string}, {user.id}")
        all_data = dsf.dataStorageRead() # Data read from database

        day_index = day_to_index(day_string) # convert day code to index
        if day_index is None:
            return await ctx.send("You have entered an invalid day. Valid days: MON, TUE, WED, THU, FRI, SAT, SUN.") # Catch invalid day
        if user.id not in all_data["day-notifications"]["schedule"][day_index]: 
            return await ctx.send("That user is not assigned to this day.") # Attempting to remove a user who doesn't exist may cause problems
        all_data["day-notifications"]["schedule"][day_index].remove(user.id) # Remove user from schedule
        dsf.dataStorageWrite(all_data)
        await ctx.send(f"Success! {user.name} has been removed from {day_string.upper()}")
    
    @commands.group()
    async def weekschedule(self, ctx):
        if ctx.invoked_subcommand == None:
            print(f"User {ctx.author.id} used weekschedule list.")
            notif_data = dsf.dataStorageRead()["week-notifications"]
            who = notif_data["last-index"] + 1
            if who == len(notif_data["schedule"]): who = 0
            await ctx.send(f"The next weekly notification will be for <@{notif_data['schedule'][who]}>.") # Quick information
    
    @weekschedule.command(name = "set")
    async def week_schedule_set(self, ctx, *args):
        print(f"User {ctx.author.id} used weekschedule set. args: {args}")
        all_data = dsf.dataStorageRead() # Read data
        mention_pattern = r"[<>@!]" # Regular expression of mention filler characters
        user_ids = []

        for x in args:
            mod_x = re.sub(mention_pattern, "", x)  # Remove <@> 
            try: 
                int(mod_x) 
            except:
                return await ctx.send("One or more of your arguments is not a user mention.") # Needs to be a user mention for the scheduler
            user_ids.append(mod_x) # add to user user_ids
        
        all_data["week-notifications"]["schedule"] = user_ids # Set the schedule for week-notifications
        all_data["week-notifications"]["last-index"] = (len(user_ids) - 1) # Ensure the next user to be notified is the first in args
        dsf.dataStorageWrite(all_data) # Save to database

        await ctx.send(f"Done! The next user to be notified will be {args[0]}.")
