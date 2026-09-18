#!/usr/bin/env sh
# Install (or update) the incremental-work-order skill into an agent's skills directory.
#
#   ./install.sh                     # clone into the first existing skills dir, or ~/.agents/skills
#   ./install.sh --target ~/.claude/skills
#   ./install.sh --tag v0.1.0        # pin a release (also gives you `git pull` updates later)
#   ./install.sh --from . --copy     # install this local checkout
#   ./install.sh --update            # fast-forward an existing install (keeps a pinned tag checked out)
#
# No dependencies beyond git and a POSIX shell. Nothing is written outside the target directory.
set -eu

REPO="https://github.com/mmm-05610/incremental-work-order"
NAME="incremental-work-order"
TARGET=""
TAG=""
FROM=""
COPY=0
UPDATE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="${2:?--target needs a directory}"; shift 2 ;;
    --tag)    TAG="${2:?--tag needs a ref}"; shift 2 ;;
    --from)   FROM="${2:?--from needs a path}"; shift 2 ;;
    --copy)   COPY=1; shift ;;
    --update) UPDATE=1; shift ;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$TARGET" ]; then
  for candidate in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
    if [ -d "$candidate" ]; then TARGET="$candidate"; break; fi
  done
  TARGET="${TARGET:-$HOME/.agents/skills}"
fi
DEST="$TARGET/$NAME"

if [ -e "$DEST" ] && [ "$UPDATE" -eq 0 ]; then
  echo "already installed at $DEST" >&2
  echo "re-run with --update to fast-forward, or remove it first" >&2
  exit 1
fi

if [ "$UPDATE" -eq 1 ]; then
  [ -d "$DEST/.git" ] || { echo "$DEST is not a git checkout; cannot --update" >&2; exit 1; }
  git -C "$DEST" fetch --tags --prune origin
  if [ -n "$TAG" ]; then git -C "$DEST" checkout --quiet "$TAG"; else git -C "$DEST" pull --ff-only; fi
  echo "updated $DEST to $(git -C "$DEST" describe --tags --always)"
  exit 0
fi

mkdir -p "$TARGET"
if [ -n "$FROM" ]; then
  if [ "$COPY" -eq 1 ]; then
    mkdir -p "$DEST"
    (cd "$FROM" && tar --exclude .git -cf - .) | (cd "$DEST" && tar -xf -)
    echo "copied $(cd "$FROM" && pwd) -> $DEST"
  else
    ln -s "$(cd "$FROM" && pwd)" "$DEST"
    echo "linked $DEST -> $(cd "$FROM" && pwd)"
  fi
else
  if [ -n "$TAG" ]; then
    git clone --quiet --branch "$TAG" --depth 1 "$REPO" "$DEST"
  else
    git clone --quiet "$REPO" "$DEST"
  fi
  echo "installed $(git -C "$DEST" describe --tags --always) -> $DEST"
fi

echo
echo "next:"
echo "  * keep exactly one copy — a project-local .agents/skills/$NAME shadows this one"
echo "  * read GETTING-STARTED.md, then ask your agent to initialize the workflow in your repo"
