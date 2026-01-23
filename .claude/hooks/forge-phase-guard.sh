#!/bin/bash
#
# FORGE Phase Guard Hook
# Enforces phase constraints by blocking code writes during Focus, Orchestrate, Refine phases.
# Allows document writes to docs/ in any phase.
#
# Usage: Configure in .claude/settings.json:
#   {
#     "hooks": {
#       "PreToolUse": [{
#         "matcher": "Edit|Write",
#         "command": [".claude/hooks/forge-phase-guard.sh"]
#       }]
#     }
#   }
#

# Read tool input from stdin
TOOL_INPUT=$(cat)

# Extract file path from JSON input
FILE_PATH=$(echo "$TOOL_INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')

# If no file path found, allow (might be a different tool structure)
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Always allow writes to docs/ directory (PRDs, specs, architecture docs)
if [[ "$FILE_PATH" == */docs/* ]] || [[ "$FILE_PATH" == docs/* ]]; then
  exit 0
fi

# Always allow writes to .forge/ directory (state management)
if [[ "$FILE_PATH" == */.forge/* ]] || [[ "$FILE_PATH" == .forge/* ]]; then
  exit 0
fi

# Always allow writes to test files (TDD support)
if [[ "$FILE_PATH" == *test* ]] || [[ "$FILE_PATH" == *spec* ]] || [[ "$FILE_PATH" == *_test.* ]] || [[ "$FILE_PATH" == *.test.* ]]; then
  exit 0
fi

# Find current phase from active cycle files
PHASE=""
if [ -d ".forge/cycles/active" ]; then
  # Look for phase marker in active cycle files
  # Format: phase: Focus (or phase: "Focus")
  PHASE=$(grep -h "^phase:" .forge/cycles/active/*.yaml .forge/cycles/active/*.md 2>/dev/null | head -1 | sed 's/phase:[[:space:]]*"\?\([^"]*\)"\?/\1/' | tr -d '[:space:]')
fi

# If no active cycle or phase found, allow writes (FORGE not active)
if [ -z "$PHASE" ]; then
  exit 0
fi

# Normalize phase name (case-insensitive comparison)
PHASE_LOWER=$(echo "$PHASE" | tr '[:upper:]' '[:lower:]')

# Code file patterns
CODE_PATTERNS=(
  "*.js" "*.ts" "*.jsx" "*.tsx"
  "*.py" "*.pyw"
  "*.go"
  "*.rs"
  "*.java" "*.kt" "*.scala"
  "*.c" "*.cpp" "*.cc" "*.h" "*.hpp"
  "*.rb"
  "*.php"
  "*.swift"
  "*.cs"
  "*.sh" "*.bash" "*.zsh"
)

# Check if file matches code patterns
IS_CODE=false
for pattern in "${CODE_PATTERNS[@]}"; do
  case "$FILE_PATH" in
    $pattern)
      IS_CODE=true
      break
      ;;
  esac
done

# Also check for src/, lib/, components/ directories as code indicators
if [[ "$FILE_PATH" == */src/* ]] || [[ "$FILE_PATH" == src/* ]] || \
   [[ "$FILE_PATH" == */lib/* ]] || [[ "$FILE_PATH" == lib/* ]] || \
   [[ "$FILE_PATH" == */components/* ]] || [[ "$FILE_PATH" == components/* ]] || \
   [[ "$FILE_PATH" == */app/* ]] || [[ "$FILE_PATH" == app/* ]]; then
  IS_CODE=true
fi

# Block code writes during Focus, Orchestrate, Refine phases
if [ "$IS_CODE" = true ]; then
  case "$PHASE_LOWER" in
    focus|orchestrate|refine)
      # Output block decision as JSON
      cat << EOF
{
  "decision": "block",
  "reason": "FORGE: No code during ${PHASE} phase. Write specifications to docs/ instead. Current phase: ${PHASE}"
}
EOF
      exit 2  # Exit code 2 signals block
      ;;
  esac
fi

# Allow all other writes
exit 0
