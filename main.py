from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd
import requests
import os
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.drawing.image import Image

# Function to check for CAPTCHA and pause if detected
print("Script starting...")
print("Checking for CAPTCHA...")

def check_for_captcha():
    captcha_elements = driver.find_elements(By.XPATH, "//input[contains(@id, 'capt')]")
    if captcha_elements:
        input("CAPTCHA detected! Please solve the CAPTCHA and press Enter to continue...")
print("Checking for 2FA...")

def handle_2fa():
    # Wait for a short duration to see if the 2FA page loads
    time.sleep(3)
    # Check if the 2FA element is present
    two_fa_elements = driver.find_elements(By.ID, "twoFactorAuth")
    if two_fa_elements:
        print("2FA detected!")
        input("Please complete the 2FA step and then press Enter to continue...")

# Set ChromeDriver path
chrome_driver_path = r"YOUR_CHROMEDRIVER_PATH_HERE"

# Setting up Selenium
chrome_options = Options()
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Image save directory
IMAGE_SAVE_DIRECTORY = r"YOUR_IMAGE_OUTPUT_PATH/SAVE_DIRECTORY_PATH_HERE"
if not os.path.exists(IMAGE_SAVE_DIRECTORY):
    os.makedirs(IMAGE_SAVE_DIRECTORY)

# Spreadsheet paths
ORIGINAL_SPREADSHEET_PATH = r"YOUT_INPUT_SPREADSHEET_PATH_HERE"
ORIGINAL_SPREADSHEET_NAME = os.path.basename(ORIGINAL_SPREADSHEET_PATH).replace('.xlsx', '')

CHECKPOINT_FILE = 'last_processed_product.txt'

# Load the last checkpoint if it exists
last_processed_product = None
if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, 'r') as f:
        last_processed_product = f.readline().strip()

# 1. Navigate to Amazon homepage
print("Navigating to Amazon homepage...")
driver.get("https://www.amazon.com")
check_for_captcha()

# 2. Hover over the Sign-In dropdown
print("Hovering over the Sign-In dropdown...")
hover_element = driver.find_element(By.ID, "nav-link-accountList-nav-line-1")
ActionChains(driver).move_to_element(hover_element).perform()
time.sleep(5)
check_for_captcha()

# 3. Click on Sign In
print("Clicking on Sign In...")
driver.find_element(By.XPATH, "//span[text()='Sign in']").click()
check_for_captcha()

# 4. Enter Email & Continue
print("Entering email and proceeding...")
driver.find_element(By.ID, "ap_email").send_keys("YOUR_EMAIL/YOUR_USERNAME_HERE")
driver.find_element(By.ID, "continue").click()
time.sleep(5)
check_for_captcha()

# 5. Enter Password & Sign In
print("Entering password and signing in...")
driver.find_element(By.ID, "ap_password").send_keys("YOUR_LOGIN_PASSWORD_HERE")
time.sleep(5)
check_for_captcha()

# 6. Handle manual CAPTCHA & 2FA
try:
    signInButton = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "signInSubmit")))
    signInButton.click()
    print("Sign In button clicked.")
except:
    print("Failed to click the Sign In button.")

save_directory = r"YOUR_OUTPUT_PATH/SAVE_DIRECTORY_HERE"
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Load the spreadsheet
print("Loading the spreadsheet...")
original_file_path = r"YOUR_INPUT_SPREADSHEET_PATH_HERE"
original_file_name = os.path.basename(original_file_path)
df = pd.read_excel(original_file_path)

# Before the loop
if 'Product Images' not in df.columns:
    df['Product Images'] = ""

if 'Product Description' not in df.columns:
    df['Product Description'] = ""

# Ensure the data type for these columns is string to avoid conflicts when updating them
df['Product Images'] = df['Product Images'].astype(str)
df['Product Description'] = df['Product Description'].astype(str)

# Create a directory to store images if it doesn't exist
save_directory = "Product Images"
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Load checkpoint
start_index = 0
if os.path.exists("checkpoint.txt"):
    with open("checkpoint.txt", "r") as file:
        start_index = int(file.read().strip())

