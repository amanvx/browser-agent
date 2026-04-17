"""
browser.py — Playwright browser controller
Controls a real Chromium browser: open pages, click, type, scroll, scrape.
"""

from playwright.sync_api import sync_playwright, Page, Browser
from bs4 import BeautifulSoup
import time


class BrowserController:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser: Browser = None
        self.page: Page = None

    def start(self):
        """Launch browser."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800}
        )
        self.page = context.new_page()
        print("[Browser] Started ✅")

    def stop(self):
        """Close browser."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("[Browser] Closed.")

    # ── Navigation ─────────────────────────────────────────────────────────────

    def goto(self, url: str) -> str:
        """Navigate to a URL. Returns page title."""
        if not url.startswith("http"):
            url = "https://" + url
        self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(1.5)
        return self.page.title()

    def get_current_url(self) -> str:
        return self.page.url

    # ── Interaction ─────────────────────────────────────────────────────────────

    def click(self, selector: str) -> bool:
        """Click an element by CSS selector or text. Returns True if success."""
        try:
            self.page.click(selector, timeout=5000)
            time.sleep(1)
            return True
        except Exception as e:
            print(f"[Browser] click failed for '{selector}': {e}")
            return False

    def click_text(self, text: str) -> bool:
        """Click element containing specific text."""
        try:
            self.page.get_by_text(text, exact=False).first.click(timeout=5000)
            time.sleep(1)
            return True
        except Exception as e:
            print(f"[Browser] click_text failed for '{text}': {e}")
            return False

    def type_text(self, selector: str, text: str) -> bool:
        """Type into an input field."""
        try:
            self.page.fill(selector, text, timeout=5000)
            return True
        except Exception as e:
            print(f"[Browser] type_text failed for '{selector}': {e}")
            return False

    def press_key(self, key: str):
        """Press a keyboard key (e.g. 'Enter', 'Tab')."""
        self.page.keyboard.press(key)
        time.sleep(0.8)

    def scroll_down(self, amount: int = 500):
        """Scroll down the page."""
        self.page.mouse.wheel(0, amount)
        time.sleep(0.5)

    # ── Scraping ────────────────────────────────────────────────────────────────

    def get_page_text(self, max_chars: int = 8000) -> str:
        """Get clean readable text from the current page."""
        html = self.page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Remove noisy elements
        for tag in soup(["script", "style", "nav", "footer", "head", "noscript", "svg"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Collapse blank lines
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        result = "\n".join(lines)
        return result[:max_chars]

    def get_page_html(self, max_chars: int = 15000) -> str:
        """Get raw HTML (trimmed)."""
        return self.page.content()[:max_chars]

    def get_links(self) -> list[dict]:
        """Get all visible links on the page."""
        links = self.page.eval_on_selector_all(
            "a[href]",
            "els => els.map(e => ({ text: e.innerText.trim(), href: e.href }))"
        )
        return [l for l in links if l["text"] and l["href"].startswith("http")][:30]

    def get_inputs(self) -> list[dict]:
        """Get all input fields on the page."""
        inputs = self.page.eval_on_selector_all(
            "input, textarea, select",
            """els => els.map(e => ({
                tag: e.tagName,
                type: e.type || '',
                name: e.name || '',
                placeholder: e.placeholder || '',
                id: e.id || ''
            }))"""
        )
        return inputs[:20]

    def screenshot(self, path: str = "screenshot.png"):
        """Save a screenshot."""
        self.page.screenshot(path=path)
        print(f"[Browser] Screenshot saved: {path}")

    def wait(self, seconds: float = 1.0):
        time.sleep(seconds)