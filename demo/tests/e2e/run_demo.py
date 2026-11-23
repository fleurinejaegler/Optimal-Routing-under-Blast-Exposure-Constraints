import json, os, sys, time
from playwright.sync_api import sync_playwright

# Serve the demo first:  python3 -m http.server 8765  (run in this folder)
BASE = os.environ.get("DEMO_URL", "http://127.0.0.1:8765/index.html")
log = {}

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None, headless=True,
                                args=["--no-sandbox", "--disable-gpu"])
    page = browser.new_page(viewport={"width": 1280, "height": 900}, accept_downloads=True)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)

    # 1. first visit: pick A with the suggested start, check URL is written
    page.goto(BASE + "?seed=42", wait_until="load")
    page.wait_for_selector("#play")
    page.wait_for_function("document.getElementById('play').getAttribute('aria-label') === 'Start from a suggested spot'", timeout=60000)
    page.click("#play")
    page.wait_for_function("new URL(location.href).searchParams.has('a')", timeout=30000)
    url_after_pick = page.url
    log["url_after_pick"] = url_after_pick

    # 2. busy text: sample while the initial simulations run
    seen = set()
    t0 = time.time()
    while time.time() - t0 < 60:
        txt = page.inner_text("#busy") if page.is_visible("#busy") else ""
        if "simulations done" in txt:
            seen.add(txt)
        if page.is_visible("#stepNo") and "step 2" in page.inner_text("#stepNo"):
            break
        time.sleep(0.2)
    log["progress_labels_seen"] = sorted(seen)[:4]

    # 3. skip ahead to the result step with the step button
    t0 = time.time()
    while time.time() - t0 < 400:
        if page.is_visible("#summary") and page.locator("#dlCsv").count() and page.locator("#dlCsv").is_visible():
            break
        if page.is_enabled("#step"):
            page.click("#step")
        time.sleep(0.4)
    log["summary_visible"] = page.is_visible("#summary")

    # 4. exports
    if log["summary_visible"]:
        with page.expect_download() as d:
            page.click("#dlCsv")
        d.value.save_as("route.csv")
        with page.expect_download() as d:
            page.click("#dlJson")
        d.value.save_as("run.json")
        with page.expect_download() as d:
            page.click("#dlPng")
        d.value.save_as("map.png")

    # 5. reload the shared link: should skip picking and start running
    page.goto(url_after_pick, wait_until="load")
    page.wait_for_selector("#play")
    time.sleep(3)
    log["reload_skips_pick"] = page.get_attribute("#play", "aria-label") != "Start from a suggested spot"

    log["page_errors"] = errors[:5]
    browser.close()

print(json.dumps(log, indent=1, ensure_ascii=False))
