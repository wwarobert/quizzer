"""
Quick test to verify the two-column layout is present in the HTML template
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_two_column_layout():
    """Verify the HTML contains the two-column sidebar + dashboard layout"""

    # Load HTML template from file
    template_path = Path(__file__).parent.parent / "templates" / "index.html"
    html_content = template_path.read_text(encoding="utf-8")

    print("🔍 Checking HTML template for two-column layout...")
    print("=" * 70)

    # Check for sidebar structure
    checks = [
        ("Sidebar element", '<div class="sidebar"'),
        ("Sidebar ID", 'id="sidebar"'),
        ("Main content area", '<div class="main-content"'),
        ("Main content ID", 'id="mainContent"'),
        ("Dashboard view", 'id="dashboardView"'),
        ("Menu section", '<div class="menu-section">'),
        ("Hamburger menu container", '<div class="hamburger-container"'),
        ("Expandable menu", '<div class="expandable-menu">'),
        ("Quiz menu content", 'id="quizMenuContent"'),
        # Check for dashboard components
        ("Breadcrumb navigation", '<nav class="breadcrumb">'),
        ("Dashboard stats", '<div class="dashboard-stats">'),
        ("Stat cards", '<div class="stat-card">'),
        ("Total quizzes stat", 'id="totalQuizzes"'),
        ("Total runs stat", 'id="totalRuns"'),
        ("Average score stat", 'id="avgScore"'),
        ("Pass rate stat", 'id="passRate"'),
        ("Recent activity timeline", '<div class="timeline">'),
        ("Recent runs list", 'id="recentRunsList"'),
        # Check for CSS file link (CSS moved to external file)
        ("External CSS file", "css/style.css"),
        # Check for JavaScript functions
        ("Toggle sidebar function", "function toggleSidebar()"),
        ("Toggle quiz menu function", "function toggleQuizMenu()"),
        ("Show view function", "function showView(viewName)"),
        ("Update dashboard function", "function updateDashboard()"),
    ]

    passed = 0
    failed = 0

    for check_name, check_string in checks:
        if check_string in html_content:
            print(f"✓ {check_name:<30} FOUND")
            passed += 1
        else:
            print(f"✗ {check_name:<30} MISSING")
            failed += 1

    print("=" * 70)
    print(f"\nResults: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n✅ SUCCESS! Two-column layout IS present in the HTML template!")
        print("   - Left column: Sidebar (300px, navy gradient)")
        print("   - Right column: Dashboard (main content area)")
        print("\nIf you still see the old layout in your browser:")
        print("   1. Press Ctrl+Shift+R to hard refresh")
        print("   2. Or open OPEN_QUIZZER_HERE.html in your workspace")
    else:
        print("\n❌ FAILED! Some two-column layout elements are missing!")

    # Use assert instead of return for pytest
    assert failed == 0, f"{failed} layout elements are missing from the HTML template"


if __name__ == "__main__":
    try:
        test_two_column_layout()
        print("\n✅ Test passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
