from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import os
import urllib.parse
import base64
import threading
import random
import platform
from gemini_parser import GeminiParser
from receipt_printer import ReceiptPrinter

def load_credentials(filepath='credentials.json'):
    with open(filepath, 'r') as file:
        return json.load(file)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Add options for better Windows compatibility
    if platform.system() == 'Windows':
        chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-software-rasterizer')
    
    # Force fullscreen mode
    chrome_options.add_argument('--start-maximized')  # Start maximized
    if platform.system() == 'Windows':
        chrome_options.add_argument('--kiosk')  # Kiosk mode for Windows fullscreen
    else:
        chrome_options.add_argument('--start-fullscreen')  # Fullscreen for other OS
    
    # Use a persistent user data directory to maintain login state
    current_dir = os.path.dirname(os.path.abspath(__file__))
    user_data_dir = os.path.join(current_dir, 'chrome_user_data')
    
    # Create the directory if it doesn't exist
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
        print(f"Created Chrome user data directory: {user_data_dir}")
    else:
        print(f"Using existing Chrome user data directory: {user_data_dir}")
    
    # Set Chrome to use this user data directory
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    
    # Optionally use a specific profile (default is 'Default')
    # chrome_options.add_argument('--profile-directory=Profile 1')
    
    # Start maximized (works on all platforms)
    chrome_options.add_argument('--start-maximized')
    
    # For macOS, also use kiosk mode for true fullscreen
    # import platform
    # if platform.system() == 'Darwin':  # macOS
    #     chrome_options.add_argument('--kiosk')
    
    # Always use webdriver-manager to ensure compatibility
    print("Downloading/verifying compatible ChromeDriver...")
    try:
        driver_path = ChromeDriverManager().install()
        print(f"ChromeDriver installed at: {driver_path}")
        
        # Fix the path if it's pointing to the wrong file
        if driver_path.endswith('THIRD_PARTY_NOTICES.chromedriver'):
            driver_path = driver_path.replace('THIRD_PARTY_NOTICES.chromedriver', 'chromedriver')
        
        # On Windows, check for .exe extension
        if platform.system() == 'Windows':
            if not driver_path.endswith('.exe'):
                # Check if .exe version exists
                exe_path = driver_path + '.exe'
                if os.path.exists(exe_path):
                    driver_path = exe_path
                else:
                    # Look for chromedriver.exe in the same directory
                    driver_dir = os.path.dirname(driver_path)
                    exe_in_dir = os.path.join(driver_dir, 'chromedriver.exe')
                    if os.path.exists(exe_in_dir):
                        driver_path = exe_in_dir
        
        print(f"Using ChromeDriver: {driver_path}")
        
        # Make sure the chromedriver has execute permissions (not needed on Windows)
        if platform.system() != 'Windows':
            import subprocess
            try:
                subprocess.run(['chmod', '+x', driver_path], check=True)
                print(f"Fixed permissions for: {driver_path}")
            except Exception as e:
                print(f"Warning: Could not fix permissions: {e}")
        
        service = Service(driver_path)
        
    except Exception as e:
        print(f"Error with ChromeDriverManager: {e}")
        print("Trying alternative approach...")
        # Try without specifying executable path
        service = Service()
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Failed to create Chrome driver: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure Google Chrome is installed")
        print("2. Try updating webdriver-manager: pip install --upgrade webdriver-manager")
        print("3. Or download ChromeDriver manually from: https://chromedriver.chromium.org/")
        raise
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Ensure fullscreen/maximized window
    print("Setting window to fullscreen/maximized...")
    try:
        if platform.system() == 'Windows':
            # On Windows, kiosk mode is already set via Chrome options
            # Don't try to maximize again as it conflicts with kiosk mode
            print("Using kiosk mode on Windows")
        else:
            # For other OS, try fullscreen
            driver.fullscreen_window()
    except Exception as e:
        print(f"Note: Could not set fullscreen: {e}")
        # Continue anyway
    
    return driver

