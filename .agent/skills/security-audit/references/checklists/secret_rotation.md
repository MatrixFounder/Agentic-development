# Secret Rotation & Remediation Guide

> **Purpose:** Step-by-step guidance for remediating exposed secrets.
> **Rule:** A leaked secret is compromised FOREVER in git history, even after deletion.

## Immediate Response (When Secrets Are Found)

### 1. Rotate the Secret IMMEDIATELY
Do NOT just delete the file. The secret is already in git history.

| Secret Type | Rotation Action |
|---|---|
| AWS Access Key | IAM Console → Deactivate old key → Create new key → Update all consumers |
| GitHub Token (ghp_) | Settings → Developer Settings → Tokens → Revoke → Generate new |
| Slack Token (xoxb-) | Slack App Dashboard → Regenerate token |
| Stripe Key (sk_live_) | Stripe Dashboard → Developers → API Keys → Roll key |
| OpenAI/Anthropic Key | Provider Dashboard → API Keys → Revoke → Create new |
| Database Password | Change password in DB → Update connection strings in vault → Restart services |
| JWT Signing Key | Generate new key → Deploy → Invalidate all existing tokens |
| SSH Key | Remove public key from authorized_keys → Generate new keypair |
| Private Key (0x...) | **Transfer all assets immediately** → Generate new wallet |

### 2. Clean Git History
**WARNING:** This rewrites git history. Coordinate with your team.

#### Option A: BFG Repo-Cleaner (Recommended — fast)
```bash
# Install: brew install bfg (or download jar)
# Create a file with secrets to remove
echo "AKIA..." > secrets-to-remove.txt
echo "sk_live_..." >> secrets-to-remove.txt

# Run BFG (operates on bare clone)
git clone --mirror git@github.com:org/repo.git
bfg --replace-text secrets-to-remove.txt repo.git
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

#### Option B: git-filter-repo (More control)
```bash
# Install: pip install git-filter-repo
# Replace secret with ***REMOVED*** in all history
git filter-repo --replace-text <(echo 'AKIA...==>***REMOVED***')
git push --force --all
```

### 3. Verify Cleanup
```bash
# Search entire git history for the secret
git log -p --all -S 'AKIA...' | head -20
# Should return empty
```

## Prevention: Where to Store Secrets

### Tier 1: Secrets Manager (Recommended)
- **AWS Secrets Manager** / **AWS SSM Parameter Store**
- **HashiCorp Vault**
- **GCP Secret Manager**
- **Azure Key Vault**
- **1Password / Doppler** (for team secrets)

### Tier 2: Environment Variables (Acceptable)
- Set in CI/CD pipeline (GitHub Secrets, GitLab CI Variables)
- Set in deployment platform (Vercel, Railway, Fly.io)
- Never commit `.env` files (ensure `.gitignore` includes `.env*`)

### Tier 3: Local Development
- Use `.env.local` (gitignored)
- Use `direnv` with `.envrc` (gitignored)
- Provide `.env.example` with placeholder values only

## Pre-Commit Prevention

### Option A: gitleaks pre-commit hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

### Option B: git-secrets (AWS)
```bash
git secrets --install
git secrets --register-aws
```

### Option C: trufflehog pre-commit
```bash
trufflehog git file://. --only-verified --fail
```

## Audit Checklist
- [ ] Secret has been rotated/regenerated
- [ ] Old secret has been deactivated/revoked
- [ ] Git history has been cleaned (BFG or git-filter-repo)
- [ ] Force push completed and team notified
- [ ] All consumers updated with new secret
- [ ] `.gitignore` updated to prevent recurrence
- [ ] Pre-commit hook installed to catch future leaks
- [ ] Incident documented (date, scope, remediation)
