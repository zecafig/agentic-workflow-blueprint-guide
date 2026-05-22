#!/usr/bin/env bash
set -euo pipefail

GUIDE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OFFICIAL_AWB_DIR="${OFFICIAL_AWB_REPO:-$GUIDE_DIR/../agentic-workflow-blueprint}"

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "[FAIL] Missing file: $path"
    return 1
  fi
  echo "[OK] File exists: $path"
}

require_dir() {
  local path="$1"
  if [[ ! -d "$path" ]]; then
    echo "[FAIL] Missing directory: $path"
    return 1
  fi
  echo "[OK] Directory exists: $path"
}

check_contains() {
  local file="$1"
  local needle="$2"
  if ! grep -Fq "$needle" "$file"; then
    echo "[FAIL] Missing required text in $file: $needle"
    return 1
  fi
  echo "[OK] Found in $file: $needle"
}

check_absent() {
  local file="$1"
  local needle="$2"
  if grep -Fq "$needle" "$file"; then
    echo "[FAIL] Forbidden text found in $file: $needle"
    return 1
  fi
  echo "[OK] Not present in $file: $needle"
}

check_glob_absent() {
  local pattern="$1"
  if compgen -G "$pattern" > /dev/null; then
    echo "[FAIL] Forbidden generated files found matching: $pattern"
    return 1
  fi
  echo "[OK] No files matching forbidden pattern: $pattern"
}

require_git_up_to_date() {
  local repo="$1"

  if [[ ! -d "$repo/.git" ]]; then
    echo "[FAIL] Not a git repository: $repo"
    return 1
  fi

  echo "[INFO] Fetching latest refs for official AWB repo..."
  git -C "$repo" fetch --quiet --all --prune

  local upstream
  upstream="$(git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)"
  if [[ -z "$upstream" ]]; then
    echo "[FAIL] Official repo has no upstream tracking branch configured."
    echo "       Configure upstream or run audit with a tracked branch."
    return 1
  fi

  local ahead
  local behind
  read -r ahead behind <<< "$(git -C "$repo" rev-list --left-right --count "HEAD...$upstream")"

  if [[ "$behind" != "0" ]]; then
    echo "[FAIL] Official AWB repo is behind upstream by $behind commit(s)."
    echo "       Run: git -C '$repo' pull --ff-only"
    return 1
  fi

  echo "[OK] Official AWB repo is up to date with upstream: $upstream"

  if [[ -n "$(git -C "$repo" status --porcelain)" ]]; then
    echo "[WARN] Official AWB repo has local uncommitted changes."
    echo "       Audit uses local content; confirm this is intentional."
  else
    echo "[OK] Official AWB repo working tree is clean."
  fi
}

main() {
  local failures=0

  echo "== Pre-bootstrap audit =="
  echo "Guide repo:    $GUIDE_DIR"
  echo "Official AWB:  $OFFICIAL_AWB_DIR"

  require_dir "$OFFICIAL_AWB_DIR" || ((failures+=1))
  require_file "$OFFICIAL_AWB_DIR/AGENTS.md" || ((failures+=1))
  require_file "$OFFICIAL_AWB_DIR/SKILL.md" || ((failures+=1))
  require_file "$OFFICIAL_AWB_DIR/README.md" || ((failures+=1))
  require_dir "$OFFICIAL_AWB_DIR/workflows" || ((failures+=1))
  require_dir "$OFFICIAL_AWB_DIR/runbooks" || ((failures+=1))

  require_file "$GUIDE_DIR/README.md" || ((failures+=1))
  require_file "$GUIDE_DIR/agentic_workflow_blueprint_guidance.md" || ((failures+=1))
  require_file "$GUIDE_DIR/bootstrap_checklist.md" || ((failures+=1))
  require_file "$GUIDE_DIR/blue_print_used_on_creation.md" || ((failures+=1))
  require_file "$GUIDE_DIR/python3/guide_me.py" || ((failures+=1))
  require_file "$GUIDE_DIR/python3/helpers.py" || ((failures+=1))

  require_git_up_to_date "$OFFICIAL_AWB_DIR" || ((failures+=1))

  echo "== Contract alignment checks =="
  check_contains "$GUIDE_DIR/agentic_workflow_blueprint_guidance.md" "source of truth" || ((failures+=1))
  check_contains "$GUIDE_DIR/agentic_workflow_blueprint_guidance.md" "Required Workflow Contract Sections" || ((failures+=1))
  check_contains "$GUIDE_DIR/bootstrap_checklist.md" "Every workflow contract includes required sections" || ((failures+=1))
  check_contains "$GUIDE_DIR/python3/guide_me.py" "Canonical Constraints" || ((failures+=1))

  check_absent "$GUIDE_DIR/agentic_workflow_blueprint_guidance.md" 'Start the work while you are inside the official `agentic-workflow-blueprint` repository' || ((failures+=1))
  check_absent "$GUIDE_DIR/python3/guide_me.py" "Python 3 only" || ((failures+=1))
  check_absent "$GUIDE_DIR/python3/guide_me.py" "ruff check" || ((failures+=1))

  echo "== Guide cleanliness checks =="
  check_glob_absent "$GUIDE_DIR/blueprint_inputs_*.json" || ((failures+=1))
  check_glob_absent "$GUIDE_DIR/blueprint_inputs_*.md" || ((failures+=1))
  check_glob_absent "$GUIDE_DIR/blue_print_used_on_creation_blueprint_inputs_*.md" || ((failures+=1))

  echo "== Official inventory snapshot checks =="
  local workflow
  while IFS= read -r workflow; do
    check_contains "$GUIDE_DIR/README.md" "$workflow" || ((failures+=1))
    check_contains "$GUIDE_DIR/agentic_workflow_blueprint_guidance.md" "$workflow" || ((failures+=1))
    check_contains "$GUIDE_DIR/blue_print_used_on_creation.md" "$workflow" || ((failures+=1))
  done < <(find "$OFFICIAL_AWB_DIR/workflows" -mindepth 2 -maxdepth 2 -name SKILL.md -print | xargs -n1 dirname | xargs -n1 basename | sort -u)

  local runbook
  while IFS= read -r runbook; do
    check_contains "$GUIDE_DIR/README.md" "$runbook" || ((failures+=1))
    check_contains "$GUIDE_DIR/agentic_workflow_blueprint_guidance.md" "$runbook" || ((failures+=1))
    check_contains "$GUIDE_DIR/blue_print_used_on_creation.md" "$runbook" || ((failures+=1))
  done < <(find "$OFFICIAL_AWB_DIR/runbooks" -mindepth 1 -maxdepth 1 -type f -name '*.md' -print | xargs -n1 basename | sort -u)

  echo
  if [[ "$failures" -gt 0 ]]; then
    echo "Pre-bootstrap audit FAILED with $failures issue(s)."
    exit 1
  fi

  echo "Pre-bootstrap audit PASSED. Safe to proceed with bootstrap."
}

main "$@"