def login_to_google_gems(driver, credentials=None):
    try:
        # Simply navigate to the sign-in page with Gemini as the continue URL
        # Google will automatically skip login if already authenticated
        print("Navigating to Google sign-in...")
        driver.get('https://accounts.google.com/v3/signin/identifier?continue=https://gemini.google.com/&hl=en&theme=glif&flowName=GlifWebSignIn&flowEntry=ServiceLogin')
        
        # Wait a moment to see where we end up
        time.sleep(3)
        
        # Check if we were automatically redirected to Gemini (already logged in)
        current_url = driver.current_url
        if current_url.startswith("https://gemini.google.com/") and "accounts.google.com" not in current_url:
            print("✅ Already logged in! Redirected to Gemini automatically")
            # Wait for the interface to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "main"))
                )
            except:
                pass
            return
        
        # If we're still on the login page, proceed with login
        print("Login required, proceeding...")
        
        if credentials:
            # Try automated login if credentials provided
            try:
                # Wait for and enter email
                print("Attempting automated login...")
                email_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "identifierId"))
                )
                email_input.clear()
                email_input.send_keys(credentials['email'])
                
                # Click next button
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "identifierNext"))
                )
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
                
                # Wait for password page to load
                time.sleep(3)
                
                # Try to enter password
                password_selectors = [
                    (By.NAME, "Passwd"),
                    (By.NAME, "password"),
                    (By.CSS_SELECTOR, "input[type='password']"),
                    (By.XPATH, "//input[@type='password']")
                ]
                
                password_entered = False
                for selector_type, selector_value in password_selectors:
                    try:
                        password_input = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((selector_type, selector_value))
                        )
                        time.sleep(1)  # Wait for field to be ready
                        password_input.clear()
                        password_input.send_keys(credentials['password'])
                        
                        # Try to find and click next button
                        try:
                            password_next = driver.find_element(By.ID, "passwordNext")
                            driver.execute_script("arguments[0].click();", password_next)
                            print("Password entered and next button clicked")
                        except:
                            # If no button found, press Enter
                            password_input.send_keys("\n")
                            print("Password entered and Enter pressed")
                        
                        password_entered = True
                        break
                    except:
                        continue
                
                if password_entered:
                    # Wait a bit for the page to load
                    time.sleep(10)
                    
                    # Check multiple times for passkey page
                    for attempt in range(10):
                        time.sleep(2)
                        
                        # Handle passkey enrollment page if it appears
                        try:
                            # Check if we're on the passkey enrollment page
                            if "passkeyenrollment" in driver.current_url or "speedbump/passkeyenrollment" in driver.current_url:
                                print(f"Passkey enrollment page detected (attempt {attempt + 1}/3)...")
                                
                                # Try multiple selectors for the "Not now" button
                                not_now_selectors = [
                                    "//button[.//span[text()='Not now']]",
                                    "//button[contains(@class, 'VfPpkd-LgbsSe') and .//span[text()='Not now']]",
                                    "//div[@jsname='QkNstf']//button",
                                    "//button[@jsname='LgbsSe' and contains(., 'Not now')]",
                                    "//button[contains(@class, 'ksBjEc')]"
                                ]
                                
                                clicked = False
                                for selector in not_now_selectors:
                                    try:
                                        not_now_button = WebDriverWait(driver, 3).until(
                                            EC.element_to_be_clickable((By.XPATH, selector))
                                        )
                                        print(f"Found 'Not now' button with selector: {selector}")
                                        driver.execute_script("arguments[0].click();", not_now_button)
                                        print("Clicked 'Not now' button")
                                        clicked = True
                                        time.sleep(3)
                                        break
                                    except:
                                        continue
                                
                                if not clicked:
                                    print("Could not find 'Not now' button automatically")
                                    print("Please click 'Not now' or 'Continue' manually")
                                    
                                # Exit the attempt loop if we found the passkey page
                                break
                                
                        except Exception as e:
                            print(f"Error handling passkey page: {e}")
                            pass
                    
                    if driver.current_url.startswith("https://gemini.google.com"):
                        print("Automated login successful!")
                        return  # Skip the manual login wait
            except Exception as e:
                print(f"Automated login failed: {e}")
                print("Please complete the login manually...")
        
        # Wait indefinitely for user to complete login
        print("\n" + "="*60)
        print("🔐 Please complete the Google login process in the browser")
        print("The script will wait indefinitely until you reach Gemini...")
        print("="*60 + "\n")
        
        # Check every 2 seconds if we've reached Gemini
        while True:
            try:
                current_url = driver.current_url
                # Make sure we're actually on gemini.google.com, not just a URL with it as a parameter
                if current_url.startswith("https://gemini.google.com"):
                    print("\n✅ Login successful! Now on Gemini page")
                    break
                elif "accounts.google.com" in current_url:
                    # Check if we're on the passkey enrollment page
                    try:
                        # Look for the passkey enrollment elements
                        passkey_heading = driver.find_element(By.XPATH, "//h1[contains(text(), 'Simplify your sign-in')]")
                        not_now_button = driver.find_element(By.XPATH, "//button[.//span[text()='Not now']]")
                        if passkey_heading and not_now_button:
                            print("\n⚠️  Passkey enrollment page detected!")
                            print("Click 'Not now' to skip or 'Continue' to set up passkey")
                    except:
                        # Not on passkey page, just regular login
                        pass
                time.sleep(2)
            except:
                time.sleep(2)
                continue
        
        # Wait for the main interface to load
        print("Waiting for Google Gemini interface to load...")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
        except:
            print("Could not find main element, but continuing anyway...")
        
        print("✅ Successfully logged in to Google Gemini!")
        print(f"Current URL: {driver.current_url}")
        
        # Additional wait to ensure all content is loaded
        print("Waiting for page content to fully load...")
        time.sleep(5)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(f"Current URL: {driver.current_url}")
        raise

def close_sidebar_menu(driver):
    """Hide the sidebar and other UI elements after opening a gem"""
    try:
        # Execute all hiding operations in a single JavaScript call for speed
        hide_script = """
        // First, inject CSS to hide elements before they render
        const style = document.createElement('style');
        style.textContent = `
            /* Hide elements before they render */
            bard-sidenav,
            .cdk-overlay-pane,
            [data-test-id="chat-app"],
            .boqOnegoogleliteOgbOneGoogleBar,
            #gb,
            top-bar-actions,
            .bot-recent-chats,
            .uploader-button-container,
            toolbox-drawer,
            .mic-button-container,
            .response-container-footer,
            hallucination-disclaimer,
            .hallucination-disclaimer,
            .capabilities-disclaimer,
            [data-test-id="highly-regulated-disclaimer"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
            }
            
            /* Add bottom padding to input area */
            .input-area-container,
            [class*="input-area"],
            .query-input-container,
            [class*="query-input"],
            .composer-container,
            [class*="composer"] {
                padding-bottom: 40px !important;
            }
            
            /* Specific rule for recent chats that may load later */
            .bot-recent-chats,
            [class*="recent-chats"],
            [class*="recent"][class*="chat"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
            }
        `;
        document.head.appendChild(style);
        console.log('CSS injection complete - elements will be hidden before rendering');
        
        // Also hide existing elements immediately
        const elementsToHide = [
            'bard-sidenav',                    // Sidebar
            '.cdk-overlay-pane',               // Snackbar notification
            '[data-test-id="chat-app"]',       // Menu button area
            '.boqOnegoogleliteOgbOneGoogleBar', // Google account bar
            '#gb',                             // Alternative Google bar
            'top-bar-actions',                 // Top bar actions (upgrade button)
            '.bot-recent-chats',               // Recent chats panel
            '.uploader-button-container',      // + (Add file) button
            'toolbox-drawer',                  // Canvas button
            '.mic-button-container',           // Microphone button
            'hallucination-disclaimer',        // Hallucination disclaimer
            '.hallucination-disclaimer',
            '.capabilities-disclaimer',
            '[data-test-id="highly-regulated-disclaimer"]'
        ];
        
        elementsToHide.forEach(selector => {
            try {
                let elements;
                if (selector.startsWith('.')) {
                    elements = document.getElementsByClassName(selector.substring(1));
                } else if (selector.startsWith('#')) {
                    elements = [document.getElementById(selector.substring(1))];
                } else if (selector.startsWith('[')) {
                    elements = document.querySelectorAll(selector);
                } else {
                    elements = document.getElementsByTagName(selector);
                }
                
                for (let elem of elements) {
                    if (elem) elem.style.display = 'none';
                }
            } catch (e) {
                // Silently ignore if element not found
            }
        });
        
        console.log('Existing UI elements hidden');
        
        // Add bottom padding to input area to compensate for removed disclaimer
        const inputAreaSelectors = [
            '.input-area-container',
            '[class*="input-area"]',
            '.query-input-container',
            '[class*="query-input"]',
            '.composer-container',
            '[class*="composer"]'
        ];
        
        for (const selector of inputAreaSelectors) {
            try {
                const containers = document.querySelectorAll(selector);
                containers.forEach(container => {
                    if (container) {
                        container.style.paddingBottom = '40px';
                        console.log('Added bottom padding to:', selector);
                    }
                });
            } catch (e) {}
        }
        
        // Set up MutationObserver to hide response footers and delayed elements in real-time
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        // Check if this is a response footer or contains one
                        if (node.classList && node.classList.contains('response-container-footer')) {
                            node.style.display = 'none';
                        } else if (node.querySelectorAll) {
                            const footers = node.querySelectorAll('.response-container-footer');
                            footers.forEach(footer => {
                                footer.style.display = 'none';
                            });
                        }
                        
                        // Check for recent chats panel (최근)
                        if (node.classList && node.classList.contains('bot-recent-chats')) {
                            node.style.display = 'none';
                            console.log('Hidden delayed recent chats panel');
                        } else if (node.querySelectorAll) {
                            const recentChats = node.querySelectorAll('.bot-recent-chats');
                            recentChats.forEach(recent => {
                                recent.style.display = 'none';
                                console.log('Hidden delayed recent chats panel');
                            });
                        }
                        
                        // Also check if the node contains text '최근'
                        if (node.textContent && node.textContent.includes('최근')) {
                            // Check if it's part of the recent chats UI
                            const parent = node.closest('.bot-recent-chats') || node.closest('[class*="recent"]');
                            if (parent) {
                                parent.style.display = 'none';
                                console.log('Hidden element containing 최근');
                            }
                        }
                    }
                });
            });
            
            // Also hide any existing footers and recent panels that might have appeared
            const existingFooters = document.querySelectorAll('.response-container-footer');
            existingFooters.forEach(footer => {
                footer.style.display = 'none';
            });
            
            const existingRecent = document.querySelectorAll('.bot-recent-chats');
            existingRecent.forEach(recent => {
                recent.style.display = 'none';
            });
        });
        
        // Start observing the entire document for changes
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('MutationObserver set up for response footers and delayed elements');
        
        // Periodic check for delayed elements (최근 panel)
        setInterval(() => {
            const recentPanels = document.querySelectorAll('.bot-recent-chats');
            recentPanels.forEach(panel => {
                if (panel.style.display !== 'none') {
                    panel.style.display = 'none';
                    console.log('Hidden recent panel in periodic check');
                }
            });
            
            // Also check for any element containing '최근' text in the sidebar area
            const sidebarElements = document.querySelectorAll('[class*="sidenav"] *');
            sidebarElements.forEach(elem => {
                if (elem.textContent && elem.textContent.includes('최근') && 
                    (elem.classList.contains('bot-recent-chats') || elem.closest('.bot-recent-chats'))) {
                    const targetElement = elem.closest('.bot-recent-chats') || elem;
                    if (targetElement.style.display !== 'none') {
                        targetElement.style.display = 'none';
                        console.log('Hidden 최근 element in periodic check');
                    }
                }
            });
        }, 1000); // Check every second
        """
        
        driver.execute_script(hide_script)
        print("UI elements hidden and real-time hiding enabled with periodic checks")
            
    except Exception as e:
        print(f"Error hiding UI elements: {str(e)}")

