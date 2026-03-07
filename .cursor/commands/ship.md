# Ship to GitHub via PR + Squash-Merge (Solo Dev, 2026 Style)

**Description:**  
Automates the full solo-dev workflow: commit → push branch → create PR → squash-merge PR → delete branch. Uses GitHub CLI (`gh`) for PR/merge steps when possible. No browser needed. Clean main history. Run with `/ship` or `/ship your message here`.

**Prerequisites (one-time):**
- Install GitHub CLI: https://cli.github.com (brew install gh / winget install gh / etc.)
- Authenticate: run `gh auth login` in terminal once

---

You are an expert Git + GitHub CLI assistant for solo developers. Execute the full "ship" workflow autonomously using Cursor's terminal. Do NOT ask for confirmations — this is a solo repo.

### Workflow steps (execute in order via terminal commands):

1. **Detect state**
   - Run: `git status --short`
   - Get current branch: `git branch --show-current` → let CURRENT_BRANCH = result
   - Detect main: prefer `main`, fallback `master` → let MAIN_BRANCH = result
   - Report briefly: current branch, main branch, any changes.

2. **Commit if needed**
   - If `git status --porcelain` not empty:
     - `git add -A`
     - Commit message:
       - If user provided text after `/ship` (e.g. `/ship fix login`), use EXACTLY that.
       - Else: auto-summarize changes (look at `git diff --cached --name-only` + diffs; make concise title like "Update auth logic and fix edge case").
     - `git commit -m "YOUR_MESSAGE"`

3. **Push current branch**
   - `git push -u origin "$CURRENT_BRANCH"`

4. **If already on main branch**
   - Done. Output: "✅ Pushed directly to $MAIN_BRANCH — no PR needed."

5. **Feature branch → PR + squash-merge**
   - Ensure `gh` is available: run `gh --version` (if fails, fall back to git-only mode and warn user)
   - Create PR:
     - `gh pr create --base "$MAIN_BRANCH" --head "$CURRENT_BRANCH" --fill`
       ( `--fill` auto-uses latest commit title/body; if you have a good single commit it's perfect)
     - Capture the PR URL from output (e.g. https://github.com/user/repo/pull/123)
   - Immediately squash-merge & delete branch:
     - `gh pr merge --squash --delete-branch --body "$COMMIT_MESSAGE"`
       (reuses message; `--delete-branch` removes remote + local branch)
   - If `gh pr merge` fails (e.g. CI pending, protected branch), fall back:
     - Warn: "Merge failed — perhaps checks pending or branch protection. Falling back to local squash."
     - Then do original git squash: checkout main → pull → merge --squash → commit → push → delete branches

6. **Fallback git-only squash (if gh not installed or merge blocked)**
   - `git checkout "$MAIN_BRANCH"`
   - `git pull origin "$MAIN_BRANCH" --ff-only`
   - If not already merged: `git merge --squash "$CURRENT_BRANCH"`
   - `git commit -m "$COMMIT_MESSAGE"`
   - `git push origin "$MAIN_BRANCH"`
   - `git branch -D "$CURRENT_BRANCH"`
   - `git push origin --delete "$CURRENT_BRANCH" || true`

7. **Final steps**
   - `git checkout "$MAIN_BRANCH"`
   - `git pull`
   - Run `git status` + `git log -1 --oneline`
   - Show celebratory summary + emoji

**Rules:**
- Prefer `gh` commands for PR/merge/delete — they're cleaner & official.
- Use terminal execution for ALL git/gh commands.
- Never open browser or ask user to do manual steps.
- Handle no-changes / already-merged / errors gracefully — show exact error + suggested fix.
- End with clear success message like: "🎉 Shipped! PR created & squash-merged. Main is clean. Branch deleted."

Execute now — full workflow, no questions.