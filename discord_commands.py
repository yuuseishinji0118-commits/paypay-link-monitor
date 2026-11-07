
import os
import re
import json
import urllib.request
import urllib.parse

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]

API = "https://discord.com/api/v10"

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

def send(message):
    request(
        "POST",
        f"/channels/{CHANNEL_ID}/messages",
        {"content": message}
    )

# 監視ユーザーを読み込む
with open("users.txt", encoding="utf-8") as f:
    users = [
        line.strip().lstrip("@")
        for line in f
        if line.strip() and not line.strip().startswith("#")
    ]

# 最後に処理したDiscordメッセージID
cursor_file = "discord_cursor.txt"

try:
    with open(cursor_file, encoding="utf-8") as f:
        cursor = f.read().strip()
except FileNotFoundError:
    cursor = ""

# 初回は過去のコマンドを実行せず、最新メッセージ位置だけ記録
if not cursor:
    messages = request(
        "GET",
        f"/channels/{CHANNEL_ID}/messages?limit=1"
    )
    if messages:
        cursor = messages[0]["id"]
    else:
        cursor = "0"

else:
    messages = request(
        "GET",
        f"/channels/{CHANNEL_ID}/messages?after={cursor}&limit=100"
    )

    messages.sort(key=lambda m: int(m["id"]))

    for msg in messages:
        cursor = msg["id"]

        if msg.get("author", {}).get("bot"):
            continue

        content = msg.get("content", "").strip()
        match = re.fullmatch(
            r"!(add|remove)\s+@?([A-Za-z0-9_]{1,15})",
            content,
            re.IGNORECASE
        )

        if content.lower() == "!list":
            if users:
                send("監視ユーザー一覧:\n" + "\n".join(
                    f"@{u}" for u in users
                ))
            else:
                send("監視ユーザーはまだ登録されていません。")

        elif match:
            action, username = match.groups()

            if action.lower() == "add":
                if username.lower() in [u.lower() for u in users]:
                    send(f"@{username} は既に登録されています。")
                else:
                    users.append(username)
                    send(f"✅ @{username} を監視対象に追加しました。")

            else:
                old_count = len(users)
                users = [
                    u for u in users
                    if u.lower() != username.lower()
                ]

                if len(users) < old_count:
                    send(f"✅ @{username} を監視対象から削除しました。")
                else:
                    send(f"@{username} は登録されていません。")

        else:
            continue

    # ユーザー一覧を保存
    with open("users.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(users) + "\n")

# 処理済み位置を保存
with open(cursor_file, "w", encoding="utf-8") as f:
    f.write(cursor)
