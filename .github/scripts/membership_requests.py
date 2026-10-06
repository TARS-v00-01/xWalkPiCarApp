#!/usr/bin/env python3
"""Invite a request's author only after a live organization owner's approval."""

import argparse
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

ORG = "TARS-v00-01"
REPO = f"{ORG}/xWalkPiCarApp"
COMMAND = "/approve-membership"
LABEL = "membership-request"
CONSENT = "I request organization membership with read access to all private repositories, including documentation."


class ApiError(RuntimeError):
    """Expose an HTTP status without printing credentials or response bodies."""

    def __init__(self, status):
        self.status = status
        super().__init__(f"GitHub API returned HTTP {status}")


class GitHub:
    def __init__(self, token):
        if not token:
            raise RuntimeError("The required GitHub credential is missing.")
        self.token = token

    def __call__(self, method, path, payload=None):
        if not path.startswith((f"/orgs/{ORG}", f"/repos/{REPO}/", "/user")):
            raise RuntimeError("Unexpected API destination.")
        request = Request(
            "https://api.github.com" + path,
            data=None if payload is None else json.dumps(payload).encode(),
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
                "User-Agent": "xWalk-membership-requests",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            raise ApiError(error.code) from None


def membership(api, login):
    try:
        return api("GET", f"/orgs/{ORG}/memberships/{quote(login, safe='')}")
    except ApiError as error:
        if error.status != 404:
            raise
        return None


def check_setup(api):
    """Read-only credential and base-permission check; never invite a user."""
    account = api("GET", "/user")
    role = membership(api, account["login"])
    if not role or role.get("state") != "active" or role.get("role") != "admin":
        raise RuntimeError("The invitation credential must belong to an active organization owner.")
    organization = api("GET", f"/orgs/{ORG}")
    if organization.get("default_repository_permission") != "read":
        raise RuntimeError("Organization base permission must be Read; invitation stopped.")
    # Verifies access to invitation management without sending a test invitation.
    api("GET", f"/orgs/{ORG}/invitations?per_page=1")


def eligible(event):
    issue = event.get("issue", {})
    comment = event.get("comment", {})
    return (
        event.get("action") == "created"
        and event.get("repository", {}).get("full_name") == REPO
        and "pull_request" not in issue
        and comment.get("body", "").strip() == COMMAND
        and comment.get("user", {}).get("type") == "User"
    )


def approve(event, member_api, issue_api):
    """Revalidate the request and owner before sending a regular-member invitation."""
    if not eligible(event):
        return "ignored"
    number = event["issue"]["number"]
    comment_id = event["comment"]["id"]
    if type(number) is not int or type(comment_id) is not int or min(number, comment_id) <= 0:
        raise RuntimeError("Invalid issue or comment identifier.")
    issue_path = f"/repos/{REPO}/issues/{number}"
    issue = issue_api("GET", issue_path)
    comment = issue_api("GET", f"/repos/{REPO}/issues/comments/{comment_id}")
    if issue.get("state") != "open" or "pull_request" in issue:
        raise RuntimeError("Approval requires an open issue, not a pull request.")
    if comment.get("issue_url") != f"https://api.github.com{issue_path}":
        raise RuntimeError("Approval comment does not belong to this request.")
    if comment.get("body", "").strip() != COMMAND:
        raise RuntimeError("Approval comment has changed.")
    approver = comment["user"]
    if approver.get("type") != "User" or approver["id"] != event["comment"]["user"]["id"]:
        raise RuntimeError("Approval identity has changed.")
    role = membership(member_api, approver["login"])
    if not role or role.get("state") != "active" or role.get("role") != "admin":
        raise RuntimeError("Only an active organization owner may approve membership.")
    if LABEL not in {label["name"] for label in issue.get("labels", [])}:
        raise RuntimeError("The issue is not labelled as a membership request.")
    consent = re.compile(r"^\s*- \[[xX]\] " + re.escape(CONSENT) + r"\s*$", re.MULTILINE)
    if not consent.search(issue.get("body") or ""):
        raise RuntimeError("The requester must explicitly acknowledge organization-wide read access.")
    author = issue["user"]
    if (author.get("type") != "User" or type(author.get("id")) is not int
            or author["id"] <= 0 or author["id"] != event["issue"]["user"]["id"]):
        raise RuntimeError("Request author must be the original human GitHub account.")
    check_setup(member_api)
    existing = membership(member_api, author["login"])
    if existing and existing.get("state") == "active":
        state = "already a member"
        # Never update an existing member's role, especially an owner's role.
    elif existing and existing.get("state") == "pending":
        state = "invitation already pending"
    elif existing:
        raise RuntimeError("Unexpected membership state; no invitation sent.")
    else:
        member_api("POST", f"/orgs/{ORG}/invitations", {
            "invitee_id": author["id"], "role": "direct_member", "team_ids": [],
        })
        state = "invitation sent"
    issue_api("POST", issue_path + "/comments", {"body": (
        f"Membership approval processed: **{state}**.\n\n"
        "If an invitation is pending, the request author must accept it in GitHub before membership starts. "
        f"[Open the organization invitation](https://github.com/orgs/{ORG}/invitation). "
        "Invitations expire after seven days. Regular members inherit Read access to all private repositories "
        "from the organization base permission; this approval grants no owner role or team-specific write access. "
        "Existing member permissions are not changed. Maintainers may close this request once handled."
    )})
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only configuration check; never invite.")
    args = parser.parse_args()
    token = os.environ.get("XWALK_ORG_MEMBERSHIP_TOKEN", "")
    if not token:
        raise RuntimeError("Set the XWALK_ORG_MEMBERSHIP_TOKEN Actions secret before approving requests.")
    member_api = GitHub(token)
    if args.check:
        check_setup(member_api)
        print("Organization owner credential and Read base permissions verified; no invitation sent.")
    else:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
        print(approve(event, member_api, GitHub(os.environ.get("GITHUB_TOKEN", ""))))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyError, ValueError, OSError) as error:
        print(f"Membership automation stopped: {error}", file=sys.stderr)
        sys.exit(1)
