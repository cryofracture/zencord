import os
import datetime

import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import random
import logging

# Create a logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
zencord_error_handler = logging.FileHandler(f"./zencord_bot_err_{current_date}.log")
zencord_handler = logging.FileHandler(f"./zencord_bot_{current_date}.log")
zencord_error_handler.setLevel(logging.ERROR)
zencord_handler.setLevel(logging.INFO)

# Create formatters and add them to handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
zencord_error_handler.setFormatter(formatter)
zencord_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(zencord_error_handler)
logger.addHandler(zencord_handler)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)




@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)

    logger.info(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@bot.command(name='support_ticket')
async def support_ticket_command(ctx, *args):
    description = ' '.join(args).replace(',', '')
    await ctx.author.send(
        "Hello, I'm the Casper Support Bot and will help you in opening a request for the support team to review and assist you as soon as possible."
    )
    description_check = await ctx.author.send(f"To confirm, you described your issue as: {description}\n\nIs that right?")
    response = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    if response.content.lower() == "yes":
        await ctx.author.send(
            f"Thanks for confirming that, {ctx.author.name}. Please provide a subject for the support ticket: "
        )
        subject_response = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
        subject = subject_response.content
        try:
            new_ticket = open_new_ticket(description, subject, ctx.author.name)
        except Exception as e:
            print(e)
        await ctx.author.send(
            f"All right, {ctx.author.name}, I have created a new ticket for you and the Casper Labs Support team will begin reviewing your issue and get back to you soon."
        )
        await ctx.author.send(
            f"The new ticket ID is {new_ticket}"
        )
    else:
        await ctx.author.send("Okay, please re-enter your issue description if you'd like to open a support ticket.")


def open_new_ticket(request_description: str, request_subject: str, requester_name: str):
    zd_email = os.environ['ZD_EMAIL']
    zd_api_token = os.environ['ZD_TOKEN']
    zd_subdomain = os.environ['ZD_DOMAIN']
    headers = {'Content-Type': 'application/json'}
    url = f'https://{zd_subdomain}.zendesk.com/api/v2/requests.json'

    body = {
        "request": {
            "comment": {
                "body": request_description
            },
            "subject": request_subject,
            "requester": {
                "name": requester_name
            }
        }
    }

    auth = (zd_email, zd_api_token)

    response = requests.post(url, auth=auth, headers=headers, json=body)

    if response.status_code == 201:
        data = response.json()
        ticket_id = data['request']['id']
        return ticket_id
    else:
        raise Exception("Failed to create ticket.")


@bot.command(name='update_ticket')
async def update_ticket_command(ctx):
    if ctx.guild is not None:
        await ctx.send("This command can only be used in DMs.")
        return

    # Extract the ticket ID from the user's message content
    try:
        ticket_id = int(ctx.message.content.split()[1])
    except (ValueError, IndexError):
        await ctx.send("Please provide a valid ticket ID.")
        return

    # Check if the user is the requester of the provided ticket ID
    if not has_active_ticket(ctx.author, ticket_id):
        await ctx.send("You are not the requester of the provided ticket ID.")
        return

    await ctx.author.send(f"You have requested to update support ticket #{ticket_id}. Please provide your update:")
    update_response = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    update_content = update_response.content

    try:
        await update_ticket_comment(ticket_id, update_content)
        await ctx.author.send("Your update has been added to the support ticket.")
    except Exception as e:
        print(e)
        await ctx.author.send("An error occurred while updating the support ticket. Please try again later.")


# def has_active_ticket(user, ticket_id):
#     # Implement your logic to check if the user has an active ticket
#     # You can use a database or any other storage mechanism to track active tickets for each user
#     # Return True if the user has an active ticket, False otherwise
#     # For demonstration purposes, assume the user has an active ticket with ID 123
#     active_ticket_id = 123
#     return active_ticket_id is not None and active_ticket_id > 0


async def update_ticket_comment(ticket_id: int, comment: str):
    zd_email = os.environ['ZD_EMAIL']
    zd_api_token = os.environ['ZD_TOKEN']
    zd_subdomain = os.environ['ZD_DOMAIN']
    headers = {'Content-Type': 'application/json'}
    url = f'https://{zd_subdomain}.zendesk.com/api/v2/requests/{ticket_id}.json'

    body = {
        "request": {
            "comment": {
                "body": comment
            }
        }
    }

    auth = (zd_email, zd_api_token)

    response = requests.put(url, auth=auth, headers=headers, json=body)

    if response.status_code == 200:
        print("Comment updated successfully.")
    else:
        print("Failed to update comment.")


# description = "This is a test of Zencord bot."
# subject = "Taylor Test Ticket"
# open_new_ticket(description, subject)

bot.run(TOKEN)
