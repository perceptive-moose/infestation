"""Verify the prepared history and, only with --publish, replace master."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


REPOSITORY = "perceptive-moose/infestation"
OLD_HEAD = "292f459b3a11a5ec0fa23f388f11d1e0800a9413"
NEW_HEAD = "48e5832d2f130646427159149bff3b22a74f304d"
UPSTREAM = "a6ef414767b61977056df2b033e55334d4ff7180"
FINAL_TREE = "5dcd4c2cfc990ce52ca8071dbfce4b2800af10fe"
BUNDLE_SHA256 = "bd0abdf491f4393123e6e5efd3aac6d41350f749d7c3f69602ac85133447ad35"
ARCHIVE = "refs/heads/archive/pre-history-rewrite-2026-11-02"
TRAILER = "Co-authored-by: ChatGPT (OpenAI) <noreply@openai.com>"
LOCAL_CANDIDATE = "refs/heads/verified-history-candidate"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError(reason)


def remote_heads() -> dict[str, str]:
    lines = git("ls-remote", "--heads", "origin", "refs/heads/master", ARCHIVE).splitlines()
    return {line.split()[1]: line.split()[0] for line in lines}


def verify() -> dict:
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "history-rewrite-map.json").read_text())
    require(manifest["repository"] == REPOSITORY, "Wrong repository in manifest")
    require(manifest["expected_old_head"] == OLD_HEAD, "Unexpected original head")
    require(manifest["candidate_head"] == NEW_HEAD, "Unexpected candidate head")
    require(manifest["upstream"] == UPSTREAM, "Unexpected upstream boundary")
    require(manifest["candidate_tree"] == FINAL_TREE, "Unexpected final file tree")
    require(manifest["coauthor_trailer"] == TRAILER, "Unexpected AI attribution")
    require(manifest["candidate_ref"] == "refs/heads/reconstructed-master", "Unexpected bundle ref")
    bundle = root / "rewritten-history.bundle"
    require(hashlib.sha256(bundle.read_bytes()).hexdigest() == BUNDLE_SHA256 == manifest["bundle_sha256"], "Bundle checksum mismatch")
    git("bundle", "verify", str(bundle))
    git("fetch", "--no-tags", str(bundle), f"refs/heads/reconstructed-master:{LOCAL_CANDIDATE}")
    require(git("rev-parse", LOCAL_CANDIDATE) == NEW_HEAD, "Bundle contains a different head")
    require(git("rev-parse", f"{NEW_HEAD}^{{tree}}") == FINAL_TREE, "Final tree differs")
    require(git("rev-parse", f"{OLD_HEAD}^{{tree}}") == FINAL_TREE, "Original head tree differs")
    git("diff", "--exit-code", OLD_HEAD, NEW_HEAD)
    require(git("merge-base", NEW_HEAD, UPSTREAM) == UPSTREAM, "Upstream ancestry changed")
    require(int(git("rev-list", "--count", UPSTREAM)) == 170, "Upstream history count changed")
    expected_commits = set()
    old_squashes = set()
    expected_merges = []
    previous_main = UPSTREAM
    previous_original = UPSTREAM
    records = manifest["pull_requests"]
    require([r["pr"] for r in records] == list(range(1, 9)), "PR sequence incomplete")
    for record in records:
        pr_url = f"https://github.com/{REPOSITORY}/pull/{record['pr']}"
        require(record["url"] == pr_url, "Incorrect PR provenance")
        require(record["original_base"] == previous_original, "Original PR order changed")
        original_squash = record["original_squash"]
        old_squashes.add(original_squash)
        original_author = git("show", "-s", "--format=%an%x00%ae%x00%aI", original_squash)
        previous_feature = previous_main
        for item in record["commits"]:
            sha = item["sha"]
            require(git("show", "-s", "--format=%P", sha).split() == [previous_feature], "Feature parent mismatch")
            require(git("rev-parse", f"{sha}^{{tree}}") == item["tree"], "Feature snapshot mismatch")
            require(git("show", "-s", "--format=%an%x00%ae%x00%aI", sha) == original_author, "Human author or original author date changed")
            message = git("show", "-s", "--format=%B", sha)
            require(message.endswith(TRAILER) and message.count(TRAILER) == 1, "Missing or duplicated coauthor trailer")
            require(pr_url in message and "Developed with assistance from ChatGPT (OpenAI)." in message, "Missing provenance or AI disclosure")
            expected_commits.add(sha)
            previous_feature = sha
        merge = record["replacement_merge"]
        expected_parents = [previous_main, previous_feature]
        require(record["merge_parents"] == expected_parents, "Manifest merge parents mismatch")
        require(git("show", "-s", "--format=%P", merge).split() == expected_parents, "Merge parent mismatch")
        tree = git("rev-parse", f"{merge}^{{tree}}")
        require(tree == record["tree"] == git("rev-parse", f"{original_squash}^{{tree}}"), "Merge snapshot differs from original squash")
        require(git("rev-parse", f"{previous_feature}^{{tree}}") == tree, "Merge adds unreviewed changes")
        require(git("show", "-s", "--format=%an%x00%ae%x00%aI", merge) == original_author, "Merge human author or author date changed")
        message = git("show", "-s", "--format=%B", merge)
        require(message.endswith(TRAILER) and message.count(TRAILER) == 1, "Merge attribution missing")
        require(pr_url in message and original_squash in message, "Merge provenance missing")
        expected_commits.add(merge)
        expected_merges.append(merge)
        previous_main = merge
        previous_original = original_squash
    require(previous_main == NEW_HEAD and previous_original == OLD_HEAD, "Wrong final heads")
    actual_commits = set(git("rev-list", f"{UPSTREAM}..{NEW_HEAD}").splitlines())
    require(actual_commits == expected_commits and len(actual_commits) == 26, "Candidate contains unexpected commits")
    require(old_squashes.isdisjoint(actual_commits), "Old squash commits re-entered canonical ancestry")
    require(git("rev-list", "--first-parent", "--reverse", f"{UPSTREAM}..{NEW_HEAD}").splitlines() == expected_merges, "Mainline merge sequence differs")
    require(manifest["feature_commit_count"] == 18 and manifest["merge_count"] == 8, "Wrong feature/merge counts")
    print("Verified 18 attributed feature commits, 8 real merges, all original PR snapshots, and identical final files.")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true", help="Replace master using an exact force-with-lease after verification")
    args = parser.parse_args()
    verify()
    if not args.publish:
        print("Verification only: no remote changes made.")
        return
    require(os.environ.get("GITHUB_REPOSITORY") == REPOSITORY, "Publication must run in the intended repository")
    require(os.environ.get("GITHUB_REF") == "refs/heads/history/rewrite-2026-11-02", "Publication must run from the administrative branch")
    require(os.environ.get("GITHUB_EVENT_NAME") == "push", "Unexpected publication event")
    require(os.environ.get("GITHUB_ACTOR") == "perceptive-moose", "Publication requires the repository owner's push")
    origin = git("remote", "get-url", "--push", "origin").removesuffix(".git")
    require(origin == f"https://github.com/{REPOSITORY}", "Unexpected publication destination")
    heads = remote_heads()
    require(heads.get("refs/heads/master") == OLD_HEAD, "Master moved since the rewrite was prepared")
    require(heads.get(ARCHIVE) == OLD_HEAD, "Original history archive is absent or changed")
    # This explicit expected SHA protects against a concurrent push between the
    # preceding read and this update. No other branch is force-updated.
    subprocess.run([
        "git", "push", f"--force-with-lease=refs/heads/master:{OLD_HEAD}",
        "origin", f"{LOCAL_CANDIDATE}:refs/heads/master",
    ], check=True)
    heads = remote_heads()
    require(heads.get("refs/heads/master") == NEW_HEAD, "Published master does not match the candidate")
    require(heads.get(ARCHIVE) == OLD_HEAD, "Archive changed unexpectedly")
    print(f"Published {NEW_HEAD}; archive remains at {OLD_HEAD}.")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        Path(summary_path).write_text(
            "## History rewrite published\n\n"
            f"New master: [`{NEW_HEAD}`](https://github.com/{REPOSITORY}/commit/{NEW_HEAD})\n\n"
            f"Original master remains at `{ARCHIVE.removeprefix('refs/heads/')}`.\n\n"
            "18 coherent feature commits and 8 normal merge commits, all with explicit ChatGPT attribution. "
            "All eight merge snapshots and the final file tree match the originals exactly.\n\n"
            "The original PRs and their feature branches remain available. Start the existing Pages workflow "
            "on master to validate and deploy this new commit identity.\n"
        )


if __name__ == "__main__":
    main()
