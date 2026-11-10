
import os
import requests

token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]

response = requests.post(
    f"https://api.telegram.org/bot{token}/sendMessage",
    json={
        "chat_id": chat_id,
        "text": "🍜 大元家監視Bot\nGitHub Actionsからの通知テスト成功！",
    },
    timeout=20,
)

response.raise_for_status()
result = response.json()

if not result.get("ok"):
    raise RuntimeError(result.get("description", "Telegram API error"))

print("Telegram notification sent successfully.")
