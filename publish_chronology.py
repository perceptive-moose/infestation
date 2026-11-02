"""Verify a date-only history reconstruction and optionally publish it safely."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

REPOSITORY = "perceptive-moose/infestation"
OLD = "d048d86fabc423ef6e5e30ad488efe648d4f1d32"
NEW = "5abef0257f820bb5f3e9d9a1fca1866ca366b751"
UPSTREAM = "a6ef414767b61977056df2b033e55334d4ff7180"
TREE = "5dcd4c2cfc990ce52ca8071dbfce4b2800af10fe"
BUNDLE_HASH = "03f44b8467da48827b3e92e26d64f75dabea0472acf0038edc027178d2ce82ec"
BUNDLE_REF = "refs/heads/chronological-master"
CANDIDATE = "refs/heads/verified-chronology"
ARCHIVE = "refs/heads/archive/pre-chronology-2026-11-02"
EXISTING_ARCHIVES = {
    "refs/heads/archive/pre-history-rewrite-2026-11-02": "292f459b3a11a5ec0fa23f388f11d1e0800a9413",
    "refs/heads/archive/pre-message-cleanup-2026-11-02": "48e5832d2f130646427159149bff3b22a74f304d",
}
TRAILER = b"Co-authored-by: ChatGPT (OpenAI) <noreply@openai.com>"
REMOVED_SENTENCE = b"Developed with assistance from ChatGPT (OpenAI)."
FEATURE_COUNTS = [3, 2, 3, 3, 2, 1, 3, 1]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def text(*args):
    return git(*args).decode().strip()


def commit(sha):
    headers, message = git("cat-file", "commit", sha).split(b"\n\n", 1)
    return headers.split(b"\n"), message


def identity_date(sha, role):
    headers, _ = commit(sha)
    matches = [line for line in headers if line.startswith(role.encode() + b" ")]
    require(len(matches) == 1, f"Unexpected {role} header in {sha}")
    identity, epoch, offset = matches[0].rsplit(b" ", 2)
    return identity, int(epoch), offset.decode()


def parents(sha):
    return text("show", "-s", "--format=%P", sha).split()


def verify():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "chronology-map.json").read_text())
    for key, expected in {
        "repository": REPOSITORY, "old_head": OLD, "new_head": NEW,
        "upstream": UPSTREAM, "tree": TREE, "candidate_ref": BUNDLE_REF,
        "bundle_sha256": BUNDLE_HASH,
    }.items():
        require(manifest[key] == expected, f"Unexpected manifest {key}")
    bundle = root / "chronological-history.bundle"
    require(hashlib.sha256(bundle.read_bytes()).hexdigest() == BUNDLE_HASH, "Bundle checksum differs")
    git("bundle", "verify", str(bundle))
    git("fetch", "--no-tags", str(bundle), f"{BUNDLE_REF}:{CANDIDATE}")
    require(text("rev-parse", CANDIDATE) == NEW, "Wrong candidate head")

    records = manifest["commits"]
    mapping = {item["old"]: item["new"] for item in records}
    require(len(records) == len(mapping) == len(set(mapping.values())) == 26, "Incorrect commit mapping")
    require(mapping.get(OLD) == NEW, "Head mapping differs")
    require(set(text("rev-list", f"{UPSTREAM}..{OLD}").splitlines()) == set(mapping), "Missing original commits")
    require(set(text("rev-list", f"{UPSTREAM}..{NEW}").splitlines()) == set(mapping.values()), "Unexpected replacement commits")
    require([record["pr"] for record in manifest["pull_requests"]] == list(range(1, 9)), "Unexpected PR sequence")
    require([record["feature_count"] for record in manifest["pull_requests"]] == FEATURE_COUNTS, "Feature counts changed")

    expected_order = []
    old_main = UPSTREAM
    original_main = UPSTREAM
    previous_epoch = identity_date(UPSTREAM, "committer")[1]
    for pr in manifest["pull_requests"]:
        number = pr["pr"]
        url = f"https://github.com/{REPOSITORY}/pull/{number}"
        require(pr["url"] == url, "PR provenance differs")
        uploads = pr["original_uploads"]
        require(bool(uploads) and len(uploads) == len(set(uploads)), "Invalid upload evidence")
        previous_upload = original_main
        source_times = []
        for upload in uploads:
            require(parents(upload) == [previous_upload], "Original upload chain differs")
            source_times.append(identity_date(upload, "committer")[1])
            previous_upload = upload
        require(all(a < b for a, b in zip(source_times, source_times[1:])), "Original upload timestamps are not ordered")
        require(parents(pr["original_squash"]) == [original_main], "Original squash sequence differs")
        require(text("rev-parse", uploads[-1] + "^{tree}") == text("rev-parse", pr["original_squash"] + "^{tree}"), "Upload endpoint differs from squash")
        first, last = source_times[0], source_times[-1]
        _, merge_epoch, offset = identity_date(pr["original_squash"], "committer")
        require(identity_date(pr["original_squash"], "author")[1:] == (merge_epoch, offset), "Original merge author date differs")
        require(offset == "-0500", "Original merge timezone differs")
        require(pr["first_upload"] == text("show", "-s", "--format=%cI", uploads[0]), "First upload date differs")
        require(pr["last_upload"] == text("show", "-s", "--format=%cI", uploads[-1]), "Last upload date differs")
        require(pr["original_merge"] == text("show", "-s", "--format=%cI", pr["original_squash"]), "Merge date differs")
        require(previous_epoch < first <= last < merge_epoch, "PR intervals overlap or cross their merge")

        group = [item for item in records if item["pr"] == number]
        count = pr["feature_count"]
        require([item["kind"] for item in group] == ["feature"] * count + ["merge"], "Curated PR structure differs")
        dates = [last] if count == 1 else [first + (last - first) * i // (count - 1) for i in range(count)]
        dates.append(merge_epoch)
        previous_feature = old_main
        for item, epoch in zip(group, dates):
            old, new = item["old"], item["new"]
            require(item["epoch"] == epoch and item["offset"] == offset, "Timestamp differs from recovered rule")
            require(epoch > previous_epoch, "Reconstructed timestamps are not strictly increasing")
            previous_epoch = epoch
            expected_parents = [old_main, previous_feature] if item["kind"] == "merge" else [previous_feature]
            require(parents(old) == expected_parents, "Previous curated parent structure differs")
            old_headers, message = commit(old)
            require(message.count(TRAILER) == 1 and REMOVED_SENTENCE not in message, "Attribution changed")
            require(url.encode() in message, "Commit has different PR provenance")
            require(item["subject"] == message.split(b"\n", 1)[0].decode(), "Subject differs")
            expected_headers = []
            for line in old_headers:
                if line.startswith(b"parent "):
                    parent = line[7:].decode()
                    line = b"parent " + mapping.get(parent, parent).encode()
                elif line.startswith((b"author ", b"committer ")):
                    identity = line.rsplit(b" ", 2)[0]
                    line = identity + f" {epoch} {offset}".encode()
                expected_headers.append(line)
            expected_raw = b"\n".join(expected_headers) + b"\n\n" + message
            require(git("cat-file", "commit", new) == expected_raw, f"Unrequested metadata or file changes in {new}")
            require(text("show", "-s", "--format=%aI", new) == item["date"] == text("show", "-s", "--format=%cI", new), "Displayed dates differ")
            require(all(identity_date(parent, "committer")[1] < epoch for parent in parents(new)), "Child precedes a parent")
            expected_order.append(old)
            previous_feature = old
        require(group[-1]["new"] == pr["replacement_merge"], "Replacement merge differs")
        require(pr["original_squash"].encode() in commit(group[-1]["old"])[1], "Merge provenance differs")
        require(text("rev-parse", group[-1]["new"] + "^{tree}") == text("rev-parse", pr["original_squash"] + "^{tree}"), "PR snapshot differs")
        old_main = group[-1]["old"]
        original_main = pr["original_squash"]

    require(old_main == OLD and original_main == EXISTING_ARCHIVES["refs/heads/archive/pre-history-rewrite-2026-11-02"], "Final original heads differ")
    require([item["old"] for item in records] == expected_order, "Manifest chronology differs")
    require(text("rev-list", "--reverse", f"{UPSTREAM}..{NEW}").splitlines() == [mapping[sha] for sha in expected_order], "Default Git chronological order differs")
    require(text("rev-parse", OLD + "^{tree}") == text("rev-parse", NEW + "^{tree}") == TREE, "Final file tree changed")
    require(text("merge-base", NEW, UPSTREAM) == UPSTREAM and text("rev-list", "--count", UPSTREAM) == "170", "Upstream history changed")
    require(text("rev-list", "--count", "--merges", f"{UPSTREAM}..{NEW}") == "8", "Merge count changed")
    original_mainline = text("rev-list", "--first-parent", f"{UPSTREAM}..{OLD}").splitlines()
    require(text("rev-list", "--first-parent", f"{UPSTREAM}..{NEW}").splitlines() == [mapping[sha] for sha in original_mainline], "Mainline graph changed")
    print("Verified all 26 commits: only author/committer dates and mapped parent IDs changed.")
    print("Source-derived dates are strictly chronological; all messages, coauthors, identities, trees, and 18-feature/8-merge structure are intact.")


def remote_heads():
    return {line.split()[1]: line.split()[0] for line in text(
        "ls-remote", "--heads", "origin", "refs/heads/master", ARCHIVE, *EXISTING_ARCHIVES
    ).splitlines()}


def publish():
    for key, expected in {
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_REF": "refs/heads/history/rewrite-2026-11-02",
        "GITHUB_EVENT_NAME": "push", "GITHUB_ACTOR": "perceptive-moose",
    }.items():
        require(os.environ.get(key) == expected, f"Unexpected publication {key}")
    require(text("remote", "get-url", "--push", "origin").removesuffix(".git") == f"https://github.com/{REPOSITORY}", "Wrong destination")
    heads = remote_heads()
    require(heads.get("refs/heads/master") == OLD, "Master moved since preparation")
    require(all(heads.get(ref) == sha for ref, sha in EXISTING_ARCHIVES.items()), "Existing archive changed")
    require(heads.get(ARCHIVE) in (None, OLD), "Chronology archive already has different content")
    command = ["git", "push", "--atomic", f"--force-with-lease=refs/heads/master:{OLD}"]
    refs = [f"{CANDIDATE}:refs/heads/master"]
    if ARCHIVE not in heads:
        command.append(f"--force-with-lease={ARCHIVE}:")
        refs.append(f"{OLD}:{ARCHIVE}")
    subprocess.run([*command, "origin", *refs], check=True)
    heads = remote_heads()
    require(heads.get("refs/heads/master") == NEW and heads.get(ARCHIVE) == OLD, "Published refs differ")
    require(all(heads.get(ref) == sha for ref, sha in EXISTING_ARCHIVES.items()), "Existing archive changed")
    print(f"Published {NEW}; previous master preserved at {ARCHIVE}.")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        Path(summary).write_text(
            "## Commit chronology restored\n\n"
            f"New master: [{NEW}](https://github.com/{REPOSITORY}/commit/{NEW})\n\n"
            "Restored the eight original merge timestamps and placed the 18 curated feature commits "
            "in order within their original PR upload intervals. Feature dates are approximations. "
            "All messages, coauthors, identities, file trees, and merge structure are unchanged.\n"
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