def monitor_chat_and_add_print_button(driver):
    """Monitor chat for 'Gems Station' keyword and add print button when detected"""
    try:
        # Get the absolute path to the print button image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print_btn_path = os.path.join(current_dir, "res", "GEMS_print_btn.png")
        transition_path = os.path.join(current_dir, "transition_screen.html")
        
        # Convert to base64 for inline embedding
        with open(print_btn_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        monitor_script = f"""
        // Create global flags
        window.gemsConversationEnded = false;
        window.printButtonClicked = false;
        window.exitCommand = false;
        window.testCommand = false;
        
        // Function to check if text contains "Gems Station"
        function containsGemsStation(text) {{
            return text && text.includes("Gems Station");
        }}
        
        // Function to disable input and add print button
        function endConversationAndAddPrintButton() {{
            if (window.gemsConversationEnded) return;
            
            console.log("Gems Station detected - ending conversation");
            window.gemsConversationEnded = true;
            
            // Find the input textarea
            const inputSelectors = [
                'rich-textarea textarea',
                '.ql-editor',
                'textarea[placeholder]',
                '[contenteditable="true"]',
                'textarea',
                'input[type="text"]'
            ];
            
            let inputElement = null;
            let inputContainer = null;
            
            for (const selector of inputSelectors) {{
                const elements = document.querySelectorAll(selector);
                for (const elem of elements) {{
                    if (elem && (elem.tagName === 'TEXTAREA' || elem.tagName === 'INPUT' || elem.contentEditable === 'true')) {{
                        inputElement = elem;
                        // Find the parent container that holds the input
                        inputContainer = elem.closest('.input-area') || elem.closest('.query-input-container') || 
                                       elem.closest('[class*="input"]') || elem.parentElement;
                        break;
                    }}
                }}
                if (inputElement) break;
            }}
            
            if (inputElement) {{
                // Disable the input without changing color
                inputElement.disabled = true;
                inputElement.setAttribute('readonly', 'true');
                inputElement.style.cursor = 'not-allowed';
                
                // If it's contenteditable, disable it
                if (inputElement.contentEditable) {{
                    inputElement.contentEditable = 'false';
                }}
                
                // Hide send button
                const sendButtonSelectors = [
                    'button[aria-label*="send"]',
                    'button[aria-label*="Send"]',
                    'button[aria-label*="전송"]',
                    'button[aria-label*="보내기"]',
                    '.send-button',
                    '[class*="send-button"]',
                    'button mat-icon[fonticon="send"]',
                    'button mat-icon[fonticon="arrow_upward"]',
                    'rich-textarea button',
                    '.input-area button',
                    '.query-input-container button'
                ];
                
                for (const selector of sendButtonSelectors) {{
                    const sendButtons = document.querySelectorAll(selector);
                    sendButtons.forEach(btn => {{
                        if (btn && (btn.textContent.includes('send') || 
                                   btn.textContent.includes('arrow_upward') ||
                                   btn.querySelector('mat-icon[fonticon="send"]') ||
                                   btn.querySelector('mat-icon[fonticon="arrow_upward"]'))) {{
                            btn.style.display = 'none';
                            console.log('Hidden send button');
                        }}
                    }});
                }}
                
                // Create print button container
                const printBtnContainer = document.createElement('div');
                printBtnContainer.id = 'gems-print-button-container';
                printBtnContainer.style.cssText = `
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin-bottom: 10px;
                    padding: 0;
                    position: relative;
                    opacity: 0;
                    transform: translateY(20px);
                `;
                
                // Create print button
                const printBtn = document.createElement('button');
                printBtn.id = 'gems-print-button';
                printBtn.style.cssText = `
                    border: none;
                    background: transparent;
                    cursor: pointer;
                    padding: 0;
                    z-index: 1000;
                    outline: none;
                    width: 150px;
                    height: auto;
                `;
                
                // Create image element that fills the button
                const printImg = document.createElement('img');
                printImg.src = 'data:image/png;base64,{img_base64}';
                printImg.style.cssText = 'width: 100%; height: auto; display: block;';
                printImg.alt = 'Print';
                
                printBtn.appendChild(printImg);
                printBtnContainer.appendChild(printBtn);
                
                // Add CSS animation keyframes
                const styleSheet = document.createElement('style');
                styleSheet.textContent = `
                    @keyframes popUpFromBottom {{
                        0% {{
                            opacity: 0;
                            transform: translateY(20px);
                        }}
                        100% {{
                            opacity: 1;
                            transform: translateY(0);
                        }}
                    }}
                    
                    .pop-up-animation {{
                        animation: popUpFromBottom 0.4s ease-out forwards;
                    }}
                `;
                document.head.appendChild(styleSheet);
                
                // Add click handler for transition animation
                printBtn.addEventListener('click', function() {{
                    console.log('Print button clicked!');
                    // Set a flag for Python to detect
                    window.printButtonClicked = true;
                }});
                
                // Find the input area's outermost container
                let insertTarget = null;
                let searchElement = inputElement;
                
                // Search for the main input area container by going up the DOM tree
                while (searchElement && searchElement.parentElement) {{
                    const parent = searchElement.parentElement;
                    
                    // Look for containers that are likely the main input area
                    if (parent.className && (
                        parent.className.includes('input-area') ||
                        parent.className.includes('query-input') ||
                        parent.className.includes('message-input') ||
                        parent.className.includes('composer') ||
                        parent.className.includes('chat-input')
                    )) {{
                        insertTarget = parent;
                    }}
                    
                    // Also check if we've reached a main content area
                    if (parent.tagName === 'MAIN' || 
                        parent.className.includes('main-content') ||
                        parent.className.includes('chat-content')) {{
                        break;
                    }}
                    
                    searchElement = parent;
                }}
                
                // If we didn't find a specific input container, use the highest suitable parent
                if (!insertTarget && inputElement) {{
                    insertTarget = inputElement.parentElement;
                    while (insertTarget && insertTarget.parentElement) {{
                        const nextParent = insertTarget.parentElement;
                        if (nextParent.tagName === 'BODY' || 
                            nextParent.tagName === 'HTML' ||
                            nextParent.className.includes('main-content')) {{
                            break;
                        }}
                        insertTarget = nextParent;
                    }}
                }}
                
                // Insert the print button container above the input area
                if (insertTarget && insertTarget.parentElement) {{
                    // Make sure we're inserting before the input area, not inside it
                    insertTarget.parentElement.insertBefore(printBtnContainer, insertTarget);
                    console.log("Print button added above input box");
                    
                    // Trigger the pop-up animation after insertion
                    setTimeout(() => {{
                        printBtnContainer.classList.add('pop-up-animation');
                    }}, 50);
                    
                    // Wait a moment for layout to settle, then center properly
                    setTimeout(() => {{
                        // Apply positioning to center button on page
                        printBtnContainer.style.cssText = `
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            margin-bottom: 10px;
                            padding: 0;
                            width: 100%;
                            position: relative;
                            left: 0;
                            right: 0;
                            box-sizing: border-box;
                            opacity: 1;
                        `;
                        
                        console.log('Button centered on page');
                    }}, 100);  // Small delay to ensure layout is complete
                }} else {{
                    // Fallback: try to find the chat area and append there
                    const chatArea = document.querySelector('[class*="chat"]') || document.querySelector('main');
                    if (chatArea) {{
                        chatArea.appendChild(printBtnContainer);
                        console.log("Print button added to chat area");
                    }} else {{
                        document.body.appendChild(printBtnContainer);
                        console.log("Print button added to body as fallback");
                    }}
                    
                    // Trigger animation for fallback cases too
                    setTimeout(() => {{
                        printBtnContainer.classList.add('pop-up-animation');
                    }}, 50);
                }}
                
                console.log("Input disabled and print button added");
            }} else {{
                console.log("Could not find input element");
            }}
        }}
        
        // Set up MutationObserver to monitor chat messages
        const chatObserver = new MutationObserver((mutations) => {{
            mutations.forEach((mutation) => {{
                mutation.addedNodes.forEach((node) => {{
                    if (node.nodeType === 1) {{ // Element node
                        // Check for message containers with improved selectors
                        const messageSelectors = [
                            '.model-response-text',
                            '.response-container-content',
                            '.presented-response-container',
                            '[class*="message-content"]',
                            '.message-text',
                            '.response-text',
                            '.markdown-container',
                            'message-content'
                        ];
                        
                        // First check the node itself
                        const nodeText = node.textContent || node.innerText || '';
                        if (nodeText && containsGemsStation(nodeText)) {{
                            console.log("Found 'Gems Station' in new node");
                            setTimeout(endConversationAndAddPrintButton, 500);
                            return;
                        }}
                        
                        // Then check child elements
                        for (const selector of messageSelectors) {{
                            let elements = [];
                            if (node.matches && node.matches(selector)) {{
                                elements = [node];
                            }} else if (node.querySelectorAll) {{
                                elements = node.querySelectorAll(selector);
                            }}
                            
                            for (const elem of elements) {{
                                const text = elem.textContent || elem.innerText || '';
                                if (containsGemsStation(text)) {{
                                    console.log("Found 'Gems Station' in message element");
                                    // Delay slightly to ensure DOM is ready
                                    setTimeout(endConversationAndAddPrintButton, 500);
                                    return;
                                }}
                            }}
                        }}
                    }}
                }});
            }});
        }});
        
        // Start observing the chat area
        chatObserver.observe(document.body, {{
            childList: true,
            subtree: true,
            characterData: true,
            characterDataOldValue: true
        }});
        
        console.log('Chat monitoring for "Gems Station" started');
        
        // Monitor input for special commands
        setInterval(() => {{
            const inputSelectors = [
                'rich-textarea textarea',
                '.ql-editor',
                'textarea[placeholder]',
                '[contenteditable="true"]',
                'textarea',
                'input[type="text"]'
            ];
            
            for (const selector of inputSelectors) {{
                const elements = document.querySelectorAll(selector);
                for (const elem of elements) {{
                    if (elem && (elem.value || elem.textContent)) {{
                        const text = elem.value || elem.textContent || '';
                        
                        // Check for exit command
                        if (text === '종료') {{
                            console.log('Exit command detected');
                            window.exitCommand = true;
                            // Clear the input
                            if (elem.value !== undefined) elem.value = '';
                            else elem.textContent = '';
                            return;
                        }}
                        
                        // Check for test command
                        if (text === '출력테스트') {{
                            console.log('Test command detected');
                            window.testCommand = true;
                            // Clear the input
                            if (elem.value !== undefined) elem.value = '';
                            else elem.textContent = '';
                            return;
                        }}
                    }}
                }}
            }}
        }}, 500);  // Check every 500ms
        
        // Also check existing messages with improved selectors and debugging
        setTimeout(() => {{
            console.log("Starting to check existing messages...");
            
            // Try multiple approaches to find messages
            const messageSelectors = [
                '.model-response-text',
                '.response-container-content',
                '.presented-response-container',
                '[class*="message-content"]',
                '.message-text',
                '.response-text',
                '.markdown-container',
                'message-content',
                // Add more specific selectors for Gemini
                '.model-response',
                '[data-test-id*="response"]',
                '.conversation-container',
                'model-response'
            ];
            
            // First, try to find all elements that might contain messages
            let allMessages = [];
            for (const selector of messageSelectors) {{
                try {{
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {{
                        console.log(`Found ${{elements.length}} elements with selector: ${{selector}}`);
                        allMessages.push(...elements);
                    }}
                }} catch (e) {{
                    console.log(`Error with selector ${{selector}}: ${{e}}`);
                }}
            }}
            
            // Also try to find elements containing Korean text
            const allElements = document.querySelectorAll('*');
            for (const elem of allElements) {{
                const text = elem.textContent || elem.innerText || '';
                if (text.includes('Gems Station') || text.includes('지수님')) {{
                    console.log(`Found relevant text in element:`, elem.className || elem.tagName);
                    if (!allMessages.includes(elem)) {{
                        allMessages.push(elem);
                    }}
                }}
            }}
            
            console.log(`Total elements to check: ${{allMessages.length}}`);
            
            // Check each message for 'Gems Station'
            for (const msg of allMessages) {{
                const text = msg.textContent || msg.innerText || '';
                if (containsGemsStation(text)) {{
                    console.log("Found 'Gems Station' in existing messages!");
                    console.log("Element class:", msg.className);
                    console.log("Element tag:", msg.tagName);
                    endConversationAndAddPrintButton();
                    break;
                }}
            }}
        }}, 3000);  // Increased delay to ensure page is fully loaded
        """
        
        driver.execute_script(monitor_script)
        print("Chat monitoring and print button functionality initialized")
        
        # Monitor for print button clicks in a separate thread
        def check_print_button():
            # Use absolute path for CSV
            csv_path = os.path.join(current_dir, "res", "GML25_F&B Menu.csv")
            
            # Get API key from environment or credentials
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                try:
                    with open('gemini_api_key.txt', 'r') as f:
                        api_key = f.read().strip()
                except:
                    print("WARNING: No Gemini API key found. Please set GEMINI_API_KEY environment variable or create gemini_api_key.txt")
                    api_key = ""
            
            parser = GeminiParser(api_key, csv_path)
            
            # Test data for 출력테스트
            test_names = ["지수", "민준", "서연", "하준", "서준", "도윤", "예준", "시우", "주원", "하은"]
            test_types = [
                ("1", "Bold Creator", "남다른 시도로 새로운 가치를 만들고, 깊이 있는 전략으로 시장을 이끄는 마케터.", "#도전 #전략적 #리더십", "Negroni", "코랄 소스의 랍스터 테일"),
                ("2", "Unexpected Innovator", "틀을 깨는 아이디어로 고객에게 놀라움을 선사하고, 늘 새로운 변화를 시도하는 마케터.", "#열정 #변주 #모험적", "Negroni", "파가든 브리오쉬 한우 버거"),
                ("3", "Future Seeker", "시대의 흐름을 꿰뚫어 보고, 자신만의 방식으로 새로운 유행을 만들어가는 마케터.", "#전략적 #넓은시야 #영감", "Negroni", "아보카도 리코타 치즈 토스트"),
                ("4", "Experience Architect", "고객의 오감을 사로잡는 디테일로, 상품을 넘어 완벽한 경험을 디자인하는 마케터.", "#조화 #섬세함 #소통", "Grapefruit Blossom", "망고 크림 새우"),
                ("5", "Harmony Seeker", "서로 다른 요소를 균형 있게 조화시켜, 모두가 만족할 수 있는 안정적인 솔루션을 제시하는 마케터.", "#밸런스 #조화 #안정성", "Grapefruit Blossom", "고르곤졸라 피자"),
                ("6", "Curious Explorer", "익숙함 속에서도 새로운 재미를 찾아내고, 고객의 호기심을 자극하며 다양성을 즐기는 마케터.", "#영감 #도전 #다양성", "Grapefruit Blossom", "와사비 젤리 허브 연어"),
                ("7", "Positive Giver", "고객의 삶에 긍정적인 에너지와 영감을 불어넣으며, 좋은 라이프스타일을 자연스럽게 제안하는 마케터.", "#소통 #효율성 #안정성", "Fuzzy Navel", "아보카도 리코타 치즈 토스트"),
                ("8", "Cozy Connector", "일상의 작은 행복을 소중히 여기고, 섬세한 감성으로 고객의 마음에 공감하며 편안함을 주는 마케터.", "#조화 #섬세함 #아우름", "Fuzzy Navel", "고르곤졸라 피자")
            ]
            
            while True:
                try:
                    # Check for exit command
                    if driver.execute_script("return window.exitCommand || false;"):
                        print("Exit command detected, returning to waiting screen...")
                        driver.execute_script("window.exitCommand = false;")
                        # Navigate to waiting screen
                        show_waiting_screen_and_continue(driver)
                        break
                    
                    # Check for test command
                    if driver.execute_script("return window.testCommand || false;"):
                        print("Test command detected, creating test data...")
                        driver.execute_script("window.testCommand = false;")
                        
                        # Generate random test data
                        test_name = random.choice(test_names)
                        test_type = random.choice(test_types)
                        
                        test_data = {
                            "이름": test_name,
                            "번호": test_type[0],
                            "타입명": test_type[1],
                            "타입_설명": test_type[2],
                            "성향_키워드": test_type[3],
                            "음료": test_type[4],
                            "푸드": test_type[5]
                        }
                        
                        # Save test data
                        with open("parsed_conversation.json", 'w', encoding='utf-8') as f:
                            json.dump(test_data, f, ensure_ascii=False, indent=2)
                        
                        print(f"Test data saved: {test_name} - {test_type[1]} (Type #{test_type[0]})")
                        print(json.dumps(test_data, ensure_ascii=False, indent=2))
                        
                        # Generate receipt with name
                        try:
                            printer = ReceiptPrinter()
                            printer.add_name_to_receipt(test_data, "thermal_print.png")
                        except Exception as e:
                            print(f"Error generating receipt: {e}")
                        
                        # Navigate to transition screen
                        if platform.system() == 'Windows':
                            driver.get(f"file:///{transition_path.replace(chr(92), '/')}")
                        else:
                            driver.get(f"file://{transition_path}")
                        
                        # Wait for transition to complete
                        print("Waiting for transition to complete...")
                        while True:
                            try:
                                if driver.execute_script("return window.transitionComplete || false;"):
                                    print("Transition complete, returning to waiting screen...")
                                    # Show waiting screen again
                                    show_waiting_screen_and_continue(driver)
                                    break
                            except:
                                break
                            time.sleep(0.1)
                        break
                    
                    # Check for print button click
                    if driver.execute_script("return window.printButtonClicked || false;"):
                        print("Print button clicked detected!")
                        
                        # Extract conversation text before navigating
                        conversation_text = None
                        try:
                            conversation_text = driver.execute_script("""
                                // Try multiple selectors to find conversation elements
                                const selectors = [
                                    '.model-response-text',
                                    '.response-container-content', 
                                    '.presented-response-container',
                                    '[class*="message-content"]',
                                    '.message-text',
                                    '.response-text',
                                    '.markdown-container',
                                    'message-content',
                                    '[class*="response"]',
                                    '[class*="message"]'
                                ];
                                
                                let allElements = new Set();
                                selectors.forEach(selector => {
                                    try {
                                        document.querySelectorAll(selector).forEach(el => allElements.add(el));
                                    } catch(e) {}
                                });
                                
                                let fullText = '';
                                allElements.forEach(el => {
                                    if (el.textContent && el.textContent.trim()) {
                                        fullText += el.textContent + '\\n';
                                    }
                                });
                                
                                return fullText;
                            """)
                        except Exception as e:
                            print(f"Error extracting conversation: {e}")
                        
                        driver.execute_script("window.printButtonClicked = false;")
                        
                        # Navigate to transition page IMMEDIATELY
                        print("Navigating to transition page...")
                        if platform.system() == 'Windows':
                            driver.get(f"file:///{transition_path.replace(chr(92), '/')}")
                        else:
                            driver.get(f"file://{transition_path}")
                        
                        # Now do the heavy processing while user sees the transition animation
                        if conversation_text:
                            print(f"Processing conversation (length: {len(conversation_text)})...")
                            
                            # Parse with Gemini API (this takes time)
                            try:
                                print("Parsing conversation data with Gemini...")
                                parsed_data = parser.parse_and_save(conversation_text)
                                print(f"Parsed data: {json.dumps(parsed_data, ensure_ascii=False, indent=2)}")
                                
                                # Generate receipt image
                                print("Generating receipt image...")
                                printer = ReceiptPrinter()
                                printer.add_name_to_receipt(parsed_data, "thermal_print.png")
                                
                                # Print to thermal printer
                                print("Sending to thermal printer...")
                                # The printer will automatically print when receipt is generated
                                
                            except Exception as ex:
                                print(f"Error in processing: {ex}")
                        else:
                            print("No conversation text found!")
                        
                        # Wait for transition to complete
                        print("Waiting for transition to complete...")
                        while True:
                            try:
                                if driver.execute_script("return window.transitionComplete || false;"):
                                    print("Transition complete, returning to waiting screen...")
                                    # Show waiting screen again
                                    show_waiting_screen_and_continue(driver)
                                    break
                            except:
                                break
                            time.sleep(0.1)
                        break
                except:
                    break
                time.sleep(0.1)
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=check_print_button, daemon=True)
        monitor_thread.start()
        
    except Exception as e:
        print(f"Error setting up chat monitoring: {str(e)}")

