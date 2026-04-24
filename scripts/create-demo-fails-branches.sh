#!/usr/bin/env bash
# Creates 3 permanent demo-fails-* branches per ADR-0011 · NEVER merge
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

[ "$(git branch --show-current)" = "main" ] || { echo "must be on main"; exit 1; }
git diff --quiet && git diff --cached --quiet || { echo "working tree not clean"; exit 1; }

# Branch 1 · G1 type error
git checkout -b demo-fails-g1
cat >> src/rag/generate.py <<'PY_APPEND'


def _demo_g1_broken() -> int:
    """Intentional type error · caught by G1 mypy gate."""
    return "not an int"  # type: ignore[return-value]
PY_APPEND
echo "# demo-fails-g1 · DO NOT MERGE" > BRANCH_README.md
echo "Intentional type error · G1 gate blocks the PR." >> BRANCH_README.md
git add -A
git commit -m "demo: intentional type error to demonstrate G1 gate"
git push -u origin demo-fails-g1 || true

# Branch 2 · guardrail bypass
git checkout main
git checkout -b demo-fails-guardrail
python3 - <<'PY_EDIT'
from pathlib import Path
p = Path("src/main.py")
s = p.read_text()
start = "# ── BRIEF-E:GUARDRAIL-INPUT-GATE"
end = "# ── /BRIEF-E:GUARDRAIL-INPUT-GATE ──"
i = s.index(start); j = s.index(end) + len(end)
p.write_text(s[:i] + "# gate bypassed for demo · G4 must catch this" + s[j:])
PY_EDIT
echo "# demo-fails-guardrail · DO NOT MERGE" > BRANCH_README.md
echo "Input gate bypassed · G4 Guardrail tier catches." >> BRANCH_README.md
git add -A
git commit -m "demo: bypass content safety to demonstrate G4 Guardrail gate"
git push -u origin demo-fails-guardrail || true

# Branch 3 · eval regression
git checkout main
git checkout -b demo-regresses-eval
python3 - <<'PY_EDIT2'
from pathlib import Path
p = Path("src/rag/retrieve.py")
s = p.read_text()
inject = '\n    # INTENTIONAL REGRESSION · random vectors (demo-regresses-eval)\n    import random; qvec = [random.random() for _ in range(len(qvec))]\n'
s = s.replace("    if s.mode == \"azure\":", inject + "    if s.mode == \"azure\":", 1)
p.write_text(s)
PY_EDIT2
echo "# demo-regresses-eval · DO NOT MERGE" > BRANCH_README.md
echo "Retrieval randomised · G4 Eval Regression gate fires." >> BRANCH_README.md
git add -A
git commit -m "demo: retrieval regression to demonstrate G4 Eval Regression gate"
git push -u origin demo-regresses-eval || true

git checkout main
echo "✓ Three demo-fails branches created · file PRs against main to surface failing CI"
