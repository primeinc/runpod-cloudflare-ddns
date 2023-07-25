RunPod Cloudflare DDNS
======================

This script uses the Cloudflare API to create a unique subdomain on your Cloudflare-managed domain and set the IP address to the public IP of the RunPod. It also sets the hostname in `/etc/hostname` to the unique subdomain, and can delete subdomains that are older than a specified number of hours.

Prerequisites
-------------

*   Python 3
*   A Cloudflare account with a managed domain
*   A RunPod with internet access and the ability to run Python scripts

Installation
------------

1. Clone this repository to your local machine or RunPod.

   bash

   ```bash
   git clone https://github.com/primeinc/runpod-cloudflare-ddns.git
   cd runpod-cloudflare-ddns
   ```

2. Set up a Python virtual environment and activate it.

   bash

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Use 'venv\Scripts\activate' on Windows
   ```

3. Install the required Python packages.

   `pip install -r requirements.txt`

Configuration
-------------

1. Rename `config.ini.defaults` to `config.ini`.

   arduino

   ```arduino
   mv config.ini.defaults config.ini
   ```

2. Open `config.ini` in a text editor and fill in your Cloudflare API token, zone ID, and (optional) subdomain prefix.

   ini

   ```ini
   [Cloudflare]
   Token = YOUR_CLOUDFLARE_API_TOKEN
   Zone_ID = YOUR_ZONE_ID
   Debug = false
   Subdomain_Prefix = ddns  # optional
   
   [General]
   Log_File_Path = subdomains.log
   Delete_After_Hours = 48
   ```

Usage
-----

Run the script with Python 3.

css

```css
python main.py
```

The script will:

*   Generate a unique subdomain by concatenating a random adjective and animal, optionally prefixed with a subdomain from your config file.
*   Check if the subdomain exists in your Cloudflare DNS records. If it does, it will generate a new one.
*   Get your public IP address using the ipify API.
*   Create a new A record in your Cloudflare DNS with the subdomain and your public IP.
*   Set the hostname in `/etc/hostname` to the full subdomain.
*   Write the full subdomain and the current date and time to the log file.
*   Check your Cloudflare DNS records for entries that are older than the number of hours specified in your config file, and delete them.

When the script completes, it will print the hostname, IP address, and a URL to the console.

Warning
-----
  This script will automatically delete DNS records in your Cloudflare zone that are older than the number of hours specified in your configuration file. To avoid accidentally deleting important records, it is recommended to use a unique subdomain prefix.

Notes
-----

*   The script requires the Cloudflare API token to have the `Zone.DNS:Edit` permission.
*   The script must be run with sufficient permissions to write to `/etc/hostname` and the log file specified in your config file.
*   If the optional subdomain prefix is specified in your config file, the script will append it to the unique subdomain when creating the DNS record and setting the hostname.
*   Don't forget to deactivate the virtual environment when you're done by running `deactivate` in your terminal.
