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
