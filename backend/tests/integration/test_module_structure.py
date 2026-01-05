"""Integration tests for the refactored module structure.

Tests that verify:
1. All modules can be imported without circular dependencies
2. All routers are properly registered
3. All services are accessible
4. Backward compatibility is maintained
"""

import pytest


class TestModuleImports:
    """Test that all modules can be imported without errors."""

    def test_import_all_domain_modules(self):
        """Test importing all domain modules."""
        from src.features.process_mining import (
            analyses,
            analytics,
            business_use_cases,
            conformance,
            discovery,
            filtering,
            ocpm,
            organizational,
            predictions,
            simulation,
            visualization,
            workflows,
        )

        assert analyses is not None
        assert analytics is not None
        assert business_use_cases is not None
        assert conformance is not None
        assert discovery is not None
        assert filtering is not None
        assert ocpm is not None
        assert organizational is not None
        assert predictions is not None
        assert simulation is not None
        assert visualization is not None
        assert workflows is not None

    def test_import_all_routers(self):
        """Test importing all routers from API layer."""
        from src.features.process_mining.api import (
            analyses_router,
            analytics_router,
            business_use_cases_router,
            conformance_router,
            datasets_router,
            discovery_router,
            filtering_router,
            ocpm_router,
            organizational_router,
            predictions_router,
            simulation_router,
            visualization_router,
            workflows_router,
        )

        # Verify all routers are APIRouter instances
        from fastapi import APIRouter

        assert isinstance(analyses_router, APIRouter)
        assert isinstance(analytics_router, APIRouter)
        assert isinstance(business_use_cases_router, APIRouter)
        assert isinstance(conformance_router, APIRouter)
        assert isinstance(datasets_router, APIRouter)
        assert isinstance(discovery_router, APIRouter)
        assert isinstance(filtering_router, APIRouter)
        assert isinstance(ocpm_router, APIRouter)
        assert isinstance(organizational_router, APIRouter)
        assert isinstance(predictions_router, APIRouter)
        assert isinstance(simulation_router, APIRouter)
        assert isinstance(visualization_router, APIRouter)
        assert isinstance(workflows_router, APIRouter)

    def test_import_all_services(self):
        """Test importing all services from domain modules."""
        from src.features.process_mining.analytics import analytics_service
        from src.features.process_mining.business_use_cases import business_use_cases
        from src.features.process_mining.conformance import conformance_service
        from src.features.process_mining.discovery import mining_service
        from src.features.process_mining.filtering import filtering_service
        from src.features.process_mining.ocpm import ocpm_service
        from src.features.process_mining.organizational import organizational_service
        from src.features.process_mining.predictions import prediction_service
        from src.features.process_mining.simulation import simulation_service
        from src.features.process_mining.visualization import visualization_service
        from src.features.process_mining.workflows import workflow_service

        assert analytics_service is not None
        assert business_use_cases is not None
        assert conformance_service is not None
        assert mining_service is not None
        assert filtering_service is not None
        assert ocpm_service is not None
        assert organizational_service is not None
        assert prediction_service is not None
        assert simulation_service is not None
        assert visualization_service is not None
        assert workflow_service is not None

    def test_backward_compatibility_services(self):
        """Test that old service imports still work (backward compatibility)."""
        # Old imports should still work via shims
        from src.features.process_mining.services.analytics import analytics_service
        from src.features.process_mining.services.conformance import conformance_service
        from src.features.process_mining.services.filtering import filtering_service
        from src.features.process_mining.services.mining import mining_service
        from src.features.process_mining.services.ocpm import ocpm_service
        from src.features.process_mining.services.organizational import (
            organizational_service,
        )
        from src.features.process_mining.services.prediction import prediction_service
        from src.features.process_mining.services.simulation import simulation_service
        from src.features.process_mining.services.workflow import workflow_service

        # Verify they're not None
        assert analytics_service is not None
        assert conformance_service is not None
        assert filtering_service is not None
        assert mining_service is not None
        assert ocpm_service is not None
        assert organizational_service is not None
        assert prediction_service is not None
        assert simulation_service is not None
        assert workflow_service is not None