# Loop through each product in the spreadsheet
print("Iterating through products in the spreadsheet...")
for index, row in df.iterrows():
    if index < start_index:
        continue  # Skip products we've already processed

    product_name = row['Product Name']
    print(f"Processing product: {product_name}")

    # Navigate to 'Your Orders' page
    print("Navigating to 'Your Orders' page...")
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            driver.get("https://www.amazon.com/gp/css/homepage.html?ref_=abn_bnav_youraccount_btn")
            account_for_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "abnav-accountfor"))
            )
            account_for_link.click()
            break  # Break out of the loop if successful
        except Exception as e:
            print(f"Attempt {retry_count + 1}: Failed to navigate to 'Your Orders'. Trying again...")
            retry_count += 1
            time.sleep(5)  # Wait for 5 seconds before retrying

    # Click on 'Your Orders' link
    your_orders_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//h2[contains(text(), 'Your Orders')]"))
    )
    your_orders_link.click()

    # Search for the product using the search bar
    try:
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchOrdersInput"))
        )
        search_input.clear()
        search_input.send_keys(product_name)
        search_button = driver.find_element(
            By.CSS_SELECTOR, "input.a-button-input[aria-labelledby='a-autoid-3-announce']"
        )
        search_button.click()
    except Exception as e:
        print(f"Failed to search for product. Error: {e}")

    # Click on the product link
    try:
        product_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//a[contains(text(), '{product_name}')]"))
        )
        product_link.click()
    except Exception as e:
        print(f"Couldn't find product listing for: {product_name}. Error: {e}")

    # Image Extraction
    image_blocks = ["imageBlock", "aplusBatch_feature_div"]
    saved_image_paths = []

    for block in image_blocks:
        try:
            image_container = driver.find_element(By.ID, block)
            images = image_container.find_elements(By.TAG_NAME, 'img')

            for idx, img in enumerate(images):
                img_url = img.get_attribute('data-old-hires') or img.get_attribute('src')

                # Only save images that have a valid URL
                if img_url:
                    response = requests.get(img_url, stream=True)
                    file_name = f"{product_name}_image_{idx}.jpg".replace(" ", "_")
                    file_path = os.path.join(save_directory, file_name)
                    with open(file_path, 'wb') as out_file:
                        out_file.write(response.content)
                    saved_image_paths.append(file_path)
                    print(f"Image {idx+1} saved successfully for {block}.")

        except Exception as e:
            print(f"Failed to extract and save images from {block}. Error: {e}")

    # Insert the image paths into the "Product Images" column of the spreadsheet
    image_paths_str = ', '.join(saved_image_paths)
    df.at[index, 'Product Images'] = image_paths_str
    print("Product images updated successfully.")

    # Save the spreadsheet after image extraction
    partial_spreadsheet_path = os.path.join(os.path.dirname(ORIGINAL_SPREADSHEET_PATH), ORIGINAL_SPREADSHEET_NAME + '_updated_partial_images.xlsx')
    df.to_excel(partial_spreadsheet_path, index=False)
    if os.path.exists(partial_spreadsheet_path):
        print(f"Spreadsheet saved after text extraction at: {partial_spreadsheet_path}")
    else:
        print(f"Spreadsheet {partial_spreadsheet_path} does NOT exist!")

    # Text Extraction
    text_blocks = ["aplusBatch_feature_div", "featurebullets_feature_div"]
    product_description_parts = []

    for block in text_blocks:
        try:
            text_container = driver.find_element(By.ID, block)

            # For the aplusBatch, get text from ul and p elements
            if block == "aplusBatch_feature_div":
                ul_texts = text_container.find_elements(By.TAG_NAME, 'ul')
                p_texts = text_container.find_elements(By.TAG_NAME, 'p')

                for ul in ul_texts:
                    product_description_parts.append(ul.text)

                for p in p_texts:
                    product_description_parts.append(p.text)

            # For the featurebullets, get text directly
            else:
                product_description_parts.append(text_container.text)

        except Exception as e:
            print(f"Failed to extract text from {block}. Error: {e}")

    # Extracting item details like weight, brand, dimensions, etc.
    try:
        detail_table = driver.find_element(By.CSS_SELECTOR, "div.a-section table.a-normal")
        rows = detail_table.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, 'td')
            if len(columns) == 2:
                label = columns[0].text.strip()
                value = columns[1].text.strip()
                product_description_parts.append(f"{label}: {value}")
    except Exception as e:
        print(f"Failed to extract additional product details. Error: {e}")

    # Combine the extracted texts to form the product description
    product_description = '\n'.join(product_description_parts)

    # Insert the text into the "Product Description" column of the spreadsheet
    df.at[index, 'Product Description'] = product_description
    print("Product description updated successfully.")

    # Save the spreadsheet after text extraction
    partial_spreadsheet_path = os.path.join(os.path.dirname(ORIGINAL_SPREADSHEET_PATH), ORIGINAL_SPREADSHEET_NAME + '_updated_partial_text.xlsx')
    df.to_excel(partial_spreadsheet_path, index=False)
    if os.path.exists(partial_spreadsheet_path):
        print(f"Spreadsheet saved after text extraction at: {partial_spreadsheet_path}")
    else:
        print(f"Spreadsheet {partial_spreadsheet_path} does NOT exist!")

    # Navigate back to "Your Orders"
    try:
        # Hover over "Hello, Alysha"
        hover_element = driver.find_element(By.XPATH, "//span[text()='Hello, YOUR_ACCOUNT_NAME_HERE']")
        ActionChains(driver).move_to_element(hover_element).perform()
        time.sleep(2)

        # Click on "Your Orders"
        your_orders_element = driver.find_element(By.XPATH, "//span[text()='Your Orders']")
        your_orders_element.click()
        time.sleep(2)
    except Exception as e:
        print(f"Failed to navigate back to 'Your Orders'. Error: {e}")

    with open(CHECKPOINT_FILE, 'w') as f:
        f.write(product_name)

# After all the products have been processed, save the final spreadsheet
final_spreadsheet_path = os.path.join(os.path.dirname(ORIGINAL_SPREADSHEET_PATH), ORIGINAL_SPREADSHEET_NAME + '_updated_final.xlsx')
df.to_excel(final_spreadsheet_path, index=False)

# Don't forget to close the driver when done
driver.quit()

print("Script completed successfully!")
