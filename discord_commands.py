import os
import json
import urllib.request

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]

API = "https://discord.com/api/v10"
PANEL_MARKER = "PayPay監視ユーザー管理パネル"

def request(method, path, data=None):
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "User-Agent": "PayPayManager/1.0"
    }

    body = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(
        API + path,
        data=body,
        headers=headers,
        method=method
    )

    with urllib.request.urlopen(req, timeout=20) as res:
        result = res.read()
        return json.loads(result) if result else None


def create_panel():
    messages = request(
        "GET",
        f"/channels/{CHANNEL_ID}/messages?limit=100"
    )

    # 既にパネルがあれば重複投稿しない
    for msg in messages:
        if (
            msg.get("author", {}).get("bot")
            and msg.get("content", "").startswith(PANEL_MARKER)
        ):
            return

    panel = {
        "content": (
            PANEL_MARKER
            + "\n下のボタンから監視ユーザーを管理できます。"
        ),
        "components": [
            {
                "type": 1,
                "components": [
                    {
                        "type": 2,
                        "style": 1,
                        "label": "ユーザーを追加",
                        "custom_id": "add"
                    },
                    {
                        "type": 2,
                        "style": 4,
                        "label": "ユーザーを削除",
                        "custom_id": "remove"
                    },
                    {
                        "type": 2,
                        "style": 3,
                        "label": "登録一覧を見る",
                        "custom_id": "list"
                    }
                ]
            }
        ]
    }

    request(
        "POST",
        f"/channels/{CHANNEL_ID}/messages",
        panel
    )


create_panel()
print("管理パネルの確認が完了しました")
