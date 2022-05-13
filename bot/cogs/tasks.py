import discord
from datetime import datetime as dt

import config as c
import datastoragefunctions as dsf

from discord.ext import commands, tasks

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.notifier.start()

    def cog_unload(self):
        self.notifier.cancel()

    @tasks.loop(minutes=60)
    async def notifier(self):
        """
        Notifier loop, now with less clunk
        """
        await self.bot.wait_until_ready()
        print("Running cogs.Tasks.notifier()")
        #if dt.now().hour != c.notify_hour:
        #    return print("Aborting cogs.Tasks.notifier(): Not notify_hour")
        data = dsf.datastorageread()
        today = data["tasks"][dt.today().weekday()]
        if not today:
            return print("Aborting cogs.Tasks.notifier(): No tasks scheduled")
        output = "__Tasks for today__\n"
        for x in range(len(today)):  # where entry = {"task_name": str, "rota": list[str], "last_number": int}
            entry = today[x]
            entry["last_number"] += 1
            if len(entry["rota"]) == entry["last_number"]:
                entry["last_number"] = 0
            user_on = entry["rota"][entry["last_number"]]
            output += f"<@{user_on}> - {entry['task_name']}"
            data["tasks"][dt.today().weekday()][x] = entry
        channel = self.bot.get_channel(c.notification_channel)
        await channel.send(output)
        dsf.datastoragewrite(data)
        return print("cogs.Tasks.notifier() run successfully.")

    @commands.group()
    async def tasks(self, ctx):
        if not ctx.invoked_subcommand:
            return await ctx.send("Expected usage: tasks add|remove")

    @tasks.command(name="add")
    async def tasks_add(self, ctx, day, name, *args: discord.User):
        try:
            day = days.index(day.title())
        except ValueError:
            return await ctx.send("The day given is not valid. Please ensure you only write the first 3 letters of the "
                                  "day when you rerun the command.")
        users = []
        for user in args:
            users.append(user.id)
        data = dsf.datastorageread()
        data["tasks"][day].append({
            "task_name": name, "rota": users, "last_number": len(users) - 1})
        dsf.datastoragewrite(data)  # Read, add, write
        await ctx.send("Task successfully added!")

    @tasks.command(name="remove")
    async def tasks_remove(self, ctx, day, name):
        try:
            day = days.index(day.title())
        except ValueError:
            return await ctx.send("The day given is not valid. Please ensure you only write the first 3 letters of the "
                                  "day when you rerun the command.")
        to_pop = []
        data = dsf.datastorageread()
        day_data = data["tasks"][day]  # Prevent typing this whole thing out
        for x in range(len(day_data)):
            if day_data[x]["task_name"] == name:
                to_pop.append(x)
        to_pop.reverse()  # Decreasing order to prevent lower indices from changing
        for pop in to_pop:
            day_data.pop(pop)
        data["tasks"][day] = day_data  # Recombine
        dsf.datastoragewrite(data)
        await ctx.send("Task successfully removed.")
