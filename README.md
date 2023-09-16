**Step-by-Step Guide to Set Up and Run the Code**

**Setting Up Your Computer**

Installing Python:
Visit https://www.python.org/downloads/windows/
Download the latest version for Windows.
Open the downloaded file and install Python. Make sure to check the box that says "Add Python to PATH" during installation.
Installing Google Chrome:

If you don’t have Google Chrome installed, you can download it here https://www.google.com/chrome/
Installing Chocolatey & ChromeDriver:

First, we need to install Chocolatey, a package manager for Windows.
Open the Windows Command Prompt as an administrator.
Copy and paste this command and hit Enter:

	@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile - InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((Invoke-WebRequest - Uri 'https://chocolatey.org/install.ps1').Content)"

Wait for it to install.
Install ChromeDriver using Chocolatey:
In the same Command Prompt, type: choco install chromedriver
Wait for it to install.

**Setting Up Your Python Environment**

Installing Necessary Libraries:
Open the Command Prompt.
Install the required Python libraries by typing the following commands and pressing Enter after each:
	
 	pip install selenium 
	pip install pandas 
	pip install requests

**Preparing the Code**

Copy the provided Python code.
Open a text editor like Notepad.
Paste the code into this Notepad.
Save the file with a .py extension, for instance, amazon_script.py.

** Modifying the Code for Your Use**

Open the saved amazon_script.py in Notepad or any text editor.
Locate YOUR_CHROMEDRIVER_PATH_HERE in the code. Replace it with the path where ChromeDriver is installed. If you used the Chocolatey method above, the path would typically be C:\ProgramData\chocolatey\bin\chromedriver.exe.
Find YOUR_EMAIL_HERE and replace it with your Amazon email address.
Replace YOUR_PASSWORD_HERE with your Amazon password.
Replace YOUR_SPREADSHEET_PATH_HERE with the path to your desired spreadsheet on your computer.

Finally, update YOUR_UPDATED_SPREADSHEET_PATH_HERE with the path where you'd like to save the updated spreadsheet after the script runs.

**Running the Code**

Open the Command Prompt.
Navigate to the directory where you saved amazon_script.py using the cd command. For example: cd C:\path\to\your\directory
Type python amazon_script.py and press Enter.
The script will start running. Follow any on-screen instructions, especially when prompted to handle CAPTCHAs or 2FA.

**After Running**

Once the script has finished, it will have updated your spreadsheet with details from your Amazon orders.
You can now use this spreadsheet for your WooCommerce uploads or for any other purpose.
Remember, always ensure your credentials are secure and never share the script with personal details embedded in it.

