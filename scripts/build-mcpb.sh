#!/usr/bin/env bash
# Build the Claude Desktop .mcpb bundle from the latest server.py
set -euo pipefail
cd "$(dirname "$0")/.."
VERSION=$(grep '"version"' mcpb-build/manifest.json | head -1 | sed 's/.*"\([0-9.]*\)".*/\1/')
echo "Building sibo-research-db v${VERSION}.mcpb..."
cp server.py mcpb-build/src/server.py
npx -y --package=@anthropic-ai/mcpb mcpb validate mcpb-build/manifest.json
npx -y --package=@anthropic-ai/mcpb mcpb pack mcpb-build "sibo-research-db-${VERSION}.mcpb"
echo "Built: sibo-research-db-${VERSION}.mcpb"
