import undetected_chromedriver as uc
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.common.exceptions import NoSuchElementException
from fake_useragent import UserAgent
import json
import time
import random
from time import sleep
from random import randint
from collections import Counter
from datetime import datetime, timedelta
from selenium.webdriver.common.keys import Keys
from io import StringIO # Using StringBuilder from https://appdividend.com/2022/01/21/string-builder-equivalent-in-python/
from datetime import datetime
import requests
import traceback
import subprocess
import os
import glob
from selenium.webdriver.chrome.options import Options

# Get today's date in the format "dd/mm/yyyy"
today = datetime.now()
#today = datetime(2024, 3, 2)
start_date = today - timedelta(days=1)
#start_date = datetime(2024, 7, 31)
end_date = today
#end_date = datetime(2024, 8, 4)



class StringBuilder:
    _file_str = None
    def __init__(self):
        self._file_str = StringIO()
    def Add(self, str):
        self._file_str.write(str)
    def __str__(self):
        return self._file_str.getvalue()

string_builder = StringBuilder()
# Add today's date to the string_builder
string_builder.Add(f"{today.strftime('%Y-%m-%d')} OpenAI API Usage Report\n")

# I send my final json format to n8n, which has access to my company DB
n8n_url = "$YOUR N8N URL$"


# Format dates
start_date_str = start_date.strftime("%d/%m/%Y")
end_date_str = end_date.strftime("%d/%m/%Y")
start_date_path_str = start_date.strftime("%Y-%m-%d")
end_date_path_str = end_date.strftime("%Y-%m-%d")
print(start_date_path_str)
print(end_date_path_str)

# Adjust the file path below to match the location of your JSON file
file_path_activity = r"$YOUR PATH$-{}-{}.json".format(start_date_path_str, end_date_path_str)
file_path_cost = r"$YOUR PATH$-{}-{}.json".format(start_date_path_str, end_date_path_str)


model_costs = {
    "gpt-3.5-turbo": {"context": 0.003, "generated": 0.006},
    "gpt-3.5-turbo-0125": {"context": 0.0005, "generated": 0.0015},
    "gpt-3.5-turbo-0301": {"context": 0.0015, "generated": 0.002},
    "gpt-3.5-turbo-0613": {"context": 0.0015, "generated": 0.002},
    "gpt-3.5-turbo-1106": {"context": 0.001, "generated": 0.002},  
    "gpt-3.5-turbo-16k": {"context": 0.003, "generated": 0.004},
    "gpt-3.5-turbo-16k-0613": {"context": 0.003, "generated": 0.004},
    "gpt-3.5-turbo-instruct": {"context": 0.0015, "generated": 0.002},  
    "gpt-3.5-turbo-instruct-0914": {"context": 0.0015, "generated": 0.002},
    "ft:gpt-3.5-turbo-1106": {"context": 0.001, "generated": 0.002},  
    "ft:gpt-3.5-turbo-0125": {"context": 0.008, "generated": 0.008},
    "gpt-4": {"context": 0.03, "generated": 0.06},
    "gpt-4-turbo-2024-04-09" : {"context": 0.01, "generated": 0.03},
    "gpt-4-0314": {"context": 0.03, "generated": 0.06},
    "gpt-4-0613": {"context": 0.03, "generated": 0.06},
    "gpt-4-32k": {"context": 0.06, "generated": 0.12},
    "gpt-4-32k-0314": {"context": 0.06, "generated": 0.12},
    "gpt-4-32k-0613": {"context": 0.06, "generated": 0.12},
    "gpt-4-1106-preview": {"context": 0.01, "generated": 0.03},
    "gpt-4-0125-preview": {"context": 0.01, "generated": 0.03},  
    "gpt-4-1106-vision-preview": {"context": 0.01, "generated": 0.03},  
    "gpt-4-vision-preview": {"context": 0.01, "generated": 0.03},
    "gpt-4o": {"context": 0.005, "generated": 0.015},
    "gpt-4o-2024-08-06": {"context": 0.0025, "generated": 0.01},
    "gpt-4o-2024-05-13": {"context": 0.005, "generated": 0.015},
    "gpt-4o-mini": {"context": 0.000150, "generated": 0.000600},
    "gpt-4o-mini-2024-07-18": {"context": 0.000150, "generated": 0.000600},
    "babbage": {"context": 0.0016, "generated": 0.0016},  
    "babbage-002": {"context": 0.0016, "generated": 0.0016}, 
    "ft:babbage-002": {"context": 0.0004, "generated": 0.0004},
    "davinci": {"context": 0.012, "generated": 0.012},  
    "davinci-002": {"context": 0.012, "generated": 0.012},
    "ft:davinci-002": {"context": 0.006, "generated": 0.006},
    "text-embedding-3-large": {"context": 0.00013, "generated": 0},  
    "text-embedding-3-small": {"context": 0.00002, "generated": 0},  
    "text-embedding-ada-002": {"context": 0.0001, "generated": 0},  
    "text-embedding-ada-002-v2": {"context": 0.0001, "generated": 0},  
    "whisper-1": {"context": 0.006 / 60, "generated": 0},
    "text-moderation": {"context": 0, "generated": 0}, 
    "dall-e-2-256": {"num_image": 0.016},
    "dall-e-2-512": {"num_image": 0.018},
    "dall-e-2-1024": {"num_image": 0.020},
    "dall-e-3-sd-1024-1024": {"num_image": 0.04},
    "dall-e-3-sd-1024-1792": {"num_image": 0.08},
    "dall-e-3-sd-1792-1024": {"num_image": 0.08},
    "dall-e-3-hd-1024-1024": {"num_image": 0.08}, 
    "dall-e-3-hd-1024-1792": {"num_image": 0.12},
    "dall-e-3-hd-1792-1024": {"num_image": 0.12},
    "assistant_code_interpreter" : {"session": 0.03},
    "vector_store" : {"total_vector_store_bytes": 0, "cost_per_gb_per_day": 0.10},
    "tts-1": {"num_characters": 0.015},
    "tts-1-hd": {"num_characters": 0.030}
}

