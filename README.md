# Synthetic Concurrent User Simulator

An asynchronous Python tool built with Playwright to simulate concurrent user behavior across web streaming platforms under variable load conditions.

## Project Structure
* `simulator.py`: Main async execution script.
* `config.json`: Adjustable runtime parameters.
* `proxies.txt`: Proxy connection list.
* `requirements.txt`: Python package dependencies.
* `Dockerfile`: Container deployment config.

## Setup & Installation

1. Install system dependencies and Playwright:
   ```bash
   python3 -m pip install -r requirements.txt
   python3 -m playwright install chromium

   Project Execution Scripts: simulator.py: Executes interactive concurrent sessions with full human behavior simulation (mouse movements, vertical page scrolling, and chat automation).bot_simulator.py: Runs stealth, unauthenticated bot sessions designed to bypass bot detection (playwright-stealth), auto-start playback, drop stream quality to $144\text{p}$, and generate viewing metrics without requiring signed-in user accounts.Setup & Execution Commands: Install Dependencies: Ensure packages are installed under the Python 3.13 environment: Bash/opt/homebrew/bin/python3.13 -m pip install -r requirements.txt
/opt/homebrew/bin/python3.13 -m pip install playwright-stealth
/opt/homebrew/bin/python3.13 -m playwright install chromium
Navigate to Directory: Bash cd "/Users/ananyajha/Desktop/Concurrent User Simulator"
Run Simulator / Bot Engine: Run Interactive UI / Chat Simulator: Bash/opt/homebrew/bin/python3.13 simulator.py
Run Unauthenticated Bot Fleet: Bash/opt/homebrew/bin/python3.13 bot_simulator.py
