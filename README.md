# Gems Station Receipt Printer

Google Gemini chat monitor with automatic thermal receipt printing for "Gems Station" conversations.

## Features

- Monitors Google Gemini chat for "Gems Station" keyword
- Parses conversations using Gemini API to extract customer information
- Generates personalized receipts with customer names
- Automatically prints to HWASUNG HMK-072 thermal printer (Windows)
- Shows transition animation while printing

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. For Windows thermal printing:
```bash
pip install pywin32
```

3. Create `gemini_api_key.txt` with your Gemini API key

4. Update `credentials.json` with your Google account email:
```json
{
  "email": "your-email@gmail.com"
}
```

## Usage

Run the main application:
```bash
python google_gems.py
```

Test thermal printer:
```bash
python test_printer.py
```

## File Structure

- `google_gems.py` - Main application
- `gemini_parser.py` - Gemini API conversation parser
- `receipt_printer.py` - Receipt image generator
- `windows_thermal_printer.py` - Windows thermal printer driver
- `thermal_printer.py` - Printer interface (fallback to DLL method)
- `receipt_text_printer.py` - Text-based receipt fallback
- `waiting_screen.html` - Start screen
- `transition_screen.html` - Animation during printing
- `res/` - Resources (fonts, images, receipt templates)

## Requirements

- Windows OS (for thermal printing)
- HWASUNG HMK-072 thermal printer installed on Windows
- Google Chrome
- Python 3.8+

## Commands

- Type "종료" in chat to return to waiting screen
- Type "출력테스트" to test print with random data