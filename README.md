# ASU

Setup:

You'll need to pip install various packages (if you can write a requirements file please!)
You'll need to put an .env file similar to .env_example in the root directory.
Finally, make sure OPENAI_API_KEY="..." is either in a local .env file or in .zshrc etc

Install Homebrew (if not already installed)
Install Python via Homebrew: brew install python
Install Selenium: pip3 install selenium
Check python3 version: python3 --version
Check pip3 version: pip3 --version
Check the installed Selenium version: python3 -c "import selenium; print(selenium.__version__)"
 
# database.py - 1
#import redis and zulu
pip3 install redis
pip3 install zulu

# agent.py
#import openai and httpx
pip3 install openai
pip3 install httpx

# database.py - 2
#import mysql.connector and dotenv
pip3 install mysql-connector-python
pip3 install python-dotenv

# main.py
#import undetected_chromedriver
pip3 install undetected-chromedriver

# Issue: urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)
# Solution 1 - prefer to use
Go to Applications > PythonX.Y folder > double click on "Install Certificates.command" file
# Solution 2
1. Install the certifi package if you haven't already: pip install certifi
2. Retrieve the path to the cacert.pem file from the certifi package in your Python script (main.py)
import certifi
import os
# Get the path to the cacert.pem file
cacert_path = certifi.where()
# Optionally, you can print the path
print("Path to cacert.pem:", cacert_path)
# Set the CA certificates path as an environment variable
os.environ['SSL_CERT_FILE'] = cacert_path