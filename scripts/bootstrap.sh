#!/usr/bin/env bash
# Compatibility wrapper; bootstrap.py is the cross-platform implementation.
set -euo pipefail
cd "$(dirname "$0")/.."
exec "${PYTHON:-python3}" scripts/bootstrap.py "$@"
