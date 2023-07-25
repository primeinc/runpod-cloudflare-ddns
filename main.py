import os
import configparser
import random
import requests
from datetime import datetime, timedelta
import CloudFlare

# Check if the configuration file exists
config_file = 'config.ini'
if not os.path.exists(config_file):
    print(f"The configuration file {config_file} does not exist.")
    print("Please rename config.ini.defaults to config.ini and fill in your information.")
    exit(1)

# Read the configuration file
config = configparser.ConfigParser()
config.read(config_file)

# List of adjectives and animals
adjectives = ["silly", "smelly", "cool", "lazy", "quick", "happy", "sad", "tiny", "big", "crazy",
              "furry", "soft", "loud", "quiet", "fast", "slow", "friendly", "grumpy"]
animals = ["cat", "dog", "mouse", "bird", "fish", "lion", "tiger", "elephant", "monkey", "zebra",
           "giraffe", "bear", "rabbit", "turtle", "fox", "wolf", "horse", "squirrel"]

try:
    # Initialize Cloudflare client
    cf = CloudFlare.CloudFlare(token=config['Cloudflare']['Token'], debug=config['Cloudflare']['Debug'])

    # Path to the log file
    log_file_path = config['General']['Log_File_Path']

    # Generate a unique subdomain
    while True:
        subdomain = random.choice(adjectives) + random.choice(animals)
        if not os.path.exists(log_file_path):
            open(log_file_path, 'w').close()
        with open(log_file_path, 'r') as log_file:
            if subdomain not in log_file.read():
                break

    # Get public IP
    public_ip = requests.get('https://api.ipify.org').text

    # Create the subdomain on Cloudflare
    zone_id = config['Cloudflare']['Zone_ID']
    zone = cf.zones.get(zone_id)
    zone_name = zone['name']
    dns_records = cf.zones.dns_records.post(zone_id, data={
        "type": "A",
        "name": subdomain,
        "content": public_ip,
        "ttl": 120,
        "proxied": False
    })

    # Change the hostname
    try:
        with open('/etc/hostname', 'w') as hostname_file:
            hostname_file.write(subdomain)
    except PermissionError:
        print("Permission error while trying to change the hostname. Please ensure the script has the necessary permissions to modify /etc/hostname.")
    except Exception as e:
        print(f"An error occurred while trying to change the hostname: {e}")

    # Append the subdomain and current date to the log file
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{subdomain},{datetime.now()}\n")

    # Check the log file for entries older than the configured hours and delete them
    delete_after_hours = int(config['General']['Delete_After_Hours'])
    if delete_after_hours > 0:
        with open(log_file_path, 'r') as log_file:
            lines = log_file.readlines()
        with open(log_file_path, 'w') as log_file:
            for line in lines:
                subdomain, date = line.strip().split(',')
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                if datetime.now() - date <= timedelta(hours=delete_after_hours):
                    log_file.write(line)
                else:
                    # Delete the subdomain on Cloudflare
                    dns_records = cf.zones.dns_records.get(zone_id)
                    for record in dns_records:
                        if record['name'] == subdomain:
                            cf.zones.dns_records.delete(zone_id, record['id'])
                            print(f"Deleted subdomain {subdomain} due to exceeding the age limit of {delete_after_hours} hours.")


    # Print out the URL, IP address, and hostname
    print("\n--- Setup Complete ---")
    print(f"Hostname: {subdomain}.{zone_name}")
    print(f"IP Address: {public_ip}")
    print(f"https://{subdomain}.{zone_name}")

except CloudFlare.exceptions.CloudFlareAPIError:
    print(f"Authentication error. Please check your Cloudflare configuration in {config_file}.")
    print(f"Email: {config['Cloudflare']['Email']}")
    print(f"Zone_ID: {config['Cloudflare']['Zone_ID']}")
    print("Token: Please check that it's correct and has the necessary permissions.")
