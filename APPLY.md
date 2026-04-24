# APPLY · Brief C · Delivery Pipeline · Operator Checklist

After running `apply-brief-c.sh` and committing, complete these one-time setup steps:

## 1 · Set GitHub Secrets (before Wave 4)

These are needed by `deploy-azure.yml` and `teardown-azure.yml`. Values come from Wave-4 Azure activation.

```bash
gh secret set AZURE_CLIENT_ID       --body "<placeholder>"
gh secret set AZURE_TENANT_ID       --body "<placeholder>"
gh secret set AZURE_SUBSCRIPTION_ID --body "<placeholder>"
```

Replace `<placeholder>` with actual values once Wave 4 activates Azure.

## 2 · Create production environment

```bash
gh api -X PUT /repos/sowthri-industrial-ai/project-00-ground-zero/environments/production \
  -F wait_timer=0 \
  -F reviewers='[]' \
  -F deployment_branch_policy='{"protected_branches":true,"custom_branch_policies":false}'
```

## 3 · Verify workflows are discovered

```bash
gh workflow list --repo sowthri-industrial-ai/project-00-ground-zero
```

Should list all 7 workflows.

## 4 · Trigger first CI run (automatic on push)

After you commit the Brief C artifacts, push to main. `ci.yml` runs automatically.

## 5 · Create deliberate failure branches (ADR-0011)

```bash
# demo-fails-g1 · break pyproject.toml
git checkout -b demo-fails-g1
echo "INVALID TOML {" > pyproject.toml
git commit -am "demo: deliberate G1 fail"
git push origin demo-fails-g1
git checkout main

# demo-fails-guardrail · remove content-safety.bicep
git checkout -b demo-fails-guardrail
git rm infra/bicep/modules/content-safety.bicep
git commit -m "demo: deliberate G2 fail"
git push origin demo-fails-guardrail
git checkout main

# demo-regresses-eval · placeholder (Brief E fills)
git checkout -b demo-regresses-eval
echo "# Eval regression demo (Brief E fills)" > tests/demo-regression.md
git add tests/ 2>/dev/null || mkdir -p tests && echo "placeholder" > tests/demo-regression.md
git commit -am "demo: deliberate G4 regression"
git push origin demo-regresses-eval
git checkout main
```

These branches stay permanent — reviewers see the gates actually firing.

## 6 · Verify PR comment bot

Open a test PR. The bot should post an as-built summary comment within ~1 minute of PR creation.

---

**Wave 2 · Brief C gate status**: Authored. Wave 4 activates deploys.
