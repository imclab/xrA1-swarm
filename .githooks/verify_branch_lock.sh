#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() {
  echo "[branch-lock] FAIL: $1" >&2
  exit 1
}

pass() {
  echo "[branch-lock] PASS: $1"
}

hooks_path="$(git config --local --get core.hooksPath || true)"
if [ "$hooks_path" != ".githooks" ]; then
  fail "core.hooksPath is '$hooks_path' (expected '.githooks'). Run: git config --local core.hooksPath .githooks"
fi
pass "core.hooksPath=.githooks"

[ -x ".githooks/pre-commit" ] || fail ".githooks/pre-commit is not executable"
[ -x ".githooks/pre-push" ] || fail ".githooks/pre-push is not executable"
pass "hook executables are present"

set +e
printf "refs/heads/codemini-isolated 111 refs/heads/main 222\n" | .githooks/pre-push origin https://example.invalid >/dev/null 2>&1
blocked_main_rc=$?
printf "refs/heads/codemini-isolated 111 refs/heads/codemini-isolated 222\n" | .githooks/pre-push origin https://example.invalid >/dev/null 2>&1
allowed_branch_rc=$?
set -e

[ "$blocked_main_rc" -ne 0 ] || fail "pre-push did not block push to refs/heads/main"
[ "$allowed_branch_rc" -eq 0 ] || fail "pre-push unexpectedly blocked non-main branch push"
pass "pre-push block/allow behavior verified"

echo "[branch-lock] OK"

