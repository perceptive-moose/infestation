"""Verify a message-only rewrite, then optionally publish with an exact lease."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

REPOSITORY = "perceptive-moose/infestation"
OLD = "48e5832d2f130646427159149bff3b22a74f304d"
NEW = "d048d86fabc423ef6e5e30ad488efe648d4f1d32"
UPSTREAM = "a6ef414767b61977056df2b033e55334d4ff7180"
TREE = "5dcd4c2cfc990ce52ca8071dbfce4b2800af10fe"
BUNDLE_HASH = "faed4c8db346dfe5655ee2418369841678770674c1396f27e6192c2a2b572e13"
SENTENCE = b"Developed with assistance from ChatGPT (OpenAI)."
TRAILER = b"Co-authored-by: ChatGPT (OpenAI) <noreply@openai.com>"
CANDIDATE = "refs/heads/verified-message-cleanup"
ARCHIVE = "refs/heads/archive/pre-message-cleanup-2026-11-02"
ORIGINAL_ARCHIVE = "refs/heads/archive/pre-history-rewrite-2026-11-02"
ORIGINAL_SQUASH = "292f459b3a11a5ec0fa23f388f11d1e0800a9413"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def text(*args):
    return git(*args).decode().strip()


def verify():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "message-cleanup-map.json").read_text())
    for key, expected in {"repository": REPOSITORY, "old_head": OLD, "new_head": NEW,
                          "upstream": UPSTREAM, "tree": TREE,
                          "candidate_ref": "refs/heads/cleaner-commit-messages",
                          "bundle_sha256": BUNDLE_HASH}.items():
        require(manifest[key] == expected, f"Unexpected manifest {key}")
    bundle = root / "cleaned-history.bundle"
    require(hashlib.sha256(bundle.read_bytes()).hexdigest() == BUNDLE_HASH, "Bundle checksum differs")
    git("bundle", "verify", str(bundle))
    git("fetch", "--no-tags", str(bundle), f"refs/heads/cleaner-commit-messages:{CANDIDATE}")
    require(text("rev-parse", CANDIDATE) == NEW, "Wrong candidate head")
    mapping = {item["old"]: item["new"] for item in manifest["commits"]}
    require(len(manifest["commits"]) == len(mapping) == len(set(mapping.values())) == 26, "Incorrect commit mapping")
    require(mapping.get(OLD) == NEW, "Head mapping differs")
    require(set(text("rev-list", f"{UPSTREAM}..{OLD}").splitlines()) == set(mapping), "Missing original commits")
    require(set(text("rev-list", f"{UPSTREAM}..{NEW}").splitlines()) == set(mapping.values()), "Unexpected replacement commits")
    for old, new in mapping.items():
        headers, message = git("cat-file", "commit", old).split(b"\n\n", 1)
        require(message.count(SENTENCE) == message.count(TRAILER) == 1, "Original attribution differs")
        if b"\n\n" + SENTENCE + b"\n\n" in message:
            cleaned = message.replace(b"\n\n" + SENTENCE + b"\n\n", b"\n\n")
        else:
            cleaned = message.replace(SENTENCE + b"\n", b"")
        require(SENTENCE not in cleaned and cleaned.count(TRAILER) == 1, "Incorrect message cleanup")
        expected_headers = []
        for line in headers.split(b"\n"):
            if line.startswith(b"parent "):
                parent = line[7:].decode()
                line = b"parent " + mapping.get(parent, parent).encode()
            expected_headers.append(line)
        expected = b"\n".join(expected_headers) + b"\n\n" + cleaned
        require(git("cat-file", "commit", new) == expected, f"Unrequested changes in {new}")
    require(text("rev-parse", OLD + "^{tree}") == text("rev-parse", NEW + "^{tree}") == TREE, "File tree changed")
    require(text("merge-base", NEW, UPSTREAM) == UPSTREAM, "Upstream ancestry changed")
    require(text("rev-list", "--count", UPSTREAM) == "170", "Upstream count changed")
    require(text("rev-list", "--count", "--merges", f"{UPSTREAM}..{NEW}") == "8", "Merge count changed")
    original_main = text("rev-list", "--first-parent", f"{UPSTREAM}..{OLD}").splitlines()
    require(text("rev-list", "--first-parent", f"{UPSTREAM}..{NEW}").splitlines() == [mapping[x] for x in original_main], "Merge structure changed")
    require(SENTENCE not in git("log", "--format=%B", NEW), "Redundant sentence remains")
    print("Verified all 26 commits: only the requested sentence and mapped parent IDs changed.")
    print("All trees, other message text, coauthors, identities, dates, and merge structure are intact.")


def remote_heads():
    return {line.split()[1]: line.split()[0] for line in text(
        "ls-remote", "--heads", "origin", "refs/heads/master", ARCHIVE, ORIGINAL_ARCHIVE
    ).splitlines()}


def publish():
    for key, expected in {"GITHUB_REPOSITORY": REPOSITORY,
                          "GITHUB_REF": "refs/heads/history/rewrite-2026-11-02",
                          "GITHUB_EVENT_NAME": "push", "GITHUB_ACTOR": "perceptive-moose"}.items():
        require(os.environ.get(key) == expected, f"Unexpected publication {key}")
    require(text("remote", "get-url", "--push", "origin").removesuffix(".git") == f"https://github.com/{REPOSITORY}", "Wrong destination")
    heads = remote_heads()
    require(heads.get("refs/heads/master") == OLD, "Master moved since preparation")
    require(heads.get(ORIGINAL_ARCHIVE) == ORIGINAL_SQUASH, "Original archive changed")
    require(heads.get(ARCHIVE) in (None, OLD), "Cleanup archive already has different content")
    command = ["git", "push", "--atomic", f"--force-with-lease=refs/heads/master:{OLD}"]
    refs = [f"{CANDIDATE}:refs/heads/master"]
    if ARCHIVE not in heads:
        command.append(f"--force-with-lease={ARCHIVE}:")
        refs.append(f"{OLD}:{ARCHIVE}")
    subprocess.run([*command, "origin", *refs], check=True)
    heads = remote_heads()
    require(heads.get("refs/heads/master") == NEW and heads.get(ARCHIVE) == OLD, "Published refs differ")
    require(heads.get(ORIGINAL_ARCHIVE) == ORIGINAL_SQUASH, "Original archive changed")
    print(f"Published {NEW}; previous master preserved at {ARCHIVE}.")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        Path(summary).write_text(
            "## Commit messages cleaned\n\n"
            f"New master: [{NEW}](https://github.com/{REPOSITORY}/commit/{NEW})\n\n"
            "Removed the redundant assistance sentence from all 26 reconstructed commits. "
            "Coauthor trailers, files, author and committer metadata, and merge structure are unchanged.\n"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    verify()
    if args.publish:
        publish()
    else:
        print("Verification only; no remote changes.")
