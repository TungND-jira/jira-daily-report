import os
import requests
from datetime import datetime

# Config
JIRA_DOMAIN = os.environ["JIRA_DOMAIN"]
API_TOKEN = os.environ["JIRA_API_TOKEN"]
EMAIL = os.environ["JIRA_EMAIL"]
HEADERS = {
    "Authorization": f"Basic {requests.auth._basic_auth_str(EMAIL, API_TOKEN)}",
    "Accept": "application/json"
}

# Webhook Google Chat
WEBHOOK_URL = os.environ["GOOGLE_CHAT_URL"]

# Các JQL filter
filters = {
    "🔥 Bug impact lớn": 'project = "KR2" AND status in (Done, Rollback) AND type = "Release plan" AND summary ~ "All"',
    "🤬 Customer Push": 'project = KR2 and labels = KVR_Technical'
}

# Lấy số lượng issue từ từng filter
def get_issue_count(jql):
    url = f"{JIRA_DOMAIN}/rest/api/3/search"
    params = {"jql": jql, "maxResults": 0}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()["total"]

# Tạo nội dung báo cáo
def build_message():
    today = datetime.now().strftime("%d/%m/%Y")
    message = f"📋 *Daily Report {today}*\n"
    for title, jql in filters.items():
        count = get_issue_count(jql)
        message += f"{title}:  {count}\n"
    return message.strip()

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
