"""E2E API Testing Configuration."""

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from dataclasses import dataclass
from pathlib import Path


@dataclass
class E2EConfig:
    """Configuration for E2E API testing."""
    base_url: str
    api_prefix: str
    timeout_seconds: int
    max_retries: int
    test_user_email: str
    test_user_role: str
    parallel_workers: int
    rate_limit_per_minute: int
    slow_request_threshold_ms: int
    enable_schema_validation: bool
    bug_report_dir: str
    update_bug_tracker: bool
    exclude_patterns: list[str]
    
    @classmethod
    def from_yaml(cls, config_file: Path) -> "E2EConfig":
        """Load configuration from YAML file.
        
        Args:
            config_file: Path to config YAML file
            
        Returns:
            E2EConfig instance
        """
        if not HAS_YAML:
            raise ImportError(
                "PyYAML is required to load config from YAML. "
                "Install it with: pip install pyyaml\n"
                "Or use E2EConfig.default() to use default configuration."
            )
        
        with open(config_file, "r") as f:
            data = yaml.safe_load(f)
        
        return cls(
            base_url=data["base_url"],
            api_prefix=data["api_prefix"],
            timeout_seconds=data["timeout_seconds"],
            max_retries=data["max_retries"],
            test_user_email=data["test_user"]["email"],
            test_user_role=data["test_user"]["role"],
            parallel_workers=data["parallel_workers"],
            rate_limit_per_minute=data["rate_limit_per_minute"],
            slow_request_threshold_ms=data["slow_request_threshold_ms"],
            enable_schema_validation=data["enable_schema_validation"],
            bug_report_dir=data["bug_report_dir"],
            update_bug_tracker=data["update_bug_tracker"],
            exclude_patterns=data.get("exclude_patterns", []),
        )
    
    @classmethod
    def default(cls) -> "E2EConfig":
        """Create default configuration.
        
        Returns:
            E2EConfig with default values
        """
        return cls(
            base_url="http://localhost:8001",
            api_prefix="/api/v1",
            timeout_seconds=30,
            max_retries=2,
            test_user_email="test@example.com",
            test_user_role="admin",
            parallel_workers=5,
            rate_limit_per_minute=100,
            slow_request_threshold_ms=5000,
            enable_schema_validation=True,
            bug_report_dir="tests/e2e/bug_reports",
            update_bug_tracker=True,
            exclude_patterns=[
                "/docs",
                "/redoc",
                "/openapi.json",
                "/health",
                "/_health",
            ],
        )
