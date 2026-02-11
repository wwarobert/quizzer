"""
Quick test to verify the two-column layout is present in the HTML template
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web_quiz import HTML_TEMPLATE


def test_two_column_layout():
    """Verify the HTML contains the two-column sidebar + dashboard layout"""
    
    print("🔍 Checking HTML template for two-column layout...")
    print("=" * 70)
    
    # Check for sidebar structure
    checks = [
        ("Sidebar element", '<div class="sidebar"'),
        ("Sidebar ID", 'id="sidebar"'),
        ("Main content area", '<div class="main-content"'),
        ("Main content ID", 'id="mainContent"'),
        ("Dashboard view", 'id="dashboardView"'),
        ("Sidebar header", '<div class="sidebar-header">'),
        ("Toggle sidebar button", '<button class="toggle-sidebar"'),
        ("Expandable menu", '<div class="expandable-menu">'),
        ("Quiz menu content", 'id="quizMenuContent"'),
        
        # Check for dashboard components
        ("Dashboard header", '<div class="dashboard-header">'),
        ("Dashboard stats", '<div class="dashboard-stats">'),
        ("Stat cards", '<div class="stat-card">'),
        ("Total quizzes stat", 'id="totalQuizzes"'),
        ("Total runs stat", 'id="totalRuns"'),
        ("Average score stat", 'id="avgScore"'),
        ("Pass rate stat", 'id="passRate"'),
        ("Recent runs section", '<div class="recent-runs">'),
        ("Recent runs list", 'id="recentRunsList"'),
        
        # Check for CSS layout
        ("Sidebar CSS position", 'position: fixed;'),
        ("Sidebar width", 'width: 260px;'),
        ("Main content margin", 'margin-left: 260px;'),
        ("Two-column grid", 'grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));'),
        
        # Check for JavaScript functions
        ("Toggle sidebar function", 'function toggleSidebar()'),
        ("Toggle quiz menu function", 'function toggleQuizMenu()'),
        ("Show view function", 'function showView(viewName)'),
        ("Update dashboard function", 'function updateDashboard()'),
    ]
    
    passed = 0
    failed = 0
    
    for check_name, check_string in checks:
        if check_string in HTML_TEMPLATE:
            print(f"✓ {check_name:<30} FOUND")
            passed += 1
        else:
            print(f"✗ {check_name:<30} MISSING")
            failed += 1
    
    print("=" * 70)
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✅ SUCCESS! Two-column layout IS present in the HTML template!")
        print("   - Left column: Sidebar (260px, purple gradient)")
        print("   - Right column: Dashboard (main content area)")
        print("\nIf you still see the old layout in your browser:")
        print("   1. Press Ctrl+Shift+R to hard refresh")
        print("   2. Or open OPEN_QUIZZER_HERE.html in your workspace")
        return True
    else:
        print("\n❌ FAILED! Some two-column layout elements are missing!")
        return False


if __name__ == '__main__':
    success = test_two_column_layout()
    sys.exit(0 if success else 1)
