#!/bin/bash
# Deploy su_mcp extension to SketchUp plugins directory
set -e

SRC="$(cd "$(dirname "$0")" && pwd)"
PLUGINS_DIR="$HOME/Library/Application Support/SketchUp 2026/SketchUp/Plugins"

echo "Deploying su_mcp from $SRC to SketchUp plugins..."

# Copy loader
cp "$SRC/su_mcp.rb" "$PLUGINS_DIR/su_mcp.rb"

# Copy extension files
mkdir -p "$PLUGINS_DIR/su_mcp"
for f in main.rb woodworking.rb package.rb extension.json; do
  cp "$SRC/su_mcp/$f" "$PLUGINS_DIR/su_mcp/$f"
done

# Clean up any stale signature artifacts (SketchUp .rbs is proprietary, can't self-sign)
rm -f "$PLUGINS_DIR/su_mcp.rbs"
rm -f "$PLUGINS_DIR/su_mcp/"*.rbs
rm -f "$PLUGINS_DIR/su_mcp/signature.sig" "$PLUGINS_DIR/su_mcp/signing_cert.pem"

echo "Deployed. Restart SketchUp or reload from Ruby console:"
echo '  load "su_mcp/woodworking.rb"; load "su_mcp/main.rb"'
