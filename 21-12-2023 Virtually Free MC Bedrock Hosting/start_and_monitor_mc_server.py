###### Configuration ######
DISCORD_WEBHOOK_URL = ""
WEBHOOK_MESSAGE_ID = ""
DYNAMIC_DNS_URL = ""
SERVER_PORT = 19132

# How often the server checks the player count
CHECK_INTERVAL_MINUTES = 15
# Once no players are detected, recheck after this amount of time before shutting down the server
COOLDOWN_INTERVAL_MINUTES = 5



###### Main Program ######

# Startup
import os
import time
import requests
from datetime import datetime

try:
    from discord_webhook import DiscordWebhook, DiscordEmbed
    from mcstats import mcstats
except:
    os.system("py -m pip install discord-webhook")
    os.system("py -m pip install mcstats")
    print("Error loading script, try reloading")
    quit()

if WEBHOOK_MESSAGE_ID == "" and DISCORD_WEBHOOK_URL != "":
    DiscordWebhook(url=DISCORD_WEBHOOK_URL, content="This is the first time running the MC Bedrock server script. Right click on this message, click 'Copy Message Id' and then place then add this to the WEBHOOK_MESSAGE_ID variable in this script! Then reboot the server!").execute()
    quit()

# Main Methods
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

def get_server_players():
    try:
        with mcstats("localhost", port=SERVER_PORT, timeout=10) as data:
            return data.num_players
    except:
        return -1

def startup():
    # Update dynamic DNS service with server IP
    if DYNAMIC_DNS_URL != "":
        try:
            requests.get(DYNAMIC_DNS_URL)
        except:
            pass
    
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
            # Check server player count every x minutes
            time.sleep(CHECK_INTERVAL_MINUTES*60)
            alter_webhook("Online", "Checking player count")
            players = get_server_players()

            # If MC Server is stopped, then shutdown the server
            if players == -1:
                stop_server_and_ec2("Server unexpectedly appeared offline")
        
            if players == 0:
                # If no players, wait another x minutes and recheck before shutting down
                alter_webhook("Shutting Down", "No players detected. Server will shut down if no players join in the next " + str(COOLDOWN_INTERVAL_MINUTES) + " minutes")

                time.sleep(COOLDOWN_INTERVAL_MINUTES * 60)
                players = get_server_players()
                if players < 1:
                    stop_server_and_ec2("No players detected for 15 minutes")
                
            alter_webhook("Online", "Server is online and has " + str(players) + " active players")

            
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
