import os
import discord
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands
from datetime import datetime
import json

load_dotenv()
TOKEN = os.getenv("TOKEN")
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("curriculum tracker")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
TASK_DEADLINES = {
    "Task 00 Codeforces": None,  
    "Task 01 Git": 5,
    "Task 02 Web Dev basics": 10,
    "Task 03 Build a Simple Shell": 12,
    "Task 04 NOT A SRS DOC": 3,
    "Task 05 WIREFRAME THE SKELETON": 5,
    "Task 06 Figma Design Task": 7,
    "Task 07 Frontend Development": 12,
    "Task 08 Backend Development": 12,
    "Task 09 Flutter Development": 10,
}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command(name="taskstatusgroup1")
async def taskstatus_group1(ctx):
    await fetch_tasks_for_group(ctx, "GROUP1")


@bot.command(name="taskstatusgroup2")
async def taskstatus_group2(ctx):
    await fetch_tasks_for_group(ctx, "GROUP2")


@bot.command(name="taskstatusgroup3")
async def taskstatus_group3(ctx):
    await fetch_tasks_for_group(ctx, "GROUP3")


@bot.command(name="taskstatusgroup4")
async def taskstatus_group4(ctx):
    await fetch_tasks_for_group(ctx, "GROUP4")

@bot.command(name="curriculumdeadlines")
async def curriculum_deadlines(ctx):
    embed = discord.Embed(
        title="📌 Curriculum Deadlines",
        description="Here are the task deadlines for the curriculum:",
        color=discord.Color.orange()
    )
    for task, days in TASK_DEADLINES.items():
        if days is None:
            deadline = "Until objectives are met"
        else:
            deadline = f"{days} days"

        embed.add_field(name=task, value=deadline, inline=False)

    embed.set_footer(text="")
    
    await ctx.send(embed=embed)
async def fetch_tasks_for_group(ctx, group_name):
    try:
        available_sheets = [ws.title for ws in sheet.worksheets()]
        if group_name not in available_sheets:
            await ctx.send(
                f"Error: Sheet '{group_name}' not found!\nAvailable sheets: {', '.join(available_sheets)}"
            )
            return
        worksheet = sheet.worksheet(group_name)
        data = worksheet.get_all_values()
        mentee_tasks = {}
        last_mentee = None
        for row in data[1:]:
            if not any(row):
                continue
            mentee, task, state, start_date, end_date, *_ = row
            if mentee.strip():
                last_mentee = mentee.strip()
                if last_mentee not in mentee_tasks:
                    mentee_tasks[last_mentee] = []
            if last_mentee is None:
                continue
            days_taken = ""
            date_format = "%d/%m/%Y"
            if state.strip().lower() == "done" and start_date and end_date:
                try:
                    start = datetime.strptime(start_date, date_format)
                    end = datetime.strptime(end_date, date_format)
                    days_taken = f" ({(end - start).days} days)"
                except ValueError:
                    pass
                mentee_tasks[last_mentee].append(
                    f"✅️ **{task}** - time taken: {start_date} - {end_date}{days_taken}"
                )
            elif state.strip().lower() == "in progress" and start_date:
                try:
                    start = datetime.strptime(start_date, date_format)
                    today_date = datetime.today()
                    days = f" ({(today_date - start).days} days)"
                except ValueError:
                    days= ""  
                mentee_tasks[last_mentee].append(f"🟠 **{task}** -In Progress, start date: {start_date}, days: {days}⃰")
        embed = discord.Embed(
            title=f"Tasks from {group_name}", color=discord.Color.orange()
        )
        embed.set_footer(text="Curriculum Tracker Bot")

        if not mentee_tasks:
            embed.description = "No tasks found"
        else:
            for mentee, tasks in mentee_tasks.items():
                embed.add_field(
                    name=f"__**{mentee}**__", value="\n".join(tasks), inline=False
                )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Error fetching data from {group_name}: {e}")


bot.run(TOKEN)
