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
chrome_driver_path = r"YOUR_CHROMEDRIVER_PATH_HERE"  # <-- REPLACE with your ChromeDriver path
# Setting up Selenium
chrome_options = Options()
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 1. Navigate to Amazon homepage
print("Navigating to Amazon homepage...")
driver.get("https://www.amazon.com")
check_for_captcha()

# 2. Hover over the Sign-In dropdown
print("Hovering over the Sign-In dropdown...")
hover_element = driver.find_element(By.ID, "nav-link-accountList-nav-line-1")
ActionChains(driver).move_to_element(hover_element).perform()
time.sleep(2)
check_for_captcha()

# 3. Click on Sign In
print("Clicking on Sign In...")
driver.find_element(By.XPATH, "//span[text()='Sign in']").click()
check_for_captcha()

# 4. Enter Email & Continue
print("Entering email and proceeding...")
driver.find_element(By.ID, "ap_email").send_keys("YOUR_EMAIL_HERE")  # <-- REPLACE with your Amazon email
driver.find_element(By.ID, "continue").click()
time.sleep(2)
check_for_captcha()

# 5. Enter Password & Sign In
print("Entering password and signing in...")
driver.find_element(By.ID, "ap_password").send_keys("YOUR_PASSWORD_HERE")  # <-- REPLACE with your Amazon passworddriver.find_element(By.ID, "signInSubmit").click()
check_for_captcha()

# 6. Handle manual CAPTCHA & 2FA
try:
    signInButton = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "signInSubmit")))
    signInButton.click()
    print("Sign In button clicked.")
except:
    print("Failed to click the Sign In button.")

# Load your spreadsheet
print("Loading the spreadsheet...")
df = pd.read_excel('YOUR_SPREADSHEET_PATH_HERE')  # <-- REPLACE with the path to your spreadsheet

# Loop through each product in the spreadsheet
print("Iterating through products in the spreadsheet...")
for index, row in df.iterrows():
    product_name = row['Product Name']
    print(f"Processing product: {product_name}")

    # Navigate to 'Your Orders' page
    print("Navigating to 'Your Orders' page...")
    driver.get("https://www.amazon.com/gp/css/homepage.html?ref_=abn_bnav_youraccount_btn")
    account_for_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "abnav-accountfor"))
    )
    account_for_link.click()

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

       # Initialize a list to store paths of saved images for this product
        saved_image_paths = []

    try:
        image_block = driver.find_element(By.ID, 'imageBlock')
        image_block_images = image_block.find_elements(By.TAG_NAME, 'img')

        for idx, img in enumerate(image_block_images + aplus_batch_images):
            img_url = img.get_attribute('data-old-hires') or img.get_attribute('src')
            response = requests.get(img_url, stream=True)
            file_name = f"{product_name}_image_{idx}.jpg".replace(" ", "_")
            file_path = os.path.join(save_directory, file_name)
            with open(file_path, 'wb') as out_file:
                out_file.write(response.content)
            saved_image_paths.append(file_path)
            print(f"Image {idx+1} saved successfully.")
         
        # Update the DataFrame with extracted images
        image_paths_str = ', '.join(saved_image_paths)
        df.at[index, 'Product Images'] = image_paths_str
        print("Product images updated successfully.")

        # Save the updated DataFrame
        updated_spreadsheet_path = f'updated_{original_file_name}_partial.xlsx'
        df.to_excel(updated_spreadsheet_path, index=False)
        print(f"Updated spreadsheet saved at: {updated_spreadsheet_path}")
    except Exception as e:
        print(f"Failed to extract and save images. Error: {e}")        

       # Extract and save text from aplusBatch and featurebullets containers
    try:
        # ... (code to extract and save text)
        product_description = aplus_batch_text + '\n' + featurebullets_text
        df.at[index, 'Description'] = product_description
        print("Product description extracted successfully.")
        
        # Update the DataFrame with extracted details
        df.at[index, 'Product Images'] = ', '.join(saved_image_paths)
        print("Product images updated successfully.")

        # Save the updated DataFrame
        updated_spreadsheet_path = f'updated_{original_file_name}_final.xlsx'
        df.to_excel(updated_spreadsheet_path, index=False)
        print(f"Updated spreadsheet saved at: {updated_spreadsheet_path}")
        
    except Exception as e:
        print(f"Failed to extract and save details. Error: {e}")

    # Save the updated dataframe
    updated_spreadsheet_path = 'YOUR_UPDATED_SPREADSHEET_PATH_HERE'  # <-- REPLACE with where you want to save the updated spreadsheet
    df.to_excel(updated_spreadsheet_path, index=False)
    print(f"\nCompleted processing all products. Updated spreadsheet saved at: {updated_spreadsheet_path}")

    
    # Navigate to 'Your Orders' page
    print("Navigating to 'Your Orders' page...")
    driver.find_element(By.ID, "nav-link-yourAccount").click()
    
    # Wait for the "Your Orders" link to be clickable
    try:
        your_orders_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='order-history']"))
        )
        your_orders_link.click()
    except Exception as e:
        print(f"Failed to click 'Your Orders' link. Error: {e}")
        continue
    
    time.sleep(2)  # Wait for the page to load

    
# Don't forget to close the driver when done
driver.quit()