def inject_hiding_css(driver):
    """Inject CSS to hide elements before they render"""
    css_injection_script = """
    // Inject CSS immediately to prevent flash of unwanted content
    const style = document.createElement('style');
    style.id = 'gems-hiding-styles';
    style.textContent = `
        /* Hide elements before they render */
        bard-sidenav,
        .cdk-overlay-pane,
        [data-test-id="chat-app"],
        .boqOnegoogleliteOgbOneGoogleBar,
        #gb,
        top-bar-actions,
        .bot-recent-chats,
        .uploader-button-container,
        toolbox-drawer,
        .mic-button-container,
        .response-container-footer,
        [class*="recent-chats"],
        [class*="recent"][class*="chat"],
        hallucination-disclaimer,
        .hallucination-disclaimer,
        .capabilities-disclaimer,
        [data-test-id="highly-regulated-disclaimer"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            transition: none !important;
        }
        
        /* Add bottom padding to input area */
        .input-area-container,
        [class*="input-area"],
        .query-input-container,
        [class*="query-input"],
        .composer-container,
        [class*="composer"] {
            padding-bottom: 40px !important;
        }
    `;
    // Insert at the beginning of head to ensure it's applied early
    if (document.head.firstChild) {
        document.head.insertBefore(style, document.head.firstChild);
    } else {
        document.head.appendChild(style);
    }
    console.log('Early CSS injection complete');
    """
    driver.execute_script(css_injection_script)

