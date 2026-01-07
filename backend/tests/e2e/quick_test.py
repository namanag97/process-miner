#!/usr/bin/env python3
"""
Quick Test - Run E2E API Tests on running backend server.

This is a simplified version for quick testing during development.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from e2e_api_tester import E2EAPITester, E2EConfig

if __name__ == "__main__":
    print("Quick E2E API Test")
    print("=" * 80)

    # Use default config
    config = E2EConfig.default()

    # Override with command line args if provided
    if len(sys.argv) > 1:
        config.base_url = sys.argv[1]

    print(f"Testing: {config.base_url}")
    print()

    tester = E2EAPITester(config)
    try:
        tester.run()

        # Exit with error code if bugs found
        summary = tester.bug_detector.get_summary()
        if summary["p0"] > 0:
            print("\n⚠️  P0 bugs found - requires immediate attention!")
            sys.exit(1)
        elif summary["total"] > 0:
            print(f"\n⚠️  {summary['total']} bugs found")
            sys.exit(0)
        else:
            print("\n✅ All tests passed!")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
