import json, os
import audit
import github_api as gh
from classifier import Classifier
from retrieval import DocsIndex
from gemma import write_reply

LIVE = os.getenv("MB_LIVE", "false").lower() == "true"      # dry-run unless exactly "true"
CLS_T = float(os.getenv("MB_CLS_THRESHOLD", "0.8"))
DOC_T = float(os.getenv("MB_DOC_THRESHOLD", "0.70"))
DOCS = os.getenv("MB_DOCS_PATH", "README.md")
FORWARD_ABSTAIN = os.getenv("MB_FORWARD_ABSTAIN", "true").lower() == "true"
PREFIX = "mb:"
FWD_LABEL = "mb:needs-maintainer"
MARKER = "<!-- maintainerbot -->"


def forward_comment(why, queue_no):
    where = (f"It is on the maintainers' checklist (#{queue_no})." if queue_no
             else "It is on the maintainers' checklist.")
    return f"{MARKER}\n**Forwarded to maintainer.** {why} {where}\n\n_Automated reply from MaintainerBot._"


def finish(num, title, rec, labels, actions, reply, forward, reason):
    """forward = None, or (sentence for the comment, short reason for the checklist)."""
    if forward:
        labels = labels + [FWD_LABEL]
        actions = actions + [f"label:{FWD_LABEL}", "comment:forwarded-to-maintainer", "queue:add"]
    if LIVE:
        if labels:
            gh.add_labels(num, labels)
        if forward:
            queue_no = gh.add_to_queue(num, title, forward[1])
            rec["queue_issue"] = queue_no
            reply = forward_comment(forward[0], queue_no)
        if reply:
            gh.comment(num, reply)
    audit.log(**rec, action=actions or "none",
              reason=reason + ("" if LIVE else " (dry-run: nothing posted)"))


def main():
    event = json.load(open(os.environ["GITHUB_EVENT_PATH"]))
    issue = event["issue"]
    num, title, body = issue["number"], issue["title"], issue.get("body") or ""

    if "pull_request" in issue or issue["user"]["type"] == "Bot":
        audit.log(issue=num, action="none", reason="PR or bot author", live=LIVE)
        return

    label, conf = Classifier().predict(f"{title}\n\n{body}")
    rec = {"issue": num, "title": title[:120], "label": label,
           "confidence": round(conf, 3), "live": LIVE}

    if conf < CLS_T:
        reason = f"abstained: confidence below {CLS_T}"
        if FORWARD_ABSTAIN:
            finish(num, title, rec, [], [], None,
                   ("I wasn't confident enough to classify this.", "low confidence"), reason)
        else:
            finish(num, title, rec, [], [], None, None, reason)
        return

    labels, actions = [f"{PREFIX}{label}"], [f"label:{PREFIX}{label}"]
    reply, forward = None, None
    if label == "question":
        chunk, score = DocsIndex(open(DOCS).read()).search(f"{title}\n{body[:500]}")
        rec["retrieval_score"] = round(score, 3)
        rec["section"] = chunk["heading"]
        if score >= DOC_T:
            text, source = write_reply(title, chunk)
            rec["reply_source"] = source
            if text:
                reply = (f"{MARKER}\n{text}\n\n"
                         f"_Automated reply from MaintainerBot (section: {chunk['heading']})._")
                actions.append("comment:docs-answer")
                rec["reply_preview"] = text[:300]
        if not reply:
            rec["note"] = "not documented: forwarded to maintainer"
            forward = ("This doesn't seem to be covered in the docs.", "not documented")

    finish(num, title, rec, labels, actions, reply, forward, "confident prediction")


if __name__ == "__main__":
    main()