def show_transition_overlay(driver):
    """Show a fullscreen transition overlay while elements are being hidden"""
    overlay_script = """
    // First remove any existing overlay
    const existingOverlay = document.getElementById('gems-transition-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }
    
    // Create fullscreen overlay with transition animation
    const overlay = document.createElement('div');
    overlay.id = 'gems-transition-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(255, 255, 255, 0.95);
        z-index: 999999;
        display: flex;
        justify-content: center;
        align-items: center;
        opacity: 1;
        transition: opacity 0.5s ease-out;
    `;
    
    // Create content container
    const container = document.createElement('div');
    container.style.textAlign = 'center';
    
    // Create loader
    const loader = document.createElement('div');
    loader.className = 'loader';
    loader.style.cssText = `
        width: 80px;
        height: 80px;
        border: 8px solid #f3f3f3;
        border-top: 8px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 20px;
    `;
    
    // Create text
    const text = document.createElement('h2');
    text.style.cssText = 'font-family: Arial, sans-serif; color: #333; margin: 0;';
    text.textContent = '잠시만 기다려주세요...';
    
    // Assemble elements
    container.appendChild(loader);
    container.appendChild(text);
    overlay.appendChild(container);
    
    // Add animation keyframes
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    // Add overlay to body
    document.body.appendChild(overlay);
    
    // Function to remove overlay
    window.removeTransitionOverlay = function() {
        const overlay = document.getElementById('gems-transition-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.remove();
            }, 500);
        }
    };
    
    console.log('Transition overlay shown');
    """
    driver.execute_script(overlay_script)

