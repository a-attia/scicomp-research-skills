#!/usr/bin/env bash
#
# refresh.sh -- refresh the canonical checkout at ~/.scicomp-research-skills/
#
# Run this on any machine where you want the canonical checkout to pick
# up the latest changes from the GitHub remote.
#
# Idempotent + safe: uses --ff-only so it refuses to merge if there are
# divergent local changes (which there should never be in the canonical
# checkout because of the pre-commit hook; if there are, that's a bug
# you want to know about).

set -euo pipefail

CANONICAL="${HOME}/.scicomp-research-skills"

if [[ ! -d "${CANONICAL}/.git" ]]; then
  echo "ERROR: canonical checkout not found at ${CANONICAL}" >&2
  echo "Run install.sh first, or clone the repo to ${CANONICAL}." >&2
  exit 1
fi

echo "Refreshing ${CANONICAL} ..."
git -C "${CANONICAL}" fetch --quiet
git -C "${CANONICAL}" pull --ff-only

# Print last-revised summary so the user knows what they have.
LAST_COMMIT_DATE=$(git -C "${CANONICAL}" log -1 --format='%cd' --date=short)
LAST_COMMIT_MSG=$(git -C "${CANONICAL}" log -1 --format='%s')
echo
echo "Canonical checkout up to date."
echo "  Last commit: ${LAST_COMMIT_DATE}  ${LAST_COMMIT_MSG}"
