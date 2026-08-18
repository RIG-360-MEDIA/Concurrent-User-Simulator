import asyncio
import json
import logging
import random
import time
from datetime import datetime
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("SimulatorLogger")

INDIAN_NAMES = [
    "Ananya Jha", "Abhishek Pal", "Vibhu", "Anushka Mahajan",
    "Amaresh Jha", "Rohit Sharma", "Karan Malhotra", "Isha Joshi"
]

CHAT_MESSAGES = [
    "Great stream!", "Awesome content!", "Hello everyone",
    "To the person reading this God Bless You", "Nice performance", "Who is here in 2026?"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900}
]

def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

def load_proxies(path):
    try:
        with open(path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def log_session_metrics(session_id, platform, url, proxy, user_agent, duration, chats_sent, status, error=""):
    """Outputs structured JSON log entry for session tracking."""
    log_entry = {
        "session_id": session_id,
        "timestamp_start": datetime.utcnow().isoformat(),
        "platform": platform,
        "url": url,
        "proxy_ip": proxy or "Direct",
        "user_agent": user_agent,
        "watch_duration_sec": round(duration, 2),
        "chat_messages_sent": chats_sent,
        "status": status,
        "error": error
    }
    logger.info(json.dumps(log_entry))

async def simulate_human_behavior(page, duration, enable_chat, config, session_id):
    """Executes mouse moves, scrolling, and chat messages during playback."""
    start_time = time.time()
    chats_sent = 0
    max_chats = random.randint(config["min_chat_messages"], config["max_chat_messages"]) if enable_chat else 0
    next_chat_time = start_time + random.uniform(config["min_chat_interval_sec"], config["max_chat_interval_sec"])
    user_name = random.choice(INDIAN_NAMES)

    while (time.time() - start_time) < duration:
        #random mouse movement
        await page.mouse.move(random.randint(100, 600), random.randint(100, 600))
        
        #vertical scrolling
        if random.random() > 0.6:
            await page.mouse.wheel(0, random.choice([150, -150]))

        #chat messaging loop
        if enable_chat and chats_sent < max_chats and time.time() >= next_chat_time:
            
            chat_input = await page.query_selector("input[type='text'], textarea, #input")
            if chat_input:
                msg = f"{user_name}: {random.choice(CHAT_MESSAGES)}"
                try:
                    await chat_input.fill(msg)
                    await page.keyboard.press("Enter")
                    chats_sent += 1
                    print(f"[{session_id}] Sent chat ({chats_sent}/{max_chats}): {msg}")
                except Exception:
                    pass
            next_chat_time = time.time() + random.uniform(
                config["min_chat_interval_sec"], config["max_chat_interval_sec"]
            )

        await asyncio.sleep(random.uniform(2, 4))

    return chats_sent

async def run_session(session_id, config, proxy):
    user_agent = random.choice(USER_AGENTS)
    viewport = random.choice(VIEWPORTS)
    watch_duration = random.uniform(config["min_watch_duration_sec"], config["max_watch_duration_sec"])
    status = "failure"
    error = ""
    chats_sent = 0

    async with async_playwright() as p:
        launch_kwargs = {"headless": False}
        if config["use_proxies"] and proxy:
            launch_kwargs["proxy"] = {"server": proxy}

        try:
            browser = await p.chromium.launch(**launch_kwargs)
            context = await browser.new_context(
                user_agent=user_agent,
                viewport=viewport,
                locale="en-IN",
                timezone_id="Asia/Kolkata"
            )
            page = await context.new_page()

            print(f"[{session_id}] Navigating to {config['target_url']}...")
            await page.goto(config["target_url"], wait_until="domcontentloaded", timeout=30000)

            if config["target_platform"] == "youtube":
                try:
                    await page.click(".ytp-settings-button", timeout=3000)
                except Exception:
                    pass

            chats_sent = await simulate_human_behavior(page, watch_duration, config["enable_chat"], config, session_id)
            status = "success"
            await browser.close()

        except Exception as e:
            error = str(e)
            status = "failure" if chats_sent == 0 else "partial"
            print(f"[{session_id}] Exception: {error}")

    log_session_metrics(
        session_id, config["target_platform"], config["target_url"],
        proxy, user_agent, watch_duration, chats_sent, status, error
    )

async def main():
    config = load_config()
    proxies = load_proxies(config["proxy_file"]) if config["use_proxies"] else []

    print(f"Starting Simulator on target: {config['target_url']}\n")

    tasks = []
    for i in range(config["total_sessions"]):
        session_id = f"sess_{i+1:03d}"
        proxy = proxies[i % len(proxies)] if proxies else None
        
        task = asyncio.create_task(run_session(session_id, config, proxy))
        tasks.append(task)
        await asyncio.sleep(config["ramp_up_interval_sec"])

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())