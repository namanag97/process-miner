#!/bin/bash
# Comprehensive User Journey Data Path Tracer
# Traces all 6 user journeys and identifies potential issues

OUTPUT_DIR="/Users/namanagarwal/system/dev-logs/journey-audit"
mkdir -p "$OUTPUT_DIR"

echo "=== User Journey Data Path Audit ===" > "$OUTPUT_DIR/audit_report.md"
echo "Generated: $(date)" >> "$OUTPUT_DIR/audit_report.md"
echo "" >> "$OUTPUT_DIR/audit_report.md"

# Function to search and report
search_pattern() {
    local pattern="$1"
    local description="$2"
    local output_file="$3"
    echo "### $description" >> "$output_file"
    echo '```' >> "$output_file"
    rg -n --type py --type ts --type tsx "$pattern" /Users/namanagarwal/system/backend/src /Users/namanagarwal/system/frontend-new/src 2>/dev/null | head -50 >> "$output_file"
    echo '```' >> "$output_file"
    echo "" >> "$output_file"
}

# ==========================================
# JOURNEY 1: User Onboarding (Register → Login → Create Project)
# ==========================================
echo "# Journey 1: User Onboarding" >> "$OUTPUT_DIR/audit_report.md"
echo "" >> "$OUTPUT_DIR/audit_report.md"

echo "## Backend Endpoints" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "register|login|create.*project" --type py /Users/namanagarwal/system/backend/src/api 2>/dev/null | head -30 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "## Error Handling Patterns" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "HTTPException|raise.*Exception" --type py /Users/namanagarwal/system/backend/src/features/auth 2>/dev/null >> "$OUTPUT_DIR/audit_report.md"
rg -n "HTTPException|raise.*Exception" --type py /Users/namanagarwal/system/backend/src/features/projects 2>/dev/null >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "## Frontend Hooks" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "useLogin|useRegister|useCreateProject|useMutation.*login|useMutation.*register" /Users/namanagarwal/system/frontend-new/src 2>/dev/null | head -30 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

# ==========================================
# JOURNEY 2: Dataset Upload & Processing (CRITICAL)
# ==========================================
echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "# Journey 2: Dataset Upload & Processing (CRITICAL)" >> "$OUTPUT_DIR/audit_report.md"
echo "" >> "$OUTPUT_DIR/audit_report.md"

echo "## Upload Endpoints" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "upload|ingest|mapping" --type py /Users/namanagarwal/system/backend/src/api 2>/dev/null | head -40 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "## Dataset Service Layer" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "class.*Service|async def" --type py /Users/namanagarwal/system/backend/src/features/datasets 2>/dev/null | head -50 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "## Error Handling in Upload Flow" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "except|raise|HTTPException|logger\." --type py /Users/namanagarwal/system/backend/src/features/datasets 2>/dev/null | head -60 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "## Frontend Upload Components" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "upload|Upload|onError|catch|console\." /Users/namanagarwal/system/frontend-new/src/features/datasets 2>/dev/null | head -50 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

# ==========================================
# JOURNEY 3: Process Discovery
# ==========================================
echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "# Journey 3: Process Discovery" >> "$OUTPUT_DIR/audit_report.md"
echo "" >> "$OUTPUT_DIR/audit_report.md"

echo "## Mining Endpoints" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "miner|mining|dfg|discover" --type py /Users/namanagarwal/system/backend/src 2>/dev/null | head -50 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "## Frontend Discovery Components" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "discovery|Discovery|miner|Miner|DFG" /Users/namanagarwal/system/frontend-new/src/features 2>/dev/null | head -40 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

# ==========================================
# JOURNEY 4: Process Analysis
# ==========================================
echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "# Journey 4: Process Analysis" >> "$OUTPUT_DIR/audit_report.md"
echo "" >> "$OUTPUT_DIR/audit_report.md"

echo "## Analysis Endpoints" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "variant|bottleneck|analysis" --type py /Users/namanagarwal/system/backend/src 2>/dev/null | head -50 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

# ==========================================
# JOURNEY 5: Conformance Checking
# ==========================================
echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "# Journey 5: Conformance Checking" >> "$OUTPUT_DIR/audit_report.md"
echo "" >> "$OUTPUT_DIR/audit_report.md"

echo "## Conformance Endpoints" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "conformance|diagnostic|model.*check" --type py /Users/namanagarwal/system/backend/src 2>/dev/null | head -40 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

# ==========================================
# JOURNEY 6: Workflow Execution
# ==========================================
echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "# Journey 6: Workflow Execution" >> "$OUTPUT_DIR/audit_report.md"
echo "" >> "$OUTPUT_DIR/audit_report.md"

echo "## Temporal Workflows" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "workflow|@workflow|execute_workflow|poll" --type py /Users/namanagarwal/system/backend/src 2>/dev/null | head -50 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

# ==========================================
# CROSS-CUTTING CONCERNS
# ==========================================
echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "# Cross-Cutting Concerns" >> "$OUTPUT_DIR/audit_report.md"
echo "" >> "$OUTPUT_DIR/audit_report.md"

echo "## Bare Exception Handlers (POTENTIAL BUGS)" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "except Exception:" --type py /Users/namanagarwal/system/backend/src 2>/dev/null >> "$OUTPUT_DIR/audit_report.md"
rg -n "except:" --type py /Users/namanagarwal/system/backend/src 2>/dev/null >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "## Missing Logger Imports" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
for f in $(find /Users/namanagarwal/system/backend/src -name "*.py" -type f); do
    if ! grep -q "import.*logger\|from.*log\|logging" "$f" 2>/dev/null; then
        if grep -q "def \|class " "$f" 2>/dev/null; then
            echo "$f: NO LOGGER IMPORTED" >> "$OUTPUT_DIR/audit_report.md"
        fi
    fi
done
echo '```' >> "$OUTPUT_DIR/audit_report.md"

echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "## Console.log/error in Frontend" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "console\.(log|error|warn)" /Users/namanagarwal/system/frontend-new/src 2>/dev/null | head -50 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "## Silent Error Swallowing" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n -B2 -A2 "except.*:\s*$\|catch.*{\s*$" --type py /Users/namanagarwal/system/backend/src 2>/dev/null | head -30 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

echo "" >> "$OUTPUT_DIR/audit_report.md"
echo "## TODO/FIXME Comments" >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"
rg -n "TODO|FIXME|HACK|XXX" /Users/namanagarwal/system/backend/src /Users/namanagarwal/system/frontend-new/src 2>/dev/null | head -50 >> "$OUTPUT_DIR/audit_report.md"
echo '```' >> "$OUTPUT_DIR/audit_report.md"

echo "Audit complete! Report saved to $OUTPUT_DIR/audit_report.md"
