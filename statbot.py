import datetime
import os
import discord
import matplotlib.pyplot as plt
from discord.ext import commands

TOKEN = os.environ['DISCORD_TOKEN']
DATE_FORMAT = "%d.%m.%Y"

bot = commands.Bot(command_prefix='>')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def stats(ctx, channel: discord.TextChannel):
    now = datetime.datetime.now()
    start = datetime.datetime(now.year - 1, now.month, now.day)
    status: discord.Message = await ctx.send(
        f"Gathering stats from **{start.strftime(DATE_FORMAT)}** to **{now.strftime(DATE_FORMAT)}**"
    )

    delta = now - start
    days = reversed([now - datetime.timedelta(days=x) for x in range(delta.days + 1)])

    messages = await channel.history(limit=None, after=start, before=now).flatten()
    # Ignore bots
    messages = [m for m in messages if not m.author.bot]
    await status.edit(content=f"Gathered **{len(messages)}** messages...")

    days = [(d.strftime(DATE_FORMAT), len(list(filter(lambda m: m.created_at.date() == d.date(), messages))), d) for d in days]
    most_active = max(days, key=lambda d: d[1])

    msg_stats = {}

    users = list(set([m.author.id for m in messages]))

    for message in messages:
        idx = message.author.id
        msg_stats[idx] = msg_stats.get(idx, 0) + 1

    msg_stats = [(k, v) for k, v in msg_stats.items()]
    msg_stats.sort(key=lambda m: m[1], reverse=True)
    plt.figure(dpi=1200)

    plt.plot([d[0] for d in days], [d[1] for d in days])

    ax = plt.gca()
    # Reformat the dates
    ax.xaxis.set_ticklabels([d[2].strftime("%b. %y") for d in days])

    # Only show one day per month on the axis
    [l.set_visible(days[i][2].day == 1) for (i, l) in enumerate(ax.xaxis.get_ticklabels())]
    [l.set_visible(days[i][2].day == 1) for (i, l) in enumerate(ax.xaxis.get_major_ticks())]

    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
    plt.ylabel("Messages")
    plt.savefig('filename.png')

    embed = discord.Embed(title=f"Stats for #{channel.name}")
    embed.add_field(name="Most active", value=f"<@!{msg_stats[0][0]}>")
    embed.add_field(name="Messages", value=f"{len(messages)}")
    embed.add_field(name="Distinct users", value=f"{len(users)}")
    embed.add_field(name="Start", value=start.strftime(DATE_FORMAT))
    embed.add_field(name="End", value=now.strftime(DATE_FORMAT))
    embed.add_field(name="Days", value=f"{delta.days}")
    embed.add_field(name="Most active", value=f"{most_active[0]}, {most_active[1]} messages")
    embed.add_field(name="Channel created", value=f"{channel.created_at.strftime(DATE_FORMAT)}")

    await ctx.send(content=f"**Graph of** <#{channel.id}>", file=discord.File(open('filename.png', 'rb')))
    await status.edit(content=None, embed=embed)

bot.run(TOKEN)
