import requests
import os
from requests.auth import HTTPBasicAuth
from datetime import datetime

JIRA_DOMAIN = os.environ["JIRA_DOMAIN"]
API_TOKEN = os.environ["JIRA_API_TOKEN"]
EMAIL = os.environ["JIRA_EMAIL"]
WEBHOOK_URL = os.environ["GOOGLE_CHAT_URL"]
HEADERS = {
    "Authorization": f"Basic {requests.auth._basic_auth_str(EMAIL, API_TOKEN)}",
    "Accept": "application/json"
}

filters = {
    "🔥 Task đã làm": "project = KR2 AND type = Task AND status = Done AND created >= 2025-01-01 AND created <= 2026-01-01"
}

def fetch_issues(jql, max_results=50):
    issues = []
    start_at = 0
    while True:
        params = {
            "jql":       jql,
            "startAt":   start_at,
            "maxResults": max_results,
            "fields":    "key,summary"
        }
        resp = requests.get(
            f"{JIRA_DOMAIN}/rest/api/3/search",
            auth=auth,
            params=params,
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("issues", [])
        issues.extend(batch)

        if start_at + max_results >= data.get("total", 0):
            break
        start_at += max_results
    return issues
def build_message(filters):
    today = datetime.now().strftime("%d/%m/%Y")
    lines = [f"📋 *Daily Report {today}*"]
    for title, jql in filters.items():
        issues = fetch_issues(jql)
        lines.append(f"\n*{title}* — {len(issues)} tickets")
        for issue in issues:
            key     = issue["key"]
            summary = issue["fields"]["summary"]
            lines.append(f"- {key}: {summary}")
    return "\n".join(lines)
def send_to_google_chat(message):
    requests.post(WEBHOOK_URL, json={"text": message}, timeout=5)

# Gửi lên Google Chat
def send_to_google_chat(message):
    payload = {"text": message}
    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        print("✅ Gửi thành công!")
    else:
        print(f"❌ Lỗi gửi: {response.text}")

# Run
if __name__ == "__main__":
    msg = build_message()
    send_to_google_chat(msg)
