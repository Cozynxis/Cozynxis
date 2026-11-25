import json
import os
import re
import html
from pathlib import Path
from urllib.request import Request, urlopen

def fetch(kind):
    result = []
    page = 1
    while True:
        url = f"https://api.github.com/users/Cozynxis/{kind}?per_page=100&page={page}"
        req = Request(url, headers={"Accept": "application/vnd.github+json", "Authorization": "Bearer " + os.environ["GH_TOKEN"], "User-Agent": "Cozynxis-profile"})
        with urlopen(req, timeout=30) as response:
            batch = json.load(response)
        result.extend(batch)
        if len(batch) < 100:
            return result
        page += 1

def section(kind, title):
    users = fetch(kind)
    lines = [f"<details>", f"<summary>{title} ({len(users)})</summary>", "", '<table>']
    for start in range(0, len(users), 4):
        lines.append("<tr>")
        for user in users[start:start+4]:
            name = html.escape(user["login"], quote=True)
            avatar = html.escape(user["avatar_url"], quote=True)
            url = html.escape(user["html_url"], quote=True)
            lines.append(f'<td align="center"><a href="{url}"><img src="{avatar}" width="56" height="56" alt="{name}" /><br /><sub><b>{name}</b></sub></a></td>')
        lines.append("</tr>")
    lines += ["</table>", ""]
    if not users:
        lines.append("No users yet.")
    lines += ["", "</details>"]
    return "\n".join(lines)

path = Path("README.md")
original = path.read_text(encoding="utf-8")
block = "<!-- COMMUNITY:START -->\n" + section("followers", "👥 View followers") + "\n\n" + section("following", "👤 View following") + "\n<!-- COMMUNITY:END -->"
updated, count = re.subn(r"<!-- COMMUNITY:START -->.*?<!-- COMMUNITY:END -->", lambda _: block, original, flags=re.S)
if count != 1:
    raise RuntimeError("Expected exactly one community block")
path.write_text(updated, encoding="utf-8")
