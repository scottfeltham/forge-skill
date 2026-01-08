#!/bin/bash
# FORGE Status Line for Claude Code
# Displays current FORGE development cycle and phase information

# Read JSON input from stdin
input=$(cat)

# Extract workspace information
current_dir=$(echo "$input" | jq -r '.workspace.current_dir')
model=$(echo "$input" | jq -r '.model.display_name')

# Find .forge directory by walking up from current directory
forge_dir=""
search_dir="$current_dir"
while [ "$search_dir" != "/" ]; do
  if [ -d "$search_dir/.forge" ]; then
    forge_dir="$search_dir/.forge"
    break
  fi
  search_dir=$(dirname "$search_dir")
done

# Default status line (no FORGE project detected)
if [ -z "$forge_dir" ]; then
  # Git info
  git_info=""
  if [ -d "$current_dir/.git" ]; then
    cd "$current_dir" 2>/dev/null && \
    git_branch=$(git -c advice.detachedHead=false branch --show-current 2>/dev/null || git rev-parse --short HEAD 2>/dev/null) && \
    git_status=$(git status --porcelain 2>/dev/null) && \
    [ -n "$git_branch" ] && git_info=" │ $git_branch$([ -n "$git_status" ] && echo "*")"
  fi

  printf "\033[2m%s │ %s%s │ %s\033[0m" "$(basename "$current_dir")" "$model" "$git_info" "$(date +%H:%M)"
  exit 0
fi

# FORGE project detected - look for active cycles
active_cycles_dir="$forge_dir/cycles/active"
cycle_info=""

if [ -d "$active_cycles_dir" ]; then
  # Find the most recently modified cycle file
  latest_cycle=$(find "$active_cycles_dir" -name "*.md" -type f -exec ls -t {} + 2>/dev/null | head -1)

  if [ -n "$latest_cycle" ]; then
    # Extract cycle name from filename
    cycle_name=$(basename "$latest_cycle" .md)

    # Extract phase from the Status line in the file
    phase_line=$(grep -i "^\*\*Status\*\*:" "$latest_cycle" | head -1)

    if [ -n "$phase_line" ]; then
      # Extract phase name
      phase=$(echo "$phase_line" | sed -E 's/.*Status.*: *([A-Za-z]+).*/\1/')

      # Shorten cycle name if too long
      if [ ${#cycle_name} -gt 30 ]; then
        cycle_name="${cycle_name:0:27}..."
      fi

      cycle_info="$phase: $cycle_name"
    fi
  fi
fi

# If no cycle info found, show "No Active Cycle"
if [ -z "$cycle_info" ]; then
  cycle_info="No Active Cycle"
fi

# Git info
git_info=""
if [ -d "$current_dir/.git" ]; then
  cd "$current_dir" 2>/dev/null && \
  git_branch=$(git -c advice.detachedHead=false branch --show-current 2>/dev/null || git rev-parse --short HEAD 2>/dev/null) && \
  git_status=$(git status --porcelain 2>/dev/null) && \
  [ -n "$git_branch" ] && git_info=" │ $git_branch$([ -n "$git_status" ] && echo "*")"
fi

# Display status line with FORGE info
printf "\033[2m%s │ %s%s │ %s\033[0m" "$cycle_info" "$model" "$git_info" "$(date +%H:%M)"
