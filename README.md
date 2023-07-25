RunPod Cloudflare DDNS
======================

This script sets up a Dynamic DNS (DDNS) using Cloudflare's API for a RunPod. It generates a unique subdomain, sets the IP address to the public IP of the pod, and logs the subdomain and date created. If a log entry is older than a specified number of hours, the subdomain is deleted from both the log file and Cloudflare.

Prerequisites
-------------

*   Python 3.6 or higher
*   A Cloudflare account with a domain set up
*   The `Zone.DNS` permission in Cloudflare for your API token

Setup
-----

1.  Clone this repository to your local machine.
2.  Navigate to the cloned directory.
3.  Create a virtual environment: `python3 -m venv venv`.
4.  Activate the virtual environment: `source venv/bin/activate` (Linux/macOS) or `.\venv\Scripts\activate` (Windows).
5.  Install the required packages: `pip install -r requirements.txt`.
6.  Rename `config.ini.defaults` to `config.ini`.
7.  Open `config.ini` and replace the placeholders with your Cloudflare email, API token, zone ID, and log file path. Set `Delete_After_Hours` to the number of hours after which you want subdomains to be deleted (set to 0 to disable deletion).

Usage
-----

Run the script: `python main.py`