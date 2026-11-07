# Automatic public profile refresh

The `Refresh public profile` GitHub Actions workflow runs daily at 00:17 UTC
(07:17 Asia/Ho_Chi_Minh) and can be started with **Actions > Refresh public
profile > Run workflow** on `main`. GitHub schedules can be delayed; this is
a daily refresh target, not an exact-time delivery guarantee.

The runner uses Python 3.12 and public GitHub profile, repository and
contribution-calendar responses. No PAT or installed account credential is
required. Checkout uses the job's short-lived `GITHUB_TOKEN` to publish.
Public API requests also use that token to avoid shared anonymous rate limits;
the public HTML contribution calendar receives no token. Repository pages are
paginated and checked for completeness, duplicate IDs and private entries.
The footer shows the actual fetch time in UTC+7; `fetched_at` in the JSON is UTC.

The publisher refuses dirty checkouts and branches other than `main`. It
fetches public data, renders SVGs, builds the offline HTML, and runs metric,
native SVG and shipped-asset checks before publishing. Only generated SVGs,
`assets/profile-data.json`, `assets/profile-data.js`, and `index.html` enter
the first commit. The README enters a second commit with images pinned to
the first commit's immutable SHA. A single atomic push publishes both
commits. Both commits are authored by `github-actions[bot]`.

If generated artifacts have not changed, the existing README pin is
preserved and there is no commit or push. A validation failure stops before
push. If another writer changes `main` during the run, publication fails
without merging or overwriting their work. Rerun the workflow to refresh
from the new branch tip. A failed runner may have temporary local files or
commits; these disappear with the runner and never replace the remote.

The workflow serializes its own runs. Repository branch protection or
organization token policies may still deny its push; check the failed
Actions log instead of supplying a personal token.

The job requests a legacy GitHub Pages build explicitly because a bot-token
push does not trigger the branch-based Pages build. It checks the deployment
status for the final published README commit at `pages/deployments/{HEAD}`
and accepts only `succeed`. The legacy `builds/latest` status can report a
canceled duplicate build even when deployment succeeds, so it is not used
as completion evidence. Missing deployments are polled; terminal deployment
failures and a five-minute timeout fail the job. This check also runs after
unchanged input, so a manual rerun can recover a previously failed Pages build
without another data commit.

The schedule runs on the default branch and may be delayed by GitHub's queue.
GitHub may disable scheduled workflows in public repositories after 60 days
without repository activity; re-enable it under Actions if that happens.

References: [scheduled workflow behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule),
[bot token behavior](https://docs.github.com/en/actions/concepts/security/github_token),
and [Pages build API](https://docs.github.com/en/rest/pages/pages#request-a-github-pages-build),
[exact Pages deployment status](https://docs.github.com/en/rest/pages/pages#get-the-status-of-a-github-pages-deployment).

Run the publisher's offline integration tests locally with:

```powershell
python scripts/test_refresh_profile.py
python scripts/test_refresh_pages.py
python scripts/test_update_profile.py
```

These tests use temporary bare Git remotes and synthetic render callbacks.
They prove the immutable two-commit pin, single atomic push, frozen-input
no-op, validation failure, dirty-checkout refusal, and concurrent-writer
protection without fetching live profile data.
