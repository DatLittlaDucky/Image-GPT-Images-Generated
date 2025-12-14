import discord
from discord.ext import commands
from discord import app_commands  # Import for slash commands
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
intents.message_content = True
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
    success, output = run_command("git push -u origin master")
    if not success:
        raise RuntimeError(f"Failed to push changes: {output}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        # Sync commands with Discord
        await bot.tree.sync()
        print("Slash commands synced successfully.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="save")
@app_commands.describe(title="The title of the message", message="The content of the message")
async def save(interaction: discord.Interaction, title: str, message: str):
    """Save a message to the Git repository."""
    try:
        # Format the content
        user_info = f"by {interaction.user.name} ({interaction.user.id})"
        content = f"{title}\n\n{message}\n\n{user_info}"

        # Save to GitHub
        file_name = f"{title.replace(' ', '_')}.txt"
        repo_url = "https://github.com/DatLittlaDucky/Image-GPT-Images-Generated.git"
        save_to_git(file_name, content, repo_url)

        await interaction.response.send_message(f"Message saved to GitHub as {file_name}!")
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}")

# Run the bot
bot.run(BOT_TOKEN)