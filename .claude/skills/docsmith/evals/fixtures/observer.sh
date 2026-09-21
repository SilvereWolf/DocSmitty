#!/usr/bin/env bash
# Observer — pre-execution guardrail. Exit 0 = allow, 1 = block, 2 = needs human.
# Usage: observer.sh "<command or action description>"
set -u
ACTION="${1:-}"
LOG="$(dirname "$0")/observer.log"
ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

deny=(
  'rm -rf /' 'rm -rf ~' 'rm -rf \.\.'
  'git push .*--force' 'git push .*origin (main|master)'
  'git commit .*--no-verify' 'git push .*--no-verify'
  'DROP TABLE' 'DROP DATABASE' 'TRUNCATE '
  'terraform (destroy|apply)'
  'chmod 777' 'curl .*\| *(ba)?sh' 'wget .*\| *(ba)?sh'
)
protected_paths=( '\.env' 'secrets/' '\.git/config' 'harness/core_memory\.md' 'harness/observer\.' '\.github/workflows/harness-gate' )
confirm=( 'rm -r ' 'git rm -r' 'npm uninstall' 'pip uninstall' 'migrate' 'drop_column' )

for p in "${deny[@]}"; do
  if echo "$ACTION" | grep -qiE "$p"; then
    echo "$(ts) BLOCK  [$p] :: $ACTION" >> "$LOG"
    echo "OBSERVER BLOCK: matches immutable deny rule [$p]"; exit 1
  fi
done
for p in "${protected_paths[@]}"; do
  if echo "$ACTION" | grep -qiE "(cat|less|vim|nano|echo.*>|sed|tee|cp|mv|rm).*$p"; then
    echo "$(ts) BLOCK  [protected-path $p] :: $ACTION" >> "$LOG"
    echo "OBSERVER BLOCK: protected path [$p]"; exit 1
  fi
done
for p in "${confirm[@]}"; do
  if echo "$ACTION" | grep -qiE "$p"; then
    echo "$(ts) HUMAN  [$p] :: $ACTION" >> "$LOG"
    echo "OBSERVER: destructive-class action [$p] — requires explicit human confirmation"; exit 2
  fi
done
echo "$(ts) ALLOW  :: $ACTION" >> "$LOG"
exit 0
