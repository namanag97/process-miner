#!/bin/bash
# Quick test runner with failure summary

echo "Running API tests..."
.venv/bin/python -m pytest tests/api/ -v --tb=no --maxfail=999 -q > /tmp/test_results.txt 2>&1

echo ""
echo "========== TEST SUMMARY =========="
grep -E "passed|failed|error" /tmp/test_results.txt | tail -1

echo ""
echo "========== FAILED TESTS =========="
grep "FAILED" /tmp/test_results.txt | head -30

echo ""
echo "========== ERROR TYPES =========="
grep -E "(assert|Error|404|401|403|500)" /tmp/test_results.txt | sort | uniq -c | sort -rn | head -20