def remove_transition_overlay(driver):
    """Remove the transition overlay and any lingering overlays"""
    remove_overlay_script = """
    // Remove our transition overlay
    if (window.removeTransitionOverlay) {
        window.removeTransitionOverlay();
    }
    
    // Also remove any overlay by ID
    const overlay = document.getElementById('gems-transition-overlay');
    if (overlay) {
        overlay.remove();
    }
    
    // Remove any other overlays that might be blocking
    const overlays = document.querySelectorAll('[style*="z-index: 999999"], [style*="z-index: 2147483647"]');
    overlays.forEach(el => {
        if (el.style.position === 'fixed' && 
            el.style.width === '100vw' && 
            el.style.height === '100vh') {
            console.log('Removing blocking overlay:', el);
            el.remove();
        }
    });
    
    // Also check for any dark backgrounds or overlays from Gemini itself
    const darkOverlays = document.querySelectorAll('.cdk-overlay-backdrop, .cdk-overlay-dark-backdrop, [class*="backdrop"]');
    darkOverlays.forEach(el => {
        console.log('Removing dark backdrop:', el.className);
        el.remove();
    });
    
    // Remove any fixed position elements that cover the full screen
    const fixedElements = document.querySelectorAll('*');
    fixedElements.forEach(el => {
        const style = window.getComputedStyle(el);
        if (style.position === 'fixed' && 
            style.width === '100vw' && 
            style.height === '100vh' &&
            style.zIndex && parseInt(style.zIndex) > 1000) {
            console.log('Removing high z-index fixed element:', el);
            el.remove();
        }
    });
    """
    driver.execute_script(remove_overlay_script)
    print("Transition overlay and dark backgrounds removed")

