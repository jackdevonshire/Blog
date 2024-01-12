# py -m pip install discord-webhook
from discord_webhook import DiscordWebhook, DiscordEmbed
import os
import time
import requests
from datetime import datetime


# https://pypi.org/project/discord-webhook/
DISCORD_WEBHOOK_URL = ""
WEBHOOK_MESSAGE_ID = ""
HOST_IP = ""

if WEBHOOK_MESSAGE_ID == "" and DISCORD_WEBHOOK_URL != "":
    DiscordWebhook(url=DISCORD_WEBHOOK_URL, content="This is the first time running the MC Bedrock server script. Right click on this message, click 'Copy Message Id' and then place then add this to the WEBHOOK_MESSAGE_ID variable in this script! Then reboot the server!").execute()
    quit()


def alter_webhook(status, message):
    if (DISCORD_WEBHOOK_URL == ""):
        return

    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, id=WEBHOOK_MESSAGE_ID)
    
    # First clear message embeds
    webhook.remove_embeds()

    message = "**" + status.upper() + ":** " + message
    
    # Add status embed
    if status == "Online":
        status_embed = DiscordEmbed(title="Status", description=message, color="41C200") # Green
    elif status == "Starting Up":
        status_embed = DiscordEmbed(title="Status", description=message, color="F7860D") # Orange
    elif status == "Shutting Down":
        status_embed = DiscordEmbed(title="Status", description=message, color="F7860D") # Orange
    elif status == "Offline":
        status_embed = DiscordEmbed(title="Status", description=message, color="FB0703") # Red
    
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    webhook.content = "Last Updated: " + dt_string
    webhook.add_embed(status_embed)
    webhook.edit()

def startup():
    # Start MC server
    alter_webhook("Starting Up", "Server is starting up")
    os.system("start C:\\Users\\Administrator\\Desktop\\server\\bedrock_server")

    # Wait for MC server to be started
    time.sleep(30)

    # Server Started
    alter_webhook("Online", "The server is online")

def main_loop():
    try:
        while True:
            # Check server status every ten minutes
            time.sleep(600)
            alter_webhook("Online", "Checking player count")
            response = requests.get("https://api.mcstatus.io/v2/status/bedrock/"+HOST_IP)
            json = response.json()

            if not json["online"]:
                stop_server_and_ec2("Server unexpectedly appeared offline")
        
            players = json["players"]
            if players["online"] == 0:
                # If no players, wait another 5 minutes and if still no players, stop the server
                alter_webhook("Shutting Down", "No players detected. Server will shut down if no players join in the next 5 minutes")

                time.sleep(300)
                response = requests.get("https://api.mcstatus.io/v2/status/bedrock/"+HOST_IP)
                json = response.json()
                players = json["players"]
                if players["online"] == 0:
                    stop_server_and_ec2("No players detected for 15 minutes")
                
            alter_webhook("Online", "Server is online and has " + str(players["online"]) + " active players")

            
    except Exception as e:
        stop_server_and_ec2("An unexpected error ocurred: " + str(e))



def stop_server_and_ec2(message):
    alter_webhook("Offline", "Server has been stopped - " + message)
    os.system('shutdown -s')
    time.sleep(120)
    
    if (DISCORD_WEBHOOK_URL != ""):
        DiscordWebhook(url=DISCORD_WEBHOOK_URL, content="FAILED TO STOP SERVER").execute()


startup()
main_loop()

