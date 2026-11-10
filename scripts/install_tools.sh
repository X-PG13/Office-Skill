#!/usr/bin/env bash
# Install the QA toolchain: LibreOffice, a PDF rasterizer, and the fonts the
# engines name explicitly. Pinned Python packages come from pyproject.toml.
set -euo pipefail

if command -v sudo >/dev/null 2>&1 && [[ "$(id -u)" -ne 0 ]]; then
  SUDO="sudo"
else
  SUDO=""
fi

$SUDO apt-get update
$SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y \
  libreoffice \
  poppler-utils \
  fonts-noto-cjk \
  fonts-liberation \
  fontconfig

fc-cache -f >/dev/null

python3 -m pip install -e ".[dev]"

echo "QA fonts expected by the profiles:"
fc-list : family | grep -E 'Noto Sans CJK SC|Noto Serif CJK SC|Liberation Sans|Liberation Serif|Liberation Mono' | sort -u
echo "soffice: $(command -v soffice)"
echo "pdftoppm: $(command -v pdftoppm)"
