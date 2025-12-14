import discord
from discord.ext import commands
import subprocess
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN is not set in the .env file.")

# Intents and bot setup
intents = discord.Intents.default()
intents.message_content = True  # Fixed invalid intent
bot = commands.Bot(command_prefix="/", intents=intents)

def run_command(command):
    """Run a shell command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {command}")
        print(f"Error: {result.stderr}")
        return False, result.stderr
    return True, result.stdout

def save_to_git(file_name, content, repo_url):
    """Save content to a file and push to GitHub."""
    # Write content to file
    with open(file_name, "w") as file:
        file.write(content)

    # Check if .git directory exists
    if not os.path.exists(".git"):
        success, _ = run_command("git init")
        if not success:
            raise RuntimeError("Failed to initialize Git repository.")
        success, _ = run_command(f"git remote add origin {repo_url}")
        if not success:
            raise RuntimeError("Failed to add remote repository.")

    # Add, commit, and push changes
    run_command("git add .")
    run_command("git commit -m \"Save message\"")
    success, output = run_command("git push -u origin master")  # Updated branch to 'master'
    if not success:
        raise RuntimeError(f"Failed to push changes: {output}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def save(ctx, *, args):
    """Save a message to the Git repository."""
    try:
        # Parse the title and message
        if "title:" not in args or "message:" not in args:
            await ctx.send("Invalid format! Use /save title: <title> message: <message>")
            return

        title_start = args.find("title:") + len("title:")
        message_start = args.find("message:")
        if title_start == -1 or message_start == -1 or title_start >= message_start:
            await ctx.send("Invalid format! Use /save title: <title> message: <message>")
            return

        title = args[title_start:message_start].strip()
        message = args[message_start + len("message:"):].strip()

        if not title or not message:
            await ctx.send("Both title and message must be provided.")
            return

        # Format the content
        user_info = f"by {ctx.author.name} ({ctx.author.id})"
        content = f"{title}\n\n{message}\n\n{user_info}"

        # Save to GitHub
        file_name = f"{title.replace(' ', '_')}.txt"
        repo_url = "https://github.com/DatLittlaDucky/Image-GPT-Images-Generated.git"
        save_to_git(file_name, content, repo_url)

        await ctx.send(f"Message saved to GitHub as {file_name}!")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

# Run the bot
bot.run(BOT_TOKEN)