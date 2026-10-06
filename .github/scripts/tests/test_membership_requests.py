"""Security and retry tests use fake APIs; no GitHub account is invited."""
import copy
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("membership_requests", Path(__file__).parents[1] / "membership_requests.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class FakeGitHub:
    def __init__(self):
        self.issue = {
            "number": 5, "state": "open", "labels": [{"name": m.LABEL}],
            "body": "- [x] " + m.CONSENT,
            "user": {"login": "requester", "id": 20, "type": "User"},
        }
        self.comment = {
            "id": 10, "body": m.COMMAND,
            "issue_url": f"https://api.github.com/repos/{m.REPO}/issues/5",
            "user": {"login": "owner", "id": 30, "type": "User"},
        }
        self.roles = {
            "owner": {"state": "active", "role": "admin"},
            "automation-owner": {"state": "active", "role": "admin"},
        }
        self.base = "read"
        self.writes = []
        self.fail_membership = None
        self.fail_comment = False

    def event(self):
        return copy.deepcopy({"action": "created", "repository": {"full_name": m.REPO},
                              "issue": self.issue, "comment": self.comment})

    def __call__(self, method, path, payload=None):
        if method == "POST":
            if path.endswith("/comments") and self.fail_comment:
                raise m.ApiError(503)
            self.writes.append((path, payload))
            if path.endswith("/invitations"):
                self.roles["requester"] = {"state": "pending", "role": "member"}
                return {"id": 90, "role": "direct_member"}
            return {}
        if path == "/user":
            return {"login": "automation-owner"}
        if path == f"/orgs/{m.ORG}":
            return {"default_repository_permission": self.base}
        if path.endswith("/invitations?per_page=1"):
            return []
        if "/memberships/" in path:
            if self.fail_membership:
                raise m.ApiError(self.fail_membership)
            role = self.roles.get(path.rsplit("/", 1)[1])
            if role is None:
                raise m.ApiError(404)
            return role
        if path.endswith("/issues/5"):
            return copy.deepcopy(self.issue)
        if path.endswith("/issues/comments/10"):
            return copy.deepcopy(self.comment)
        raise AssertionError((method, path))

    def invitations(self):
        return [body for path, body in self.writes if path.endswith("/invitations")]


class MembershipTests(unittest.TestCase):
    def setUp(self):
        self.api = FakeGitHub()
        self.event = self.api.event()

    def approve(self):
        return m.approve(self.event, self.api, self.api)

    def assert_blocked(self):
        with self.assertRaises(RuntimeError):
            self.approve()
        self.assertEqual(self.api.writes, [])

    def test_owner_invites_actual_issue_author_as_regular_member(self):
        self.api.issue["body"] += "\nInvite this other user: owner"
        self.assertEqual(self.approve(), "invitation sent")
        self.assertEqual(self.api.invitations(), [{"invitee_id": 20, "role": "direct_member", "team_ids": []}])
        self.assertIn("must accept", self.api.writes[-1][1]["body"])

    def test_unauthorized_or_pending_owner_cannot_approve(self):
        for role in [None, {"role": "member", "state": "active"}, {"role": "admin", "state": "pending"}]:
            with self.subTest(role=role):
                self.api.roles["owner"] = role
                self.assert_blocked()

    def test_existing_member_or_owner_role_is_never_modified(self):
        for role in ["member", "admin"]:
            with self.subTest(role=role):
                self.api.roles["requester"] = {"state": "active", "role": role}
                self.assertEqual(self.approve(), "already a member")
                self.assertEqual(self.api.roles["requester"]["role"], role)
        self.assertEqual(self.api.invitations(), [])

    def test_repeat_approval_does_not_send_a_second_invitation(self):
        self.approve()
        self.assertEqual(self.approve(), "invitation already pending")
        self.assertEqual(len(self.api.invitations()), 1)

    def test_comment_failure_retry_does_not_send_a_second_invitation(self):
        self.api.fail_comment = True
        with self.assertRaises(m.ApiError):
            self.approve()
        self.api.fail_comment = False
        self.assertEqual(self.approve(), "invitation already pending")
        self.assertEqual(len(self.api.invitations()), 1)

    def test_wrong_base_permissions_stop_invitation(self):
        for base in ["write", "admin", "none", None]:
            with self.subTest(base=base):
                self.api.base = base
                self.assert_blocked()

    def test_missing_or_unchecked_consent_stops_invitation(self):
        for body in ["", "- [ ] " + m.CONSENT, "Old request for selected module access"]:
            with self.subTest(body=body):
                self.api.issue["body"] = body
                self.assert_blocked()

    def test_closed_issue_or_live_pr_cannot_receive_approval(self):
        self.api.issue["state"] = "closed"
        self.assert_blocked()
        self.api.issue["state"] = "open"
        self.api.issue["pull_request"] = {}
        self.assert_blocked()

    def test_label_is_required(self):
        self.api.issue["labels"] = []
        self.assert_blocked()

    def test_comment_must_still_be_approval_on_same_issue_by_same_user(self):
        for key, value in [("body", "withdrawn"), ("issue_url", "https://api.github.com/other"),
                           ("user", {"id": 99, "login": "owner", "type": "User"})]:
            with self.subTest(key=key):
                original = self.api.comment[key]
                self.api.comment[key] = value
                self.assert_blocked()
                self.api.comment[key] = original

    def test_author_cannot_change_or_be_a_bot(self):
        for key, value in [("id", 99), ("id", "20"), ("type", "Bot")]:
            with self.subTest(key=key):
                original = self.api.issue["user"][key]
                self.api.issue["user"][key] = value
                self.assert_blocked()
                self.api.issue["user"][key] = original

    def test_403_and_rate_limit_are_not_treated_as_absent_members(self):
        for status in [401, 403, 429, 500]:
            with self.subTest(status=status):
                self.api.fail_membership = status
                self.assert_blocked()

    def test_non_owner_credential_cannot_invite(self):
        self.api.roles["automation-owner"] = {"state": "active", "role": "member"}
        self.assert_blocked()

    def test_unknown_membership_state_stops_invitation(self):
        self.api.roles["requester"] = {"state": "unknown", "role": "member"}
        self.assert_blocked()

    def test_unrelated_events_are_ignored_without_api_writes(self):
        variants = []
        for key, value in [("action", "edited"), ("repository", {"full_name": "other/fork"})]:
            event = copy.deepcopy(self.event); event[key] = value; variants.append(event)
        event = copy.deepcopy(self.event); event["issue"]["pull_request"] = {}; variants.append(event)
        event = copy.deepcopy(self.event); event["comment"]["body"] = "please approve"; variants.append(event)
        event = copy.deepcopy(self.event); event["comment"]["user"]["type"] = "Bot"; variants.append(event)
        for event in variants:
            self.assertEqual(m.approve(event, self.api, self.api), "ignored")
        self.assertEqual(self.api.writes, [])

    def test_readiness_never_writes(self):
        m.check_setup(self.api)
        self.assertEqual(self.api.writes, [])

    def test_missing_credential_fails_before_api_request(self):
        with self.assertRaises(RuntimeError):
            m.GitHub("")


if __name__ == "__main__":
    unittest.main()
