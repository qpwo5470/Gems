# Google Gemini Automated Login

This script automates the login process for Google Gemini using Selenium WebDriver.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Update your credentials in `credentials.json`:
   ```json
   {
     "email": "your-email@gmail.com",
     "password": "your-password"
   }
   ```

## Usage

Run the script:
```bash
python google_gems.py
```

## Important Notes

- **Security Challenges**: If Google presents a security challenge (2FA, CAPTCHA, etc.), the script will pause and wait for you to complete it manually in the browser window.

- **ChromeDriver**: The script automatically handles ChromeDriver installation. If you encounter version mismatch errors, the script will download the correct version.

- **Browser Window**: The browser window will remain open after successful login. Press Enter in the terminal to close it.

## Troubleshooting

1. **ChromeDriver Version Mismatch**: The script handles this automatically by downloading the correct version.

2. **Permission Errors**: If you get permission errors, make sure the ChromeDriver is executable:
   ```bash
   chmod +x ~/.wdm/drivers/chromedriver/*/chromedriver-mac-arm64/chromedriver
   ```

3. **Login Fails**: Google may require additional verification for automated logins. Complete any security challenges manually when prompted.

## Files

- `google_gems_login.py` - Main script
- `credentials.json` - Your Google account credentials (keep this secure!)
- `requirements.txt` - Python dependencies