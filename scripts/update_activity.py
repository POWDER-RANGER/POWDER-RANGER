#!/usr/bin/env python3
"""Update the public activity section from GitHub's public events API."""
import json
import os
import pathlib
import urllib.request

README = pathlib.Path("README.md")
START = "<!--START_SECTION:activity-->"
END = "<!--END_SECTION:activity-->"
USER = "POWDER-RANGER"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
headers = {"Accept": "application/vnd.github+json", "User-Agent": "powder-ranger-profile"}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

request = urllib.request.Request(
    f"https://api.github.com/users/{USER}/events/public?per_page=100", headers=headers
)
with urllib.request.urlopen(request, timeout=20) as response:
    events = json.load(response)

rows = []
seen = set()
for event in events:
    kind = event.get("type")
    repo = event.get("repo", {}).get("name", "")
    payload = event.get("payload", {})
    if not repo or kind not in {"PullRequestEvent", "PushEvent", "ReleaseEvent", "IssuesEvent"}:
        continue
    if repo == f"{USER}/{USER}" or repo in seen:
        continue
    if kind == "PullRequestEvent":
        pr = payload.get("pull_request", {})
        action = payload.get("action", "")
        if action != "closed" or not pr.get("merged"):
            continue
        title = "Merged a pull request"
        url = pr.get("html_url", f"https://github.com/{repo}")
    elif kind == "PushEvent":
        title = "Pushed commits"
        url = f"https://github.com/{repo}/commits"
    elif kind == "ReleaseEvent":
        title = "Published a release"
        url = payload.get("release", {}).get("html_url", f"https://github.com/{repo}")
    else:
        if payload.get("action") != "opened":
            continue
        title = "Opened an issue"
        url = payload.get("issue", {}).get("html_url", f"https://github.com/{repo}")
    if not url.startswith("https://github.com/"):
        continue
    rows.append(f"- **{title}** in [{repo}](<{url}>)")
    seen.add(repo)
    if len(rows) >= 6:
        break

if not rows:
    print("No eligible public activity; preserving existing README section.")
    raise SystemExit(0)

content = README.read_text(encoding="utf-8")
if content.count(START) != 1 or content.count(END) != 1:
    raise SystemExit("README activity markers missing or duplicated")
a = content.index(START) + len(START)
b = content.index(END)
if a > b:
    raise SystemExit("Activity markers out of order")
updated = content[:a] + "\n" + "\n".join(rows) + "\n" + content[b:]
if updated != content:
    README.write_text(updated, encoding="utf-8")
    print("Updated public activity.")
else:
    print("No changes.")
