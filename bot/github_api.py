import os, re, requests
from urllib.parse import quote

API = "https://api.github.com"
REPO = os.environ.get("GITHUB_REPOSITORY", "")

QUEUE_MARKER = "<!-- maintainerbot-queue -->"
QUEUE_TITLE = "MaintainerBot: needs a maintainer"
QUEUE_LABEL = "mb:queue"
QUEUE_HEADER = (f"{QUEUE_MARKER}\nIssues the bot could not answer, forwarded to maintainers. "
                "Tick a box once you have dealt with it.\n\n")


def _h():
    return {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "Accept": "application/vnd.github+json"}


def add_labels(num, labels):
    requests.post(f"{API}/repos/{REPO}/issues/{num}/labels", headers=_h(),
                  json={"labels": labels}, timeout=30).raise_for_status()


def comment(num, body):
    requests.post(f"{API}/repos/{REPO}/issues/{num}/comments", headers=_h(),
                  json={"body": body}, timeout=30).raise_for_status()


def remove_label(num, label):
    r = requests.delete(f"{API}/repos/{REPO}/issues/{num}/labels/{quote(label, safe='')}",
                        headers=_h(), timeout=30)
    if r.status_code != 404:
        r.raise_for_status()


def delete_label(label):
    requests.delete(f"{API}/repos/{REPO}/labels/{quote(label, safe='')}",
                    headers=_h(), timeout=30)


def delete_comment(cid):
    requests.delete(f"{API}/repos/{REPO}/issues/comments/{cid}",
                    headers=_h(), timeout=30).raise_for_status()


def paged(url, params=None):
    p = dict(params or {})
    p["per_page"] = 100
    page = 1
    while True:
        p["page"] = page
        r = requests.get(url, headers=_h(), params=p, timeout=30)
        r.raise_for_status()
        items = r.json()
        if not items:
            return
        yield from items
        page += 1


# ---------------------------------------------------------------- maintainer checklist
def _clean(s, n=90):
    """Titles are untrusted: drop characters that could ping users or break the markdown."""
    return re.sub(r"[@\[\]<>`|\r\n]+", " ", s).strip()[:n]


def find_queue():
    for it in paged(f"{API}/repos/{REPO}/issues", {"labels": QUEUE_LABEL, "state": "open"}):
        if QUEUE_MARKER in (it.get("body") or ""):
            return it
    return None


def create_queue():
    r = requests.post(f"{API}/repos/{REPO}/issues", headers=_h(), timeout=30,
                      json={"title": QUEUE_TITLE, "body": QUEUE_HEADER, "labels": [QUEUE_LABEL]})
    r.raise_for_status()
    return r.json()


def add_to_queue(num, title, reason):
    """Append '- [ ] #N title (reason)' to the checklist issue. Returns its issue number."""
    q = find_queue() or create_queue()
    body = q.get("body") or QUEUE_HEADER
    if re.search(rf"- \[[ xX]\] #{num} ", body):        # already listed
        return q["number"]
    body = body.rstrip("\n") + f"\n- [ ] #{num} {_clean(title)} ({reason})\n"
    requests.patch(f"{API}/repos/{REPO}/issues/{q['number']}", headers=_h(),
                   json={"body": body}, timeout=30).raise_for_status()
    return q["number"]


def clear_queue(number):
    """Used by undo only: empty the checklist and close it."""
    requests.patch(f"{API}/repos/{REPO}/issues/{number}", headers=_h(), timeout=30,
                   json={"body": QUEUE_HEADER + "_Cleared by undo._\n", "state": "closed"}
                   ).raise_for_status()