class TestRouterRegistration:
    """Test that all routers are properly registered."""

    def test_all_routers_have_routes(self):
        """Verify all routers have routes defined."""
        from src.features.process_mining.api import (
            analyses_router,
            analytics_router,
            business_use_cases_router,
            conformance_router,
            datasets_router,
            discovery_router,
            filtering_router,
            ocpm_router,
            organizational_router,
            predictions_router,
            simulation_router,
            visualization_router,
            workflows_router,
        )

        # Minimum expected routes per router
        assert len(analyses_router.routes) >= 1
        assert len(analytics_router.routes) >= 1
        assert len(business_use_cases_router.routes) >= 1
        assert len(conformance_router.routes) >= 1
        assert len(datasets_router.routes) >= 1
        assert len(discovery_router.routes) >= 1
        assert len(filtering_router.routes) >= 1
        assert len(ocpm_router.routes) >= 1
        assert len(organizational_router.routes) >= 1
        assert len(predictions_router.routes) >= 1
        assert len(simulation_router.routes) >= 1
        assert len(visualization_router.routes) >= 1
        assert len(workflows_router.routes) >= 1

    def test_routers_have_correct_prefixes(self):
        """Verify routers have correct path prefixes."""
        from src.features.process_mining.api import (
            analyses_router,
            analytics_router,
            business_use_cases_router,
            conformance_router,
            discovery_router,
            filtering_router,
            ocpm_router,
            organizational_router,
            predictions_router,
            simulation_router,
            visualization_router,
            workflows_router,
        )

        # Check prefixes (must match actual router definitions)
        assert "/analyses" in str(analyses_router.prefix)
        assert "/analytics" in str(analytics_router.prefix)
        assert "business" in str(business_use_cases_router.prefix).lower()
        assert "/conformance" in str(conformance_router.prefix)
        assert "/discovery" in str(discovery_router.prefix)
        assert "/filtering" in str(filtering_router.prefix)
        assert "/ocpm" in str(ocpm_router.prefix)
        assert "organizational" in str(organizational_router.prefix)
        assert "/predictions" in str(predictions_router.prefix)
        assert "simul" in str(simulation_router.prefix).lower()
        assert "visual" in str(visualization_router.prefix).lower()
        assert "workflow" in str(workflows_router.prefix).lower()


class TestServiceLayerSeparation:
    """Test that service layer is properly separated from routers."""

    def test_services_exist_in_modules(self):
        """Test that each module has its own service file."""
        import os

        modules_with_services = [
            "analytics",
            "conformance",
            "discovery",
            "filtering",
            "organizational",
            "ocpm",
            "predictions",
            "simulation",
            "workflows",
            "visualization",
        ]

        base_path = "/Users/namanagarwal/system/backend/src/features/process_mining"
        for module in modules_with_services:
            service_path = os.path.join(base_path, module, "service.py")
            assert os.path.exists(service_path), f"{module}/service.py should exist"

    def test_routers_exist_in_modules(self):
        """Test that each module has its own router file."""
        import os

        modules_with_routers = [
            "analyses",
            "analytics",
            "business_use_cases",
            "conformance",
            "discovery",
            "filtering",
            "organizational",
            "ocpm",
            "predictions",
            "simulation",
            "workflows",
            "visualization",
        ]

        base_path = "/Users/namanagarwal/system/backend/src/features/process_mining"
        for module in modules_with_routers:
            router_path = os.path.join(base_path, module, "router.py")
            assert os.path.exists(router_path), f"{module}/router.py should exist"


class TestNoCircularDependencies:
    """Test that there are no circular import dependencies."""

    def test_can_import_all_modules_independently(self):
        """Test each module can be imported independently."""
        # If any of these raise ImportError due to circular dependency, test fails
        import src.features.process_mining.analyses
        import src.features.process_mining.analytics
        import src.features.process_mining.business_use_cases
        import src.features.process_mining.conformance
        import src.features.process_mining.discovery
        import src.features.process_mining.filtering
        import src.features.process_mining.ocpm
        import src.features.process_mining.organizational
        import src.features.process_mining.predictions
        import src.features.process_mining.simulation
        import src.features.process_mining.visualization
        import src.features.process_mining.workflows

        # All imports succeeded
        assert True
