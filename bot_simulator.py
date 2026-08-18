import asyncio
import json
import logging
import random
import time
from datetime import datetime
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# Setup JSON Logger
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("BotSimulatorLogger")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
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

def log_session_metrics(bot_id, platform, url, proxy, user_agent, duration, status, error=""):
    """Outputs structured JSON log entry for bot tracking."""
    log_entry = {
        "bot_id": bot_id,
        "timestamp_start": datetime.utcnow().isoformat(),
        "platform": platform,
        "url": url,
        "proxy_ip": proxy or "Direct",
        "user_agent": user_agent,
        "watch_duration_sec": round(duration, 2),
        "status": status,
        "error": error
    }
    logger.info(json.dumps(log_entry))

async def simulate_bot_engagement(page, duration, bot_id):
    """Executes human-like viewer actions without requiring login."""
    start_time = time.time()

    # 1. Force Video Playback if paused
    try:
        play_btn = await page.query_selector("button.ytp-play-button, video")
        if play_btn:
            await play_btn.click()
            print(f"[{bot_id}] Triggered video playback.")
    except Exception:
        pass

    # 2. Lower Quality to 144p to optimize network load
    try:
        settings_btn = await page.query_selector(".ytp-settings-button")
        if settings_btn:
            await settings_btn.click()
            await asyncio.sleep(0.5)
            menu_items = await page.query_selector_all(".ytp-menuitem")
            for item in menu_items:
                text = await item.text_content()
                if "Quality" in text:
                    await item.click()
                    await asyncio.sleep(0.5)
                    lowest_q = await page.query_selector("xpath=//span[contains(text(),'144p')]")
                    if lowest_q:
                        await lowest_q.click()
                        print(f"[{bot_id}] Adjusted quality to 144p.")
                    break
    except Exception:
        pass

    # 3. Organic Engagement Loop (Curved movements & micro-scrolls)
    while (time.time() - start_time) < duration:
        x, y = random.randint(200, 800), random.randint(200, 600)
        await page.mouse.move(x, y, steps=random.randint(5, 15))
        
        if random.random() > 0.6:
            scroll_y = random.choice([200, -200])
            await page.mouse.wheel(0, scroll_y)

        await asyncio.sleep(random.uniform(3, 7))

async def run_bot_session(bot_id, config, proxy):
    user_agent = random.choice(USER_AGENTS)
    viewport = random.choice(VIEWPORTS)
    watch_duration = random.uniform(config["min_watch_duration_sec"], config["max_watch_duration_sec"])
    status = "failure"
    error = ""

    async with Stealth().use_async(async_playwright()) as p:
        launch_kwargs = {"headless": False}  # Set to True for silent background execution
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

            print(f"[{bot_id}] Navigating to {config['target_url']}...")
            await page.goto(config["target_url"], wait_until="domcontentloaded", timeout=45000)

            await simulate_bot_engagement(page, watch_duration, bot_id)
            
            status = "success"
            await browser.close()

        except Exception as e:
            error = str(e)
            status = "failure"
            print(f"[{bot_id}] Exception: {error}")

    log_session_metrics(
        bot_id, config["target_platform"], config["target_url"],
        proxy, user_agent, watch_duration, status, error
    )

async def main():
    config = load_config()
    proxies = load_proxies(config["proxy_file"]) if config["use_proxies"] else []

    print(f"Starting Dedicated Bot Engine on: {config['target_url']}\n")

    tasks = []
    for i in range(config["total_sessions"]):
        bot_id = f"bot_{i+1:03d}"
        proxy = proxies[i % len(proxies)] if proxies else None
        
        task = asyncio.create_task(run_bot_session(bot_id, config, proxy))
        tasks.append(task)
        await asyncio.sleep(config["ramp_up_interval_sec"])

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())