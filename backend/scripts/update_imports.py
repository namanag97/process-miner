import os
import re

# Mapping of old module paths to new module paths
MODULE_MAPPING = {
    # Services
    "src.services.dataset_writer": "src.features.process_mining.services.writer",
    "src.services.event_log_loader": "src.features.process_mining.services.loader",
    "src.services.filtering": "src.features.process_mining.services.filtering",
    "src.services.ingestion": "src.features.process_mining.services.ingestion",
    "src.services.duckdb_ingestion": "src.features.process_mining.services.ingestion.duckdb",
    "src.services.unified_ingestion": "src.features.process_mining.services.ingestion.unified",
    "src.services.event_stream": "src.features.process_mining.services.ingestion.stream",
    "src.services.mining": "src.features.process_mining.services.mining",
    "src.services.mining.": "src.features.process_mining.services.mining_algorithms.", # For submodules
    "src.services.conformance": "src.features.process_mining.services.conformance",
    "src.services.analytics": "src.features.process_mining.services.analytics",
    "src.services.prediction": "src.features.process_mining.services.prediction",
    "src.services.simulation": "src.features.process_mining.services.simulation",
    "src.services.ocpm": "src.features.process_mining.services.ocpm",
    "src.services.organizational": "src.features.process_mining.services.organizational",
    "src.services.hierarchical_mining": "src.features.process_mining.services.hierarchical",
    "src.services.llm": "src.features.process_mining.services.ai",
    "src.services.analysis_registry": "src.features.process_mining.services.registry",
    "src.services.workflow": "src.features.process_mining.services.workflow",
    "src.services.recommendation": "src.features.process_mining.services.recommendation",
    "src.services.model_importer": "src.features.process_mining.services.model_importer",
    "src.services.business_use_cases": "src.features.process_mining.services.business_use_cases",
    "src.services.bottleneck_analyzer": "src.features.process_mining.services.bottleneck",
    "src.services.root_cause_analysis": "src.features.process_mining.services.root_cause",
    
    # Enums (Wave 0 artifacts cleanup + domain move)
    "src.analysis.enums": "src.features.process_mining.enums",
    "src.datasets.enums": "src.features.process_mining.enums",
}

# Generic/Platform schemas
PLATFORM_SCHEMAS = {
    "CurrentUserResponse", "ErrorResponse", "OrganizationResponse", 
    "PaginatedResponse", "PaginationParams", "ProjectCreateRequest", 
    "ProjectDetailResponse", "ProjectListResponse", "ProjectResponse", 
    "ProjectUpdateRequest", "UserResponse", "WorkspaceCreateRequest", 
    "WorkspaceDetailResponse", "WorkspaceListResponse", "WorkspaceMemberResponse", 
    "WorkspaceResponse", "WorkspaceUpdateRequest"
}

# Domain Enums to move from platform.core.enums
DOMAIN_ENUMS = {"MinerType", "ModelFormat", "SourceFormat", "ConformanceMethod"}

def update_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    
    original_content = content
    
    # 1. Update Module Imports (Services)
    for old, new in MODULE_MAPPING.items():
        if old.endswith("."): # Prefix match for submodules
             content = re.sub(rf"from {old}([\w\.]+)", rf"from {new}\1", content)
             content = re.sub(rf"import {old}([\w\.]+)", rf"import {new}\1", content)
        else: # Exact match
            content = re.sub(rf"from {old} import", rf"from {new} import", content)
            content = re.sub(rf"import {old}\s*$", rf"import {new}", content)
            content = re.sub(rf"import {old} as", rf"import {new} as", content)

    # 2. Update Schema Imports (Split src.models.schemas)
    # This is tricky because one import line might have mix of platform and domain schemas.
    # Strategy: Replace 'from src.models.schemas import (...)' with two blocks if needed.
    
    # Simple regex for single-line imports
    # from src.models.schemas import X, Y, Z
    
    def replace_schema_import(match):
        indent = match.group(1) # Capture indentation
        imports_str = match.group(2)
        
        # Parse imports (handle newlines if in parens - regex below handles parens block)
        # But for now let's assume we are matching the whole block
        # Clean up whitespace and newlines
        clean_imports = re.sub(r"\s+", " ", imports_str).strip()
        names = [n.strip() for n in clean_imports.split(",") if n.strip()]
        
        platform_names = []
        domain_names = []
        
        for name in names:
            # Handle alias "X as Y"
            base_name = name.split(" as ")[0]
            if base_name in PLATFORM_SCHEMAS:
                platform_names.append(name)
            else:
                domain_names.append(name) # Default to domain
        
        new_blocks = []
        if platform_names:
            platform_block = f"{indent}from src.infra.schemas import {', '.join(platform_names)}"
            # If line is too long or originally multiline, formatting might be ugly, but auto-formatter can fix.
            # Ideally we keep style.
            if len(platform_names) > 3 or "(" in match.group(0):
                 platform_block = f"{indent}from src.infra.schemas import (\n{indent}    " + f",\n{indent}    ".join(platform_names) + f",\n{indent})"
            new_blocks.append(platform_block)
            
        if domain_names:
            domain_block = f"{indent}from src.features.process_mining.schemas import {', '.join(domain_names)}"
            if len(domain_names) > 3 or "(" in match.group(0):
                domain_block = f"{indent}from src.features.process_mining.schemas import (\n{indent}    " + f",\n{indent}    ".join(domain_names) + f",\n{indent})"
            new_blocks.append(domain_block)
            
        return "\n".join(new_blocks)

    # Regex for Multi-line import from src.models.schemas
    # Matches: from src.models.schemas import (\n ... \n)
    pattern_multiline = re.compile(r"^(\s*)from src\.models\.schemas import \(([\s\S]*?)\)", re.MULTILINE)
    content = pattern_multiline.sub(replace_schema_import, content)
    
    # Regex for Single-line import
    # Matches: from src.models.schemas import A, B, C
    pattern_singleline = re.compile(r"^(\s*)from src\.models\.schemas import ([^\(\n]*?)$", re.MULTILINE)
    content = pattern_singleline.sub(replace_schema_import, content)
    
    # 3. Update Enum Imports (Move generic -> domain)
    # from src.infra.core.enums import MinerType, JobStatus
    def replace_enum_import(match):
        indent = match.group(1)
        imports_str = match.group(2)
        clean_imports = re.sub(r"\s+", " ", imports_str).strip()
        names = [n.strip() for n in clean_imports.split(",") if n.strip()]
        
        platform_enums = []
        domain_enums = []
        
        for name in names:
            base_name = name.split(" as ")[0]
            if base_name in DOMAIN_ENUMS:
                domain_enums.append(name)
            else:
                platform_enums.append(name)
        
        new_blocks = []
        if platform_enums:
            # Reconstruct original import for remaining platform enums
            block = f"{indent}from src.infra.core.enums import {', '.join(platform_enums)}"
            if len(platform_enums) > 3 or "(" in match.group(0):
                block = f"{indent}from src.infra.core.enums import (\n{indent}    " + f",\n{indent}    ".join(platform_enums) + f",\n{indent})"
            new_blocks.append(block)
            
        if domain_enums:
            block = f"{indent}from src.features.process_mining.enums import {', '.join(domain_enums)}"
            if len(domain_enums) > 3 or "(" in match.group(0):
                 block = f"{indent}from src.features.process_mining.enums import (\n{indent}    " + f",\n{indent}    ".join(domain_enums) + f",\n{indent})"
            new_blocks.append(block)
            
        return "\n".join(new_blocks)

    pattern_enums_multi = re.compile(r"^(\s*)from src\.platform\.core\.enums import \(([\s\S]*?)\)", re.MULTILINE)
    content = pattern_enums_multi.sub(replace_enum_import, content)

    pattern_enums_single = re.compile(r"^(\s*)from src\.platform\.core\.enums import ([^\(\n]*?)$", re.MULTILINE)
    content = pattern_enums_single.sub(replace_enum_import, content)

    if content != original_content:
        print(f"Updating {filepath}")
        with open(filepath, "w") as f:
            f.write(content)

def main():
    root_dir = "src" 
    test_dir = "tests"
    
    paths = []
    for d in [root_dir, test_dir]:
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".py"):
                    paths.append(os.path.join(root, file))
    
    # Skip the schemas files themselves to avoid circular refactor logic issues (hand-crafted)
    skip_files = [
        "src/platform/schemas.py",
        "src/features/process_mining/schemas/datasets.py",
        "src/features/process_mining/schemas/analysis.py",
        "src/features/process_mining/schemas/__init__.py",
        "src/models/schemas.py", # Already a shim
        "src/platform/core/enums.py", # Need manual check
    ]
    
    for path in paths:
        if any(path.endswith(s) for s in skip_files):
            continue
        update_file(path)

if __name__ == "__main__":
    main()