org_list = {
    "$ORG ID$": "$ORG NAME$",
    "$ORG ID$": "$ORG NAME$",
    "$ORG ID$": "$ORG NAME$"
}

# post result to slack
def post_result():
    slack_webhook_payload = { "channel":"$YOUR CHANNEL$", "message": string_builder }
    slack_webhook_url = '$YOUR API TO SEND SLACK MESSAGE$'
    requests.post(slack_webhook_url, data=slack_webhook_payload).json()
    string_builder.__init__()

def calculate_total_price(data, model_costs):
    user_costs = {}
    org_costs = {}
    missing_models = set()
    skipped_entries = []  # Initialize list to track skipped entries

    for entry in data["data"]:
        if "user" not in entry and "organization_id" not in entry:
            skipped_entries.append(entry)  # Add skipped entry to the list
            continue

        user = entry.get("user", None)
        organization_name = entry.get("organization_name", None)
        model_full = entry.get("model", entry.get("usage_type", ""))
        model_split = model_full.split(":")
        # If there is a ":" in the model name, only get the first two parts for the actual model name
        model = ':'.join(model_split[:2]) if len(model_split) > 2 else model_full
        total_cost = 0

        # Adjust model name for specific dall-e cases
        if "dall-e" in model_full and "image_size" in entry:
            image_size = entry["image_size"]
            if model == "dall-e-2" and image_size == "1024x1024":
                model = "dall-e-2-1024"
            elif model == "dall-e-2" and image_size == "256x256":
                model = "dall-e-2-256"
            elif model == "dall-e-2" and image_size == "512x512":
                model = "dall-e-2-512"
            elif model == "dall-e-3" and image_size == "1024x1024":
                model = "dall-e-3-sd-1024-1024"
            elif model == "dall-e-3" and image_size == "1024x1792":
                model = "dall-e-3-sd-1024-1792"
            elif model == "dall-e-3" and image_size == "1792x1024":
                model = "dall-e-3-sd-1792-1024"



        # Calculate cost for text generation models
        if model in model_costs and "context" in model_costs[model] and "generated" in model_costs[model]:
            n_context_tokens = entry.get("n_context_tokens_total", 0)
            n_generated_tokens = entry.get("n_generated_tokens_total", 0)
            cost_context_per_1000 = model_costs[model]["context"]
            cost_generated_per_1000 = model_costs[model]["generated"]
            total_cost = ((n_context_tokens / 1000) * cost_context_per_1000) + ((n_generated_tokens / 1000) * cost_generated_per_1000)

        # Calculate for tts models based on number of characters (including hd models)
        elif "tts" in model and "num_characters" in entry:
            num_characters = entry.get("num_characters", 0)
            # Use the exact model name if it exists, otherwise default to tts-1
            model_key = model if model in model_costs else "tts-1"
            if model_key in model_costs:
                cost_per_character = model_costs[model_key]["num_characters"]
                total_cost = num_characters * cost_per_character
            else:
                missing_models.add(model)
                continue

        # Calculate cost for assistant models based on sessions
        elif "assistant" in model and "num_sessions" in entry:
            num_sessions = entry.get("num_sessions", 0)
            if model in model_costs:
                session_cost = model_costs.get("assistant_code_interpreter", {}).get("session", 0)
                total_cost = num_sessions * session_cost
            else:
                missing_models.add(model)
                continue

        # Calculate cost for vector store models
        elif "vector_store" in model and "total_vector_store_bytes" in entry:
            total_vector_store_bytes = entry.get("total_vector_store_bytes", 0)
            cost_per_gb_per_day = model_costs.get("vector_store", {}).get("cost_per_gb_per_day", 0)
            free_bytes = 1 * 1024 ** 3  # 1 GB in bytes
            
            if total_vector_store_bytes > free_bytes:
                vector_storage_gb = (total_vector_store_bytes - free_bytes) / (1024 ** 3)  # Convert excess bytes to GB
                total_cost = vector_storage_gb * cost_per_gb_per_day
            else:
                total_cost = 0  # No cost if usage is within the free 1 GB


        # Calculate cost for DALL-E models based on the number of images
        elif "dall-e" in model and "num_image" in model_costs[model]:
            num_images = entry.get("num_images", 0)
            if model in model_costs:
                cost_per_image = model_costs[model]["num_image"]
                total_cost = num_images * cost_per_image
            else:
                missing_models.add(model)
                continue
        else:
            missing_models.add(model)
            continue


        # Update costs
        user_costs[user] = user_costs.get(user, 0) + total_cost
        org_costs[organization_name] = org_costs.get(organization_name, 0) + total_cost
        entry["total_cost"] = round(total_cost, 3)

    
    if skipped_entries:
        print("Skipped entries due to missing 'user' or 'organization_name' or 'organization_id':")
        for skipped_entry in skipped_entries:
            print(json.dumps(skipped_entry, indent=2))
            string_builder.Add(f"Skipped entries due to missing 'user' or 'organization_name' or 'organization_id': {json.dumps(skipped_entry, indent=2)}")
    

    return user_costs, org_costs, missing_models

