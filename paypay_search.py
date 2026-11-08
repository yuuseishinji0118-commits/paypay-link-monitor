import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

WEBHOOK = os.environ["DISCORD_WEBHOOK"]

QUERIES = [
    '"pay.paypay.ne.jp"',
    'paypay.ne.jp PayPay',
]

def fetch_rss(query):
    url = (
        "https://news.google.com/rss/search?q="
        + urllib.parse.quote(query + " site:x.com")
        + "&hl=ja&gl=JP&ceid=JP:ja"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req, timeout=20) as res:
        return ET.fromstring(res.read())

def send_discord(message):
    data = json.dumps({"content": message}).encode()

    req = urllib.request.Request(
        WEBHOOK,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    urllib.request.urlopen(req, timeout=20).close()

seen_file = "paypay_seen.json"

try:
    with open(seen_file, encoding="utf-8") as f:
        seen = set(json.load(f))
except FileNotFoundError:
    seen = set()

found = []

for query in QUERIES:
    try:
        root = fetch_rss(query)

        for item in root.findall(".//item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")

            text = title + " " + link

            urls = re.findall(
                r"https?://pay\.paypay\.ne\.jp/[^\s<>&]+",
                text
            )

            for url in urls:
                if url not in seen:
                    found.append((url, title, link))
                    seen.add(url)

    except Exception as e:
        print("Search error:", e)

for url, title, source in found:
    send_discord(
        "🎁 PayPayリンクを検知！\n"
        + title + "\n"
        + url + "\n"
        + source
    )

with open(seen_file, "w", encoding="utf-8") as f:
    json.dump(list(seen), f, ensure_ascii=False)

print("検知件数:", len(found))
