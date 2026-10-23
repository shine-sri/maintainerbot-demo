import argparse
import github_api as gh

MARKER = "<!-- maintainerbot -->"
ap = argparse.ArgumentParser()
ap.add_argument("--yes", action="store_true", help="actually remove; otherwise just list")
a = ap.parse_args()

labels = [l["name"] for l in gh.paged(f"{gh.API}/repos/{gh.REPO}/labels")
          if l["name"].startswith("mb:")]
comments = [c for c in gh.paged(f"{gh.API}/repos/{gh.REPO}/issues/comments")
            if MARKER in (c["body"] or "")]
queues = [i for i in gh.paged(f"{gh.API}/repos/{gh.REPO}/issues",
                              {"labels": gh.QUEUE_LABEL, "state": "all"})
          if gh.QUEUE_MARKER in (i["body"] or "")]
print(f"bot labels: {labels}\nbot comments: {[c['id'] for c in comments]}\n"
      f"checklist issues: {[q['number'] for q in queues]}")
if not a.yes:
    print("Nothing removed. Re-run with --yes to undo.")
    raise SystemExit

for q in queues:
    gh.clear_queue(q["number"])          # empties the checklist and closes it (undo is human-run)
for l in labels:
    for issue in gh.paged(f"{gh.API}/repos/{gh.REPO}/issues", {"labels": l, "state": "all"}):
        gh.remove_label(issue["number"], l)
    gh.delete_label(l)
for c in comments:
    gh.delete_comment(c["id"])
print("Undone.")
