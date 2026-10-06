# Request access and contribute

xWalk accepts access requests and proposed fixes through GitHub. A maintainer approves repository access
manually. Accepted source changes still pass Gerrit review and CI before publication to GitHub.

## Request private module access

1. Sign in to the GitHub account you will use for development.
2. Open [Request private module access](https://github.com/TARS-v00-01/xWalkPiCarApp/issues/new?template=access-request.yml).
3. Specify the modules or feature you need and explain your intended contribution.
4. Wait for a maintainer to review the request. An issue, label, or comment does not grant access.
5. If approved, accept the GitHub repository invitations sent to the account that opened the request.

Requests are public. Do not include private source, credentials, device logs, or personal contact details.
Maintainers may approve only part of a request. Read access applies only to the invited repositories and their
private forks; it does not grant organization membership, upstream write permission, Gerrit access, or access
to private Hugging Face datasets. Request any additional build dependencies explicitly.

See the [Git guide](GIT_GUIDE.md) after accepting your invitations. A public integration clone alone does not
grant access to its private components.

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

Only a repository administrator or organization owner may approve access.

1. Review the issue author's GitHub account and stated purpose. Use the actual issue author as the invitation
   recipient, not a different username pasted into the request.
2. Decide the exact modules and necessary dependencies. For the complete app checkout, the six components
   listed in [README.md](README.md#components) also need the protocol references `xWalkLibrary`,
   `xWalk-rpi5-trace`, and `xWalk-rpi5-node`. Hardware access depends on the integration's pinned submodules.
3. In each approved repository, open **Settings > Collaborators and teams > Add people** and invite the issue
   author with the **Read** role as an outside collaborator. Do not invite them to the organization or grant
   Write, Maintain, or Admin solely to submit fixes.
4. Record the approved repository names in the request and indicate that invitations are pending. Close the
   request when handled; an invitation must still be accepted before access is available. A rejected request
   receives no invitation. No label or comment triggers an automatic invitation.
5. Review access periodically and remove repository access when it is no longer needed. Removing access does
   not erase copies someone has already downloaded.

For an accepted PR, review its diff before checking it out. Preserve the contributor's authorship and add a
`Pull-Request:` source URL to the Gerrit commit message with the normal project subject and `Change-Id`.
Upload to the owning Gerrit project, wait for its current CI result and required review approval, then submit.
Let normal replication and integration uplifts publish the result. Link the Gerrit review and submitted commit
back to the PR before closing it; do not bypass this flow with an upstream GitHub push or merge.

## Repository settings

[contributor-access.json](.github/contributor-access.json) records the intended configuration. It is a
configuration reference, not an invitation bot. Organization owners enable **Allow forking of private
repositories** under organization **Settings > Member privileges**. Repository admins enable **Allow forking**
under **Settings > General** only for the listed source repositories. Repositories remain private.

Keep issue tracking enabled on the public request repository and private source repositories. The organization's
website link points to this guide. Existing organization membership and permissions are not changed by this
setup. In particular, existing member base permissions do not determine outside-collaborator invitations.

Do not enable PR execution on privileged self-hosted runners or share secrets with fork workflows to implement
this process. New contributors receive no upstream write permission, and existing Gerrit publication controls
remain in place.

GitHub references: [repository roles](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/repository-roles-for-an-organization),
[forks](https://docs.github.com/en/pull-requests/reference/forks), and
[private forking policy](https://docs.github.com/en/organizations/managing-organization-settings/managing-the-forking-policy-for-your-organization).
