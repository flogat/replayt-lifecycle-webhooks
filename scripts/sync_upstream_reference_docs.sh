#!/usr/bin/env bash
set -euo pipefail

# Optional maintainer helper: copy a local upstream docs tree into the gitignored
# snapshot directory. Not invoked by CI or pytest.
#
# Usage:
#   ./scripts/sync_upstream_reference_docs.sh /path/to/replayt/docs
#   UPSTREAM_DOCS=/path/to/replayt/docs ./scripts/sync_upstream_reference_docs.sh

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly SNAPSHOT_ROOT="${REPO_ROOT}/docs/reference-documentation/_upstream_snapshot"
readonly DEST="${SNAPSHOT_ROOT}/replayt-docs"

upstream="${UPSTREAM_DOCS-}"
if [[ $# -ge 1 ]]; then
  upstream="$1"
fi

if [[ -z "${upstream}" ]]; then
  echo "error: set UPSTREAM_DOCS or pass the path to the upstream docs directory" >&2
  echo "example: $0 \"\$HOME/src/replayt/docs\"" >&2
  exit 1
fi

if [[ ! -d "${upstream}" ]]; then
  echo "error: upstream docs directory not found: ${upstream}" >&2
  exit 1
fi

mkdir -p "${SNAPSHOT_ROOT}"

if command -v rsync >/dev/null 2>&1; then
  mkdir -p "${DEST}"
  rsync -a --delete "${upstream}/" "${DEST}/"
else
  rm -rf "${DEST}"
  mkdir -p "${DEST}"
  cp -a "${upstream}/." "${DEST}/"
fi

echo "Synced into ${DEST} (gitignored; do not commit)"
