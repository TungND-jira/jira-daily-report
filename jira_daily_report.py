import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
JIRA_DOMAIN = ""
EMAIL       = ""
API_TOKEN   = ""
WEBHOOK_URL = ""
auth = HTTPBasicAuth(EMAIL, API_TOKEN)
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
if name == "main":
    # Định nghĩa các filter JQL của bạn
    filters = {
        "🔥 Task đã làm": "created >= 2025-01-01 AND created <= 2026-01-01 order by created DESC",
        # …thêm filter khác nếu cần
    }
    report = build_message(filters)
    send_to_google_chat(report)
