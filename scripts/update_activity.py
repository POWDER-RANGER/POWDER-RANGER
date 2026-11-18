#!/usr/bin/env python3
"""Publish a short, verified summary of recent public GitHub activity."""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

USER = "POWDER-RANGER"
START = "<!--START_SECTION:activity-->"
END = "<!--END_SECTION:activity-->"
README = Path("README.md")


def summarize(events):
    lines, seen = [], set()
    for event in events:
        if not isinstance(event, dict):
            continue
        kind = event.get("type")
        repo = event.get("repo") or {}
        repo_name = repo.get("name", "") if isinstance(repo, dict) else ""
        payload = event.get("payload") or {}
        if not isinstance(payload, dict) or not repo_name or repo_name == f"{USER}/{USER}":
            continue
        if (repo_name.count("/") != 1 or any(part in {"", ".", ".."} for part in repo_name.split("/"))\n                or not all(c.isalnum() or c in "-_." for part in repo_name.split("/") for c in part)):
            continue
        url = f"https://github.com/{repo_name}"
        if kind == "PullRequestEvent":
            pr = payload.get("pull_request") or {}
            if payload.get("action") != "closed" or not isinstance(pr, dict) or not pr.get("merged"):
                continue
            number = pr.get("number")
            if not isinstance(number, int) or number < 1:
                continue
            url += f"/pull/{number}"
            label = "Merged a pull request"
        elif kind == "PushEvent":
            url += "/commits"
            label = "Pushed code"
        elif kind == "ReleaseEvent":
            label = "Published a release"
            url += "/releases"
        elif kind == "IssuesEvent" and payload.get("action") == "opened":
            issue = payload.get("issue") or {}
            number = issue.get("number") if isinstance(issue, dict) else None
            if not isinstance(number, int) or number < 1:
                continue
            url += f"/issues/{number}"
            label = "Opened an issue"
        else:
            continue
        key = (kind, repo_name)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"- **{label}** in [{repo_name}](<{url}>)")
        if len(lines) == 6:
            break
    return lines


def replace_section(content, lines):
    if content.count(START) != 1 or content.count(END) != 1:
        raise ValueError("README activity markers missing or duplicated")
    a = content.index(START) + len(START)
    b = content.index(END)
    if a > b:
        raise ValueError("README activity markers out of order")
    if not lines:
        return content
    return content[:a] + "\n" + "\n".join(lines) + "\n" + content[b:]


def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "powder-ranger-profile",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"https://api.github.com/users/{USER}/events/public?per_page=100", headers=headers)
    with urlopen(request, timeout=25) as response:
        events = json.load(response)
    if not isinstance(events, list):
        raise ValueError("Unexpected GitHub events response")
    lines = summarize(events)
    current = README.read_text(encoding="utf-8")
    updated = replace_section(current, lines)
    if updated != current:
        README.write_text(updated, encoding="utf-8")
        print(f"Updated {len(lines)} public activity entries")
    else:
        print("No eligible changes")


if __name__ == "__main__":
    main()