def gather_misc_info(file_path):
    training_costs = {}
    new_entries = []
 
    # Reading the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
     
    # Filtering for "training" entries and calculating costs
    for entry in data["data"]:
        timestamp = entry.get("timestamp", 0)
        for key, value in entry.items():
            if "training" in key:
                org_id = key.split("(")[-1].strip(")")
                model_name = key.split(" (")[0]
                if org_id not in training_costs:
                    training_costs[org_id] = 0
                training_costs[org_id] += value * 0.01  # Convert cents to dollars
 
                # Preparing new dataset entry
                new_entry = {
                    "timestamp": timestamp,
                    "organization_id": org_id,
                    "organization_name": org_list.get(org_id, "Unknown"),
                    "model": model_name,
                    "total_cost": round(value * 0.01, 3)
                }
                new_entries.append(new_entry)
     
    return training_costs, new_entries
 
# Function to clear the input field by sending backspace keys
def clear_input(element):
    element.click()  # Click the element to set focus
    # Send enough backspace keys to clear the existing value
    for _ in range(10):  # Assuming the date is not longer than 10 characters
        element.send_keys(Keys.BACKSPACE)
 
 
# I put a bunch of sleeps to avoid being detected as a bot
while attempt < max_attempts:
    try:
        # Set up undetected_chromedriver
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(options=options)
 
        # Changing the property of the navigator value for webdriver to undefined
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
 
        # Open the login URL
        login_url = 'https://platform.openai.com/usage'
        driver.get(login_url)
 
        time.sleep(random.uniform(3, 5))
         
        # Wait for the login button and click
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.nav-item[role='button']"))
        )
        login_button.click()
         
        # Wait for the email input field to appear and enter the email address
        email_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
        )
        email_field.send_keys("")
 
        time.sleep(random.uniform(3, 5))
 
        # Wait for the continue button and click
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class='continue-btn']"))
        )
        continue_button.click()
 
        time.sleep(random.uniform(3, 5))
 
        # Wait for the email input field to appear and enter the email address
        password_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )
        password_field.send_keys("")
 
        # Wait for the submit button and click
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-action-button-primary='true']"))
        )
        submit_button.click()
 
        time.sleep(random.uniform(3, 5))
 
        # Wait for the export button and click
        export_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(., 'Export')]]"))
        )
        export_button.click()
 
        time.sleep(random.uniform(3, 5))
 
        # Find the start date input field, clear it, and input today's date
        start_date_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Start date (DD/MM/YYYY)']"))
        )
        clear_input(start_date_field)
        start_date_field.send_keys(start_date_str)
 
        # Find the end date input field, clear it, and input today's date
        end_date_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='End date (DD/MM/YYYY)']"))
        )
        clear_input(end_date_field)
        end_date_field.send_keys(end_date_str)
 
        # Select JSON as the file format from the dropdown
        json_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='JSON']"))
        )
        json_option.click()
 
        time.sleep(random.uniform(3, 5))
 
        # Click on the Export button within the modal
        final_export_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-root .btn.btn-sm.btn-filled.btn-primary"))
        )
        final_export_button.click()
 
        #Wait for the download to complete
        sleep(30)
 
        # Code to click the 'Activity' button
        activity_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Activity')]/ancestor::button"))
        )
        activity_button.click()
 
        time.sleep(random.uniform(3, 5))
 
 
        # Wait for the export button and click
        export_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(., 'Export')]]"))
        )
        export_button.click()
 
        time.sleep(random.uniform(3, 5))
 
        # Find the start date input field, clear it, and input today's date
        start_date_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Start date (DD/MM/YYYY)']"))
        )
        clear_input(start_date_field)
        start_date_field.send_keys(start_date_str)
 
        # Find the end date input field, clear it, and input today's date
        end_date_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='End date (DD/MM/YYYY)']"))
        )
        clear_input(end_date_field)
        end_date_field.send_keys(end_date_str)
 
        # Select JSON as the file format from the dropdown
        json_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='JSON']"))
        )
        json_option.click()
         
        time.sleep(random.uniform(3, 5))
 
        # Click on the Export button within the modal
        final_export_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-root .btn.btn-sm.btn-filled.btn-primary"))
        )
        final_export_button.click()
 
        #Wait for the download to complete
        sleep(10)
 
        driver.quit()
 
        # Assume file_path_activity is defined and points to your JSON file
        # Reading the JSON file and calculating total prices
        with open(file_path_activity, 'r') as file:
            json_data = json.load(file)
 
        user_costs, org_costs, missing_models = calculate_total_price(json_data, model_costs)
 
        # Handle missing models
        if missing_models:
            print("Warning: The following models are not included in the model_costs and were skipped:")
            for model in missing_models:
                print(f"- {model}")
                string_builder.Add(f"Warning: The following models are not included in the model_costs and were skipped: {model}")
 
        # Print total price per user and aggregate total
        print("\n1. User Based")
        total_user_cost = 0
        for user, cost in user_costs.items():
            print(f"{user}|${cost:.2f}")
            total_user_cost += cost
        print(f"Total: ${total_user_cost:.2f}\n")
 
        # Print total price per organization and aggregate total
        print("2. Organization Based")
        total_org_cost = 0
        for organization, cost in org_costs.items():
            print(f"{organization}|${cost:.2f}")
            total_org_cost += cost
        print(f"Total: ${total_org_cost:.2f}")
 
 
        # Modified section to handle new entries
        training_costs, new_entries = gather_misc_info(file_path_cost)
        json_data["data"].extend(new_entries)  # Append new entries to the data
 
        # Save the modified data to a new JSON file
        total_json_path = r"$YOUR PATH$-{}-{}.json".format(start_date_path_str, end_date_path_str)
        with open(total_json_path, 'w') as outfile:
            json.dump(json_data, outfile, indent=2)
 
        print(f"Modified data saved to {total_json_path}")
 
         
        with open(total_json_path, 'r') as file:
            json_data_final = json.load(file)
         
        # Calculate the total sum of 'total_cost' for all entries
        total_cost_sum = sum(entry.get('total_cost', 0) for entry in json_data_final['data'])
 
        # Append this total cost sum to your StringBuilder
        string_builder.Add(f"\nTotal cost for the period {start_date_path_str} to {end_date_path_str}: ${total_cost_sum:.2f}\n")
 
        time.sleep(random.uniform(3, 5))
 
        # Send the JSON data to the specified URL using POST request
        headers = {"Content-Type": "application/json"}
 
        with open(total_json_path, 'r') as file:
            json_payload = file.read()
 
        response = requests.post(n8n_url, headers=headers, data=json_payload)
 
        if response.status_code == 200:
            print("JSON data sent successfully.")
            #post if string_builder is not empty
            if string_builder.__str__() != "":
                post_result()
        else:
            print(f"Failed to send JSON data. Response code: {response.status_code}")
        break
    except Exception as e:  # You can narrow down the exception if you know what specific ones you're handling
        print(f"Attempt {attempt + 1} failed with error: {e}")
        attempt += 1
        if attempt < max_attempts:
            print("Retrying...")
        else:
            print("Max attempts reached, exiting.")
            string_builder.Add(f"Max attempts reached for OpenAI API Usage Report. Error: {e}")
            post_result()
        try:
            driver.quit()
        except:
            pass  # If driver is not initialized or crashed, this prevents an additional error
 
    # A short sleep between retries to avoid hammering too quickly
    sleep(5)
