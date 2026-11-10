
import os
import json
import requests
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://x.com/oomotoya001"
KEYWORD = "崩れ卵"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page(locale="ja-JP")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=30000
    )

    posts = page.locator("article")
    count = min(posts.count(), 3)

    print(f"\n取得した投稿数: {count}")

    for i in range(count):
        post = posts.nth(i)
        text = post.inner_text()

        print(f"\n===== 投稿 {i + 1} =====")
        print(text[:1500])

        if KEYWORD in text:
            print("★ 崩れ卵を検出しました！")

        links = post.locator('a[href*="/status/"]')

        if links.count():
            print("URL:", links.first.get_attribute("href"))

    browser.close()

KEYWORD = "崩れ卵"
POSTS_FILE = Path("posts.json")
STATE_FILE = Path("notified_posts.json")


def load_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def send_telegram(post):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    post_id = str(post["id"])
    message = (
        "🍜 大元家・崩れ卵サービス！\n\n"
        f"{post['text'][:1500]}\n\n"
        f"https://x.com/oomotoya001/status/{post_id}"
    )

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": True,
        },
        timeout=20,
    )
    response.raise_for_status()

    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(result.get("description", "Telegram error"))


def main():
    if not POSTS_FILE.exists():
        raise FileNotFoundError("posts.json がありません")

    posts = load_json(POSTS_FILE, [])
    notified = set(load_json(STATE_FILE, []))

    print(f"取得済み投稿データ: {len(posts)}件")
    new_count = 0

    for post in posts:
        post_id = str(post["id"])
        body = post["text"]

        if KEYWORD not in body or post_id in notified:
            continue

        send_telegram(post)
        notified.add(post_id)

        STATE_FILE.write_text(
            json.dumps(sorted(notified), indent=2),
            encoding="utf-8",
        )

        new_count += 1
        print("通知成功:", post_id)

    print(f"新規通知: {new_count}件")


if __name__ == "__main__":
    main()
