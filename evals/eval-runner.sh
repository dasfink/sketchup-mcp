#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results/$(date +%Y-%m-%d-%H%M%S)"
mkdir -p "$RESULTS_DIR"

case "${1:-help}" in
  layer1)
    echo "Running Layer 1: Decision Evals..."
    for f in "$SCRIPT_DIR"/layer1-decisions/*.json; do
      echo "  Processing $(basename "$f")..."
      python3 "$SCRIPT_DIR/run_layer1.py" "$f" "$RESULTS_DIR"
    done
    passed=$(grep -rl '"pass": true' "$RESULTS_DIR" 2>/dev/null | wc -l || echo 0)
    total=$(ls "$RESULTS_DIR"/*-results.json 2>/dev/null | wc -l || echo 0)
    echo "Layer 1: $passed/$total passed"
    ;;
  layer2)
    echo "Layer 2: Execution Evals (requires SketchUp running)"
    echo "Run each case manually via Claude Code with SketchUp MCP connected."
    echo "Cases: $SCRIPT_DIR/layer2-execution/*.json"
    ;;
  layer3)
    echo "Layer 3: Integration Evals (manual)"
    echo "Run each project prompt via Claude Code with furniture-design-sketchup skill."
    echo "Cases: $SCRIPT_DIR/layer3-integration/*.json"
    echo "Score using rubric in $SCRIPT_DIR/scoring.md"
    ;;
  *)
    echo "Usage: $0 [layer1|layer2|layer3]"
    ;;
esac
echo "Results: $RESULTS_DIR"
