#!/usr/bin/env python3
import html
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PRODUCTS = {
    "daydreamers_signed": {
        "name": "JxJ DREAMSCAPE Daydreamers Ver. (Signed ver.)",
        "url": "https://seventeenshopus.com/products/jxj-1st-mini-album-dreamscape-daydreamers-ver-signed-ver",
        "marker": "Daydreamers Ver. (Signed ver.)",
    },
    "dreamchasers_signed": {
        "name": "JxJ DREAMSCAPE Dreamchasers Ver. (Signed ver.)",
        "url": "https://seventeenshopus.com/products/jxj-1st-mini-album-dreamscape-dreamchasers-ver-signed-ver",
        "marker": "Dreamchasers Ver. (Signed ver.)",
    },
}

STATE_FILE = Path(__file__).with_name("state.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Cache-Control": "no-cache",
}


def fetch_page(url: str) -> str:
    request = Request(url, headers=HEADERS)
    try:
        with urlopen(request, timeout=20) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status} for {url}")
            raw_html = response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not fetch {url}: {exc}") from exc

    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw_html, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def check_product(product: dict) -> str:
    page_text = fetch_page(product["url"])
    lower_text = page_text.lower()

    if product["marker"].lower() not in lower_text:
        raise RuntimeError(
            f'Unexpected page for {product["name"]}: product marker not found.'
        )

    if "sorry sold out" in lower_text:
        return "sold_out"

    return "available"


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def post_discord(content: str, mention_everyone: bool = False) -> None:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL is not configured.")

    payload = {
        "content": content,
        "allowed_mentions": {
            "parse": ["everyone"] if mention_everyone else []
        },
    }

    request = Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "jxj-stock-watcher/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=15) as response:
            if response.status not in (200, 204):
                raise RuntimeError(
                    f"Discord webhook returned HTTP {response.status}."
                )
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Discord notification failed: {exc}") from exc


def send_restock_alert(restocked: list[dict]) -> None:
    lines = [
        "@everyone",
        "🚨 **JxJ DREAMSCAPE 親簽版補貨！**",
        "",
    ]
    for product in restocked:
        lines.append(f'**{product["name"]}**')
        lines.append(product["url"])
        lines.append("")

    post_discord("\n".join(lines), mention_everyone=True)


def send_heartbeat(current: dict) -> None:
    lines = [
        "🟢 **JxJ Stock Watcher 正常運作**",
        "",
        f"Daydreamers Signed：**{current['daydreamers_signed']}**",
        f"Dreamchasers Signed：**{current['dreamchasers_signed']}**",
        "",
        "本訊息只是心跳確認，不會 @everyone。",
    ]
    post_discord("\n".join(lines), mention_everyone=False)


def main() -> int:
    previous = load_state()
    current = {}

    for key, product in PRODUCTS.items():
        status = check_product(product)
        current[key] = status
        print(f'{product["name"]}: {status}')

    restocked = [
        PRODUCTS[key]
        for key, status in current.items()
        if status == "available" and previous.get(key) != "available"
    ]

    if restocked:
        send_restock_alert(restocked)
        print(f"Restock alert sent for {len(restocked)} product(s).")
    elif os.environ.get("HEARTBEAT_ENABLED", "true").lower() == "true":
        send_heartbeat(current)
        print("Heartbeat notification sent.")

    if current != previous:
        save_state(current)
        print("state.json updated.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
