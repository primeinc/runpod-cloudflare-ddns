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
    subdomain_prefix = config['Cloudflare'].get('Subdomain_Prefix', '')
    print(f"Generating a unique subdomain ending with {subdomain_prefix}...")
    while True:
        subdomain = random.choice(adjectives) + random.choice(animals)
        full_subdomain = f"{subdomain}.{subdomain_prefix}" if subdomain_prefix else subdomain

        # Check if the subdomain exists in Cloudflare
        dns_records = cf.zones.dns_records.get(config['Cloudflare']['Zone_ID'])
        if not any(record['name'] == full_subdomain for record in dns_records):
            break

    # Get public IP
    public_ip = requests.get('https://api.ipify.org').text

    # Create the subdomain on Cloudflare
    zone_id = config['Cloudflare']['Zone_ID']
    zone = cf.zones.get(zone_id)
    zone_name = zone['name']
    dns_records = cf.zones.dns_records.post(zone_id, data={
        "type": "A",
        "name": full_subdomain,
        "content": public_ip,
        "ttl": 120,
        "proxied": False
    })

    # Change the hostname
    try:
        with open('/etc/hostname', 'w') as hostname_file:
            hostname_file.write(full_subdomain)
    except PermissionError:
        print("Permission error while trying to change the hostname. Please ensure the script has the necessary permissions to modify /etc/hostname.")
    except Exception as e:
        print(f"An error occurred while trying to change the hostname: {e}")
    
    try:
        with open('/etc/servername', 'w') as servername_file:
            servername_file.write(f"{full_subdomain}.{zone_name}")
    except PermissionError:
        print("Permission error while trying to change the servername. Please ensure the script has the necessary permissions to modify /etc/hostname.")
    except Exception as e:
        print(f"An error occurred while trying to change the servername: {e}")

    # Append the subdomain and current date to the log file
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{full_subdomain},{datetime.now()}\n")

        # Check the Cloudflare DNS records for entries older than the configured hours and delete them
    delete_after_hours = int(config['General']['Delete_After_Hours'])
    if delete_after_hours > 0:
        dns_records = cf.zones.dns_records.get(zone_id)
        for record in dns_records:
            if record['name'].endswith(subdomain_prefix):
                created_on = datetime.strptime(record['created_on'], "%Y-%m-%dT%H:%M:%S.%fZ")
                if datetime.now() - created_on >= timedelta(hours=delete_after_hours):
                    cf.zones.dns_records.delete(zone_id, record['id'])
                    print(f"Deleted subdomain {record['name']} due to exceeding the age limit of {delete_after_hours} hours.")

    # Print out the URL, IP address, and hostname
    print("\n--- Setup Complete ---")
    print(f"Hostname: {full_subdomain}.{zone_name}")
    print(f"IP Address: {public_ip}")
    print(f"https://{full_subdomain}.{zone_name}")

except CloudFlare.exceptions.CloudFlareAPIError:
    print(f"Authentication error. Please check your Cloudflare configuration in {config_file}.")
    print(f"Email: {config['Cloudflare']['Email']}")
    print(f"Zone_ID: {config['Cloudflare']['Zone_ID']}")
    print("Token: Please check that it's correct and has the necessary permissions.")
