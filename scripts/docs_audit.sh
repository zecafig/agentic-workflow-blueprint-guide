#!/usr/bin/env bash
set -euo pipefail

GUIDE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0

require_contains() {
  local file="$1"
  local needle="$2"
  if ! grep -Fq "$needle" "$file"; then
    echo "[FAIL] Missing required text in $file: $needle"
    return 1
  fi
  echo "[OK] Found in $file: $needle"
}

forbid_contains() {
  local file="$1"
  local needle="$2"
  if grep -Fq "$needle" "$file"; then
    echo "[FAIL] Forbidden text found in $file: $needle"
    return 1
  fi
  echo "[OK] Not present in $file: $needle"
}

echo "== Documentation consistency audit =="

require_contains "$GUIDE_DIR/README.md" "supports only Python 3 bootstrap workflows" || ((failures+=1))
require_contains "$GUIDE_DIR/README.md" "python3 python3/guide_me.py" || ((failures+=1))
require_contains "$GUIDE_DIR/README.md" "Developers, not AI, decide and execute virtual environment setup" || ((failures+=1))
require_contains "$GUIDE_DIR/README.md" "skills catalog" || ((failures+=1))
require_contains "$GUIDE_DIR/agentic_workflow_blueprint_guidance.md" "official skills catalog" || ((failures+=1))
require_contains "$GUIDE_DIR/bootstrap_checklist.md" "official AWB skills catalog" || ((failures+=1))
require_contains "$GUIDE_DIR/bootstrap_checklist.md" "Python 3 entrypoint" || ((failures+=1))
require_contains "$GUIDE_DIR/bootstrap_checklist.md" "development team owns environment, dependencies, tests/coverage, automation, database, and backend/frontend implementation decisions" || ((failures+=1))
require_contains "$GUIDE_DIR/python3/README.md" "Keep this folder Python-only" || ((failures+=1))
require_contains "$GUIDE_DIR/python3/README.md" "AI in this guide supports bootstrap guidance and artifact preparation" || ((failures+=1))
require_contains "$GUIDE_DIR/python3/guide_me.py" "Python 3, FastAPI, PostgreSQL, Redis, Celery" || ((failures+=1))
require_contains "$GUIDE_DIR/agentic_workflow_blueprint_guidance.md" "Developers own language, stack, and implementation decisions" || ((failures+=1))

forbid_contains "$GUIDE_DIR/README.md" "Other languages: planned" || ((failures+=1))
forbid_contains "$GUIDE_DIR/README.md" "Choose your project language/stack profile" || ((failures+=1))
forbid_contains "$GUIDE_DIR/README.md" "source that feeds your AWB scaffolding decisions" || ((failures+=1))
forbid_contains "$GUIDE_DIR/bootstrap_checklist.md" "available language entrypoint" || ((failures+=1))
forbid_contains "$GUIDE_DIR/python3/guide_me.py" "examples: Node.js, Python, PostgreSQL, Redis, React" || ((failures+=1))

echo
if [[ "$failures" -gt 0 ]]; then
  echo "Documentation audit FAILED with $failures issue(s)."
  exit 1
fi

echo "Documentation audit PASSED."