def find_first_gem_url(driver):
    """Find the first gem in the gems list and return its URL"""
    try:
        print("\nChecking sidebar and looking for gems...")
        
        # Wait a bit for the page to load
        time.sleep(2)
        
        # First, check if sidebar is collapsed and open it if needed
        open_sidebar_script = """
        // Check if we can see gems
        let gemLinks = document.querySelectorAll('a[href*="/gem/"]');
        let botItems = document.querySelectorAll('bot-list-item');
        
        // If no gems visible, try to open sidebar
        if (gemLinks.length === 0 && botItems.length === 0) {
            console.log('No gems visible, looking for menu button...');
            
            // Try different selectors for the menu button
            const menuSelectors = [
                'button[aria-label="기본 메뉴"]',
                'button[data-test-id="side-nav-menu-button"]',
                'button[contains(@aria-label, "menu")]',
                'button mat-icon[fonticon="menu"]',
                'button .material-icons:contains("menu")'
            ];
            
            let menuButton = null;
            for (const selector of menuSelectors) {
                try {
                    menuButton = document.querySelector(selector);
                    if (menuButton) break;
                } catch (e) {}
            }
            
            // Alternative: find button containing menu icon
            if (!menuButton) {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    if (btn.querySelector('mat-icon[fonticon="menu"]') || 
                        (btn.textContent && btn.textContent.includes('menu'))) {
                        menuButton = btn;
                        break;
                    }
                }
            }
            
            if (menuButton) {
                console.log('Found menu button, clicking to open sidebar');
                menuButton.click();
                return 'sidebar_opened';
            }
        }
        
        return 'sidebar_already_open';
        """
        
        sidebar_status = driver.execute_script(open_sidebar_script)
        
        if sidebar_status == 'sidebar_opened':
            print("Opened collapsed sidebar")
            time.sleep(2)  # Wait for sidebar animation
        else:
            print("Sidebar was already open")
        
        # Now click on the first gem button
        click_first_gem_script = """
        // Look for bot list items
        const botItems = document.querySelectorAll('bot-list-item');
        if (botItems.length > 0) {
            console.log('Found', botItems.length, 'bot items');
            
            // Get the first bot item
            const firstBot = botItems[0];
            
            // Find the button with class 'bot-new-conversation-button'
            const gemButton = firstBot.querySelector('button.bot-new-conversation-button');
            
            if (gemButton) {
                console.log('Found gem button, clicking it');
                // Get the gem name for logging
                const gemName = gemButton.querySelector('.bot-name')?.textContent || 'Unknown';
                console.log('Clicking on gem:', gemName);
                
                // Click the button
                gemButton.click();
                
                return gemName;
            }
        }
        
        console.log('No gem buttons found');
        return null;
        """
        
        gem_name = driver.execute_script(click_first_gem_script)
        
        if gem_name:
            print(f"Clicked on gem: {gem_name}")
            # Wait for navigation to complete
            time.sleep(3)
            
            # Get the current URL after clicking
            current_url = driver.current_url
            print(f"Navigated to: {current_url}")
            
            # Store the URL
            driver.first_gem_url = current_url
            return current_url
        else:
            print("Could not click on any gem")
            # Fallback to hardcoded URL if no gems found
            fallback_url = "https://gemini.google.com/gem/d43c6f8224ff"
            print(f"Using fallback URL: {fallback_url}")
            driver.first_gem_url = fallback_url
            return fallback_url
            
    except Exception as e:
        print(f"Error finding gem URL: {str(e)}")
        # Fallback to hardcoded URL
        fallback_url = "https://gemini.google.com/gem/d43c6f8224ff"
        driver.first_gem_url = fallback_url
        return fallback_url

def open_gourmet_gems(driver):
    """Navigate to the gem URL (either found dynamically or stored)"""
    try:
        print("\nOpening gem...")
        
        # Get the gem URL (use stored one if available)
        gem_url = getattr(driver, 'first_gem_url', None)
        if not gem_url:
            # If no stored URL, find it
            gem_url = find_first_gem_url(driver)
        
        print(f"Navigating to: {gem_url}")
        
        # Inject CSS before navigation to prepare the page
        inject_hiding_css(driver)
        
        driver.get(gem_url)
        
        # Don't show overlay - just hide elements quickly
        # Inject CSS again after navigation
        inject_hiding_css(driver)
        
        # Hide UI elements immediately
        close_sidebar_menu(driver)
        
        # Wait a bit for page to stabilize
        time.sleep(2)
        
        # Clean up any remaining overlays or dark backgrounds
        remove_transition_overlay(driver)
        
        print(f"Successfully navigated to gem")
        
        # Start monitoring chat for "Gems Station" keyword
        monitor_chat_and_add_print_button(driver)
        
    except Exception as e:
        print(f"Error opening gem: {str(e)}")

