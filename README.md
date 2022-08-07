# Public IP Scraper using Python

This is a python script I have written to get the public IP address from my router.

## Note (Important):

1. This script is written specifically for the model of my router only, and will not work with any other models. Use at your own risk.
2. This script will expose your public IP in Firebase and DuckDNS, anyone with your address of Firebase/DuckDNS can view your public IP and have access to your network.

## Description
The main reason I wrote this script is because the ISP in my country uses NAT and the public IP address for my local network is hidden with another IP address. This is great for security, however, the also prevented me from hosting websites, server or other web applications. VPN is a viable option to solve this issue, but knowledge on setting up VPN was quite limited at that time. Hence, this script will log into my router, scrape the public IP address in the webpage, and upload it into Google Firebase. After the script updates the IP address, it will go into sleep for a set interval.

I have also designed an app using MIT App Inventor, which will allow me to get the public IP address remotely. I have also designed the app to allow the user to tell the script to wake from sleep and updates IP address immediately. 

## Python Libraries

```python
import requests
import pyrebase
```
## Docker Implementation
I also included a Dockerfile, since I wanted to run this script in a Docker in my Raspberry Pi.
```bash
docker build --rm -t script .
docker run --rm -it script
```
