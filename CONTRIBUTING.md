# Request access and contribute

xWalk accepts membership requests and proposed fixes through GitHub. An organization owner approves each
membership request. The approval sends a regular-member invitation; the requester must accept it in GitHub.
Accepted source changes still pass Gerrit review and CI before publication to GitHub.

## Request organization membership

1. Sign in to the GitHub account you will use for development.
2. Open [Request organization membership](https://github.com/TARS-v00-01/xWalkPiCarApp/issues/new?template=access-request.yml).
3. Explain your intended contribution and acknowledge organization-wide read access.
4. Wait for an organization owner to approve the request with `/approve-membership`.
5. Accept the GitHub organization invitation sent to the account that opened the request. Invitations expire
   after seven days. You can also open the [organization invitation](https://github.com/orgs/TARS-v00-01/invitation).

Requests are public. Do not include private source, credentials, device logs, or personal contact details.
After acceptance, the organization's existing **Read** base permission gives you read access to **all private
repositories**, including private documentation and future repositories covered by that base permission.
The invitation grants regular membership, not an owner role or additional team permissions. Existing separately
assigned permissions are not removed. Membership does not grant Gerrit access or private Hugging Face dataset access.

See the [Git guide](GIT_GUIDE.md) after accepting your invitation. You can use private forks to propose fixes;
you do not need upstream write permission. A public integration clone alone does not grant private access.

## Report an issue or propose a fix

Report public-facing behavior using the
[bug form](https://github.com/TARS-v00-01/xWalkPiCarApp/issues/new?template=bug-report.yml).
Report private implementation details in the affected private repository's Issues page.
Maintainers can link accepted reports to the existing Jira work item used for implementation tracking.

For a code fix:

1. Open the repository that owns the changed files. A private component fix belongs in that component,
   not in the public integration repository.
2. Select **Fork** and use your personal account. Private forks remain private. Repository read access and
   enabled private forking are required; GitHub Free organizations cannot receive private forks.
3. Create a branch in your fork, make the change, and run the component's documented host checks.
4. Push only to your own fork. If you previously configured the Gerrit Git wrapper, check your fork remote's
   push URL before using it; do not replace the upstream Gerrit publication remote.
5. Open a pull request from your branch to the original repository's `master` branch. Explain the problem,
   the fix, and the checks you ran. Keep private code and logs inside the private repository.
6. A maintainer reviews the proposal, imports the accepted change into Gerrit, and links the Gerrit review
   in the PR. Gerrit CI and approval are required before submission. The submitted commit is then replicated
   to GitHub, and the maintainer closes the PR with that revision and review link.

Read-only contributors cannot push or merge into the original repositories. GitHub PRs are proposal intake;
maintainers do not use GitHub's merge button. PR creation does not automatically execute code on the project's
self-hosted runners. Existing CI runs on reviewed Gerrit patch sets and submitted GitHub revisions.

Contributors who already have Gerrit access may continue the
[direct Gerrit workflow](GIT_GUIDE.md#configure-gerrit-contribution).

## Maintainer approval

Only an active **organization owner** may approve membership. Repository administrator access alone is insufficient.

1. Review the issue author's account, stated purpose, and acknowledgement of read access to all private repositories.
2. Confirm the issue has the `membership-request` label and the organization base permission is still **Read**.
3. Post a new comment containing only `/approve-membership`. This is the approval action.
4. The [membership workflow](https://github.com/TARS-v00-01/xWalkPiCarApp/actions/workflows/membership-requests.yml)
   checks your current owner role and the live request, then invites its actual author by numeric GitHub user ID.
   A pasted username in the request cannot change the recipient. The bot reports whether an invitation was sent,
   is already pending, or the person is already a member. The requester must still accept a pending invitation.
5. If the workflow fails, inspect its Actions run and fix the reported configuration. Rerun that run or post a new
   approval comment. Editing an old comment does not trigger approval. Repeated approvals preserve existing roles
   and do not send a new invitation when membership is active or pending. Reopen a closed request before retrying.
6. Close the request once handled. Closing an issue or deleting an approval comment does not revoke an invitation
   or membership. Cancel pending invitations or remove members explicitly in organization **People** settings.
   Reject a request by closing it without approving it. Review membership periodically.

Older module-only requests lack the organization-wide acknowledgement and cannot trigger invitations. Ask the
requester to submit the new form. A non-owner, bot, pull request, missing acknowledgement, changed comment, or base
permission other than Read stops the invitation. The workflow never changes an existing member's role.

For an accepted PR, review its diff before checking it out. Preserve the contributor's authorship and add a
`Pull-Request:` source URL to the Gerrit commit message with the normal project subject and `Change-Id`.
Upload to the owning Gerrit project, wait for its current CI result and required review approval, then submit.
Let normal replication and integration uplifts publish the result. Link the Gerrit review and submitted commit
back to the PR before closing it; do not bypass this flow with an upstream GitHub push or merge.

## Automation configuration

[contributor-access.json](.github/contributor-access.json) records the intended settings.
[The workflow](.github/workflows/membership-requests.yml) runs only reviewed default-branch code on GitHub-hosted
runners. It never checks out fork code, initializes private submodules, or runs on privileged self-hosted runners.
The repository workflow token has only contents-read and issue-comment permissions; it cannot invite members.

An organization owner must configure the separate Actions repository secret `XWALK_ORG_MEMBERSHIP_TOKEN`:

1. Create a fine-grained personal access token owned by an active organization owner, with resource owner
   `TARS-v00-01`. Select public repositories only; no private repository code permissions are needed.
2. Give it organization **Members: Read and write** for invitations and membership verification, plus
   **Administration: Read-only** to verify the organization's Read base permission. Set an expiry and rotate
   the secret before it expires. Approve the token in organization settings if GitHub requires approval.
3. Save it under **xWalkPiCarApp > Settings > Secrets and variables > Actions > New repository secret**, using
   the exact name `XWALK_ORG_MEMBERSHIP_TOKEN`. An organization Actions secret with the same name also works
   if its repository access includes the public `xWalkPiCarApp` repository. A private-repositories-only secret
   will not be available here. Never paste tokens into issues, chat, logs, or source control.
4. Open the **Organization membership requests** workflow and use **Run workflow** on `master`. This runs the
   tests and a read-only readiness check without inviting anybody. Missing or invalid credentials fail closed.
   The readiness check verifies read access and owner identity; the token's Members-write setting must also be set.

No invitation is sent merely because a request is opened or labelled. Only an owner's approval command starts
invitation handling. GitHub controls invitation delivery, expiry, and acceptance. No real external account is
invited by the automated tests or readiness check.

Organization owners keep base permissions at **Read** and **Allow forking of private repositories** enabled under
**Settings > Member privileges**. Source repositories listed in the configuration allow private forks and issues.
All private repositories remain private. Fork PR workflows and secret sharing remain disabled. The organization's
website link points to this guide. Maintainers continue to import accepted PRs into Gerrit for CI and publication.

Run the approval and rejection tests locally:

```bash
python3 -m unittest discover -s .github/scripts/tests -v
```

GitHub references: [organization invitations](https://docs.github.com/en/organizations/managing-membership-in-your-organization/inviting-users-to-join-your-organization),
[base permissions](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/setting-base-permissions-for-an-organization), and
[private forking policy](https://docs.github.com/en/organizations/managing-organization-settings/managing-the-forking-policy-for-your-organization).