# Commented out original gem finding function
# def open_gourmet_gems(driver):
#     try:
#         print("\nChecking if menu needs to be opened...")
#         
#         # First check if the menu is collapsed/folded
#         menu_selectors = [
#             "//button[@aria-label='기본 메뉴']",
#             "//button[@data-test-id='side-nav-menu-button']",
#             "//button[contains(@class, 'main-menu-button')]",
#             "//mat-icon[@fonticon='menu']/parent::button",
#             "//mat-icon[text()='menu']/parent::button",
#             "//button[contains(@aria-label, 'menu')]",
#             "//button[contains(@aria-label, 'Menu')]"
#         ]
#         
#         # Try to find the menu button
#         for selector in menu_selectors:
#             try:
#                 menu_button = driver.find_element(By.XPATH, selector)
#                 # Check if sidebar is collapsed by looking for the gems list
#                 try:
#                     gems_visible = driver.find_element(By.CLASS_NAME, "gems-list-container")
#                     if not gems_visible.is_displayed():
#                         print("Menu appears to be collapsed, clicking to open...")
#                         driver.execute_script("arguments[0].click();", menu_button)
#                         time.sleep(2)
#                 except:
#                     # Gems list not visible, try clicking menu
#                     print("Gems list not visible, clicking menu button...")
#                     driver.execute_script("arguments[0].click();", menu_button)
#                     time.sleep(2)
#                 break
#             except:
#                 continue
#         
#         print("\nWaiting for gems list to load...")
#         
#         # Wait for the gems list container to be present
#         try:
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CLASS_NAME, "gems-list-container"))
#             )
#             print("Gems list container found")
#         except TimeoutException:
#             print("Gems list container not found, continuing anyway...")
#         
#         # Additional wait for dynamic content
#         time.sleep(3)
#         
#         print("Looking for the first gem to open...")
#         
#         # Look for any gem button/link
#         gem_selectors = [
#             "//button[@class='mat-mdc-tooltip-trigger bot-new-conversation-button']",
#             "//span[@class='bot-name']/ancestor::button",
#             "//bot-list-item//button",
#             "//div[@class='bot-item']//button",
#             "//a[contains(@href, '/gem/')]",
#             "//button[contains(@class, 'bot-') and contains(@class, 'button')]"
#         ]
#         
#         first_gem = None
#         for selector in gem_selectors:
#             try:
#                 gems = driver.find_elements(By.XPATH, selector)
#                 if gems:
#                     first_gem = gems[0]  # Get the first gem
#                     print(f"Found {len(gems)} gems, will open the first one")
#                     break
#             except:
#                 continue
#         
#         if first_gem:
#             try:
#                 gem_text = first_gem.text or first_gem.get_attribute('aria-label') or 'Unknown'
#                 print(f"\nOpening first gem: {gem_text}")
#                 
#                 # Scroll the element into view
#                 driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_gem)
#                 time.sleep(0.5)
#                 
#                 # Click the gem
#                 driver.execute_script("arguments[0].click();", first_gem)
#                 
#                 # Wait for the gem to load
#                 time.sleep(3)
#                 
#                 print(f"Successfully opened: {gem_text}")
#                 
#                 # Close the left sidebar menu
#                 close_sidebar_menu(driver)
#                 
#             except Exception as e:
#                 print(f"Failed to open first gem: {str(e)}")
#         else:
#             print("No gems found on the page")
#             
#     except Exception as e:
#         print(f"Error while searching for Gourmet gems: {str(e)}")

def show_waiting_screen(driver):
    """Display the waiting screen HTML page and wait for user to click continue"""
    print("\n" + "="*60)
    print("🎮 Showing waiting screen...")
    print("Click the button on the waiting screen to continue to Gems")
    print("="*60 + "\n")
    
    # Get the absolute path to the HTML file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "waiting_screen.html")
    
    # Convert to file URL - properly handle Windows paths
    if platform.system() == 'Windows':
        # Windows file URLs need three slashes
        file_url = "file:///" + html_path.replace("\\", "/")
    else:
        file_url = "file://" + urllib.parse.quote(html_path.replace("\\", "/"))
    
    # Navigate to the waiting screen
    driver.get(file_url)
    
    # Inject the gem URL into sessionStorage for the waiting screen to use
    if hasattr(driver, 'first_gem_url'):
        driver.execute_script(f"sessionStorage.setItem('gemUrl', '{driver.first_gem_url}');")
        print(f"Gem URL set in sessionStorage: {driver.first_gem_url}")
    
    # Wait for the user to click the continue button
    print("Waiting for user to click the continue button...")
    
    while True:
        try:
            current_url = driver.current_url
            
            # Check if we've navigated away from the waiting screen to the specific gem
            if "gemini.google.com/gem/" in current_url:
                print("Continue button clicked! Navigated to Gems")
                # Wait a moment for page to start loading
                time.sleep(0.5)
                break
            
            # Small delay to avoid excessive polling
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error checking navigation status: {e}")
            time.sleep(1)

def show_waiting_screen_and_continue(driver):
    """Show waiting screen and set up the page again when user continues"""
    show_waiting_screen(driver)
    
    # Immediately inject CSS to hide elements
    inject_hiding_css(driver)
    
    # Hide UI elements as fast as possible
    close_sidebar_menu(driver)
    
    # Start monitoring chat for "Gems Station" keyword again
    monitor_chat_and_add_print_button(driver)

def main():
    # Print system info for debugging
    print(f"Running on: {platform.system()} {platform.version()}")
    print(f"Python version: {platform.python_version()}")
    
    # Try to load credentials, but don't fail if they don't exist
    credentials = None
    try:
        credentials = load_credentials()
        print("Credentials loaded from file")
    except Exception as e:
        print(f"No credentials file found ({e}) - manual login will be required")
    
    print("\nSetting up Chrome driver...")
    try:
        driver = setup_driver()
        print("Chrome driver created successfully")
    except Exception as e:
        print(f"Failed to create Chrome driver: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure Chrome browser is installed")
        print("2. Run: pip install --upgrade selenium webdriver-manager")
        print("3. Try running test_chrome_windows.py first")
        raise
    
    try:
        print("\nStarting login process...")
        login_to_google_gems(driver, credentials)
        
        # Find and store the first gem URL after login
        find_first_gem_url(driver)
        
        # Show the waiting screen after successful login and handle the cycle
        show_waiting_screen_and_continue(driver)
        
        print("\n📝 Browser will remain open. Press Enter to close it...")
        input()
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print("\nBrowser will remain open for debugging. Press Enter to close it...")
        input()
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    main()