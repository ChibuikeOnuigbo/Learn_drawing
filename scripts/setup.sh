#!/usr/bin/env bash
# Legacy entry point retained for existing instructions.
set -euo pipefail
exec "$(dirname "$0")/bootstrap.sh" "$@"
