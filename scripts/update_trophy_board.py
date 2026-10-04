#!/usr/bin/env python3
"""Generate a repo-native GitHub trophy/achievement SVG for the profile README.

The renderer uses GitHub's public REST API and creates a static SVG committed
into this repository. It intentionally does not depend on a hosted image
renderer.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from html import escape
from pathlib import Path


API = "https://api.github.com"
USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "POWDER-RANGER")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = Path(os.environ.get("TROPHY_OUTPUT", ".github/assets/trophy.svg"))


def get_json(path: str) -> dict:
    req = urllib.request.Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
            "User-Agent": "POWDER-RANGER-profile-trophy",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def get_repositories() -> list[dict]:
    repos: list[dict] = []
    page = 1
    while True:
        payload = get_json(
            f"/users/{urllib.parse.quote(USERNAME)}/repos"
            f"?type=all&per_page=100&page={page}&sort=updated"
        )
        if not payload:
            break
        repos.extend(payload)
        if len(payload) < 100:
            break
        page += 1
        if page > 20:
            break
    return repos


def search_count(query: str) -> int:
    q = urllib.parse.quote(query, safe="")
    return int(get_json(f"/search/issues?q={q}").get("total_count", 0))


def commit_count() -> int:
    q = urllib.parse.quote(f"author:{USERNAME}", safe="")
    try:
        return int(get_json(f"/search/commits?q={q}&per_page=1").get("total_count", 0))
    except Exception:
        return 0


def tier(value: int, thresholds: list[tuple[str, int]]) -> str:
    for label, minimum in thresholds:
        if value >= minimum:
            return label
    return "C"


THRESHOLDS = {
    "COMMITS": [("SSS", 5000), ("SS", 2500), ("S", 1000), ("AAA", 500), ("AA", 250), ("A", 100), ("B", 50), ("C", 1)],
    "STARS": [("SSS", 100), ("SS", 50), ("S", 25), ("AAA", 10), ("AA", 5), ("A", 1)],
    "FOLLOWERS": [("SSS", 250), ("SS", 100), ("S", 50), ("AAA", 25), ("AA", 10), ("A", 5), ("B", 1)],
    "REPOSITORIES": [("SSS", 100), ("SS", 50), ("S", 25), ("AAA", 10), ("AA", 5), ("A", 1)],
    "PULL REQUESTS": [("SSS", 100), ("SS", 50), ("S", 25), ("AAA", 10), ("AA", 5), ("A", 1)],
    "ISSUES": [("SSS", 50), ("SS", 25), ("S", 10), ("AAA", 5), ("AA", 1)],
}


def cup_icon(cx: int, cy: int) -> str:
    return (
        f'<g transform="translate({cx - 24} {cy - 24})">'
        '<path d="M12 8h24v12c0 9-5.5 16-12 16S12 29 12 20V8Z" '
        'fill="none" stroke="#E31C23" stroke-width="3" stroke-linejoin="miter"/>'
        '<path d="M12 12H7v7c0 5 3 8 8 8M36 12h5v7c0 5-3 8-8 8" '
        'fill="none" stroke="#E31C23" stroke-width="3"/>'
        '<path d="M18 40h12M15 45h18" stroke="#E31C23" stroke-width="3"/>'
        '</g>'
    )


def card(x: int, y: int, label: str, value: int, rank: str) -> str:
    display_value = f"{value:,}"
    return (
        f'<g transform="translate({x} {y})">'
        '<rect width="300" height="118" rx="4" fill="#120000" stroke="#4A1010"/>'
        f'{cup_icon(34, 46)}'
        f'<text x="72" y="31" fill="#A08080" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11" letter-spacing="1.5">{escape(label)}</text>'
        f'<text x="72" y="65" fill="#F2E8E8" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="25" font-weight="700">{escape(display_value)}</text>'
        '<rect x="218" y="16" width="64" height="30" rx="3" fill="#1A0000" stroke="#8B0000"/>'
        f'<text x="250" y="37" text-anchor="middle" fill="#E31C23" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="14" font-weight="700">{escape(rank)}</text>'
        '<text x="72" y="93" fill="#A08080" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="9" letter-spacing="1">ACHIEVEMENT TIER</text>'
        '</g>'
    )


def render(stats: dict[str, int]) -> str:
    cards = [
        ("COMMITS", stats["commits"]),
        ("STARS", stats["stars"]),
        ("FOLLOWERS", stats["followers"]),
        ("REPOSITORIES", stats["repos"]),
        ("PULL REQUESTS", stats["prs"]),
        ("ISSUES", stats["issues"]),
    ]
    positions = [(20, 108), (330, 108), (640, 108), (20, 238), (330, 238), (640, 238)]
    body = "
".join(
        card(x, y, label, value, tier(value, THRESHOLDS[label]))
        for (label, value), (x, y) in zip(cards, positions)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="385" viewBox="0 0 960 385" role="img" aria-labelledby="title desc">
  <title id="title">POWDER-RANGER GitHub Trophy Board</title>
  <desc id="desc">Repo-native GitHub achievement board generated by GitHub Actions.</desc>
  <rect width="960" height="385" rx="8" fill="#0A0000"/>
  <rect x="0.5" y="0.5" width="959" height="384" rx="8" fill="none" stroke="#4A1010"/>
  <text x="20" y="38" fill="#E31C23" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="22" font-weight="700" letter-spacing="1">GITHUB TROPHIES // POWDER-RANGER</text>
  <text x="20" y="64" fill="#A08080" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11">REPO-NATIVE • ACTION-GENERATED • NO EXTERNAL IMAGE HOST</text>
  {body}
  <text x="20" y="376" fill="#A08080" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="9">TIER THRESHOLDS ARE THIS PROFILE'S LOCAL ACHIEVEMENT SCALE • REFRESHED FROM GITHUB API</text>
</svg>
'''


def main() -> int:
    try:
        user = get_json(f"/users/{urllib.parse.quote(USERNAME)}")
        repos = get_repositories()
        stars = sum(int(r.get("stargazers_count", 0) or 0) for r in repos)
        stats = {
            "commits": commit_count(),
            "stars": stars,
            "followers": int(user.get("followers", 0) or 0),
            "repos": int(user.get("public_repos", 0) or 0),
            "prs": search_count(f"author:{USERNAME} is:pr"),
            "issues": search_count(f"author:{USERNAME} is:issue"),
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(render(stats), encoding="utf-8")
        print(json.dumps({"username": USERNAME, **stats, "output": str(OUT)}))
        return 0
    except Exception as exc:
        print(f"trophy generation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
