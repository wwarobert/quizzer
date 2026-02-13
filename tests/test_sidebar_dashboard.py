"""
Comprehensive tests for sidebar and dashboard UI elements.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import sys
from pathlib import Path

import pytest

# Import the Flask app
sys.path.insert(0, str(Path(__file__).parent.parent))
import web_quiz


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    web_quiz.app.config["TESTING"] = True
    with web_quiz.app.test_client() as client:
        yield client


class TestSidebarPresence:
    """Test that sidebar navigation is present in HTML."""

    def test_version_comment_present(self, client):
        """Test that version 6.0 comment is in HTML."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        # Check that version is 21.0 or higher
        assert (
            "UI Version: 21" in html or "UI Version: 2" in html
        ), "Version 21.0+ comment not found"
        assert (
            "FULLSCREEN MODE" in html or "PALETTE" in html
        ), "Version identifier text not found in comment"

    def test_sidebar_element_exists(self, client):
        """Test that sidebar div exists with correct class."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert 'class="sidebar"' in html, "Sidebar CSS class not found"
        assert 'id="sidebar"' in html, "Sidebar ID not found"

    def test_sidebar_structure_exists(self, client):
        """Test that sidebar structure exists with menu items."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert 'class="sidebar"' in html, "Sidebar CSS class not found"
        assert 'id="sidebar"' in html, "Sidebar ID not found"
        assert "menu-section" in html, "Menu section not found"
        assert "Dashboard" in html, "Dashboard menu item not found"

    def test_toggle_button_exists(self, client):
        """Test that hamburger menu toggle exists."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "hamburger-container" in html, "Hamburger container class not found"
        assert 'id="hamburgerCheckbox"' in html, "Hamburger checkbox ID not found"
        assert "hamburger-lines" in html, "Hamburger lines class not found"

    def test_menu_items_present(self, client):
        """Test that menu items structure exists."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "menu-item" in html, "Menu item class not found"
        assert "Dashboard" in html, "Dashboard menu item not found"

    def test_expandable_quiz_menu(self, client):
        """Test that expandable quiz menu exists."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "expandable-menu" in html, "Expandable menu not found"
        assert "Available Quizzes" in html, "Available Quizzes text not found"
        assert "toggleQuizMenu" in html, "Toggle quiz menu function not found"

    def test_sidebar_css_styles(self, client):
        """Test that sidebar CSS styles are defined."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert ".sidebar {" in html, "Sidebar CSS definition not found"
        assert ".menu-item {" in html, "Menu item CSS not found"
        assert ".expandable-menu" in html, "Expandable menu CSS not found"


class TestDashboardPresence:
    """Test that dashboard view is present in HTML."""

    def test_dashboard_view_exists(self, client):
        """Test that dashboard view div exists."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert 'id="dashboardView"' in html, "Dashboard view ID not found"

    def test_dashboard_header_exists(self, client):
        """Test that dashboard header exists."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "dashboard-header" in html, "Dashboard header class not found"
        assert "Dashboard" in html, "Dashboard title not found"

    def test_dashboard_stats_cards(self, client):
        """Test that dashboard statistics cards exist."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "dashboard-stats" in html, "Dashboard stats container not found"
        assert "stat-card" in html, "Stat card class not found"
        assert "stat-value" in html, "Stat value class not found"
        assert "stat-label" in html, "Stat label class not found"

    def test_dashboard_stats_ids(self, client):
        """Test that dashboard stat element IDs exist."""
        response = client.get("/")
        html = response.data.decode("utf-8")

        required_ids = [
            'id="totalQuizzes"',
            'id="totalRuns"',
            'id="avgScore"',
            'id="passRate"',
        ]

        for stat_id in required_ids:
            assert stat_id in html, f"Dashboard stat {stat_id} not found"

    def test_recent_runs_section(self, client):
        """Test that recent activity section exists."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "timeline" in html, "Timeline class not found"
        assert "Recent Activity" in html, "Recent Activity title not found"
        assert 'id="recentRunsList"' in html, "Recent runs list ID not found"

    def test_dashboard_css_styles(self, client):
        """Test that dashboard CSS styles are defined."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert ".dashboard-header" in html, "Dashboard header CSS not found"
        assert ".dashboard-stats" in html, "Dashboard stats CSS not found"
        assert ".stat-card" in html, "Stat card CSS not found"


class TestLayoutStructure:
    """Test the overall layout structure."""

    def test_main_content_area(self, client):
        """Test that main content area exists."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "main-content" in html, "Main content class not found"
        assert 'id="mainContent"' in html, "Main content ID not found"

    def test_sidebar_visible_by_default(self, client):
        """Test that sidebar is not collapsed by default."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        # Sidebar should NOT have collapsed class in initial HTML
        sidebar_section = html[
            html.find('class="sidebar"') : html.find('class="sidebar"') + 200
        ]
        assert (
            "collapsed" not in sidebar_section
        ), "Sidebar should not be collapsed by default"

    def test_layout_javascript_functions(self, client):
        """Test that layout JavaScript functions exist."""
        response = client.get("/")
        html = response.data.decode("utf-8")

        required_functions = [
            "function toggleSidebar()",
            "function toggleQuizMenu()",
            "function showView(",
            "function updateDashboard()",
        ]

        for func in required_functions:
            assert func in html, f"Function {func} not found in JavaScript"

    def test_no_old_card_layout(self, client):
        """Test that old centered card layout is not present."""
        response = client.get("/")
        html = response.data.decode("utf-8")

        # Should NOT have the old selection screen structure
        assert (
            'id="selectionScreen"' not in html
        ), "Old selectionScreen should be removed"

    def test_quiz_view_mode_exists(self, client):
        """Test that quiz view divs exist in main content."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert 'id="quizView"' in html, "Quiz view div not found"
        assert 'id="resultsScreen"' in html, "Results screen div not found"
        assert "fullscreen-toggle" in html, "Fullscreen toggle button not found"


class TestJavaScriptVariables:
    """Test JavaScript variables for sidebar and dashboard."""

    def test_sidebar_variables(self, client):
        """Test that sidebar-related variables exist."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "let sidebarCollapsed" in html, "sidebarCollapsed variable not found"

    def test_quiz_runs_storage(self, client):
        """Test that quiz runs localStorage is set up."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "let quizRuns" in html, "quizRuns variable not found"
        assert "localStorage.getItem" in html, "localStorage usage not found"


class TestResponsiveLayout:
    """Test responsive layout elements."""

    def test_media_queries_exist(self, client):
        """Test that responsive media queries are present."""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "@media" in html, "Media queries not found"
        assert (
            "max-width: 768px" in html or "max-width:768px" in html
        ), "Mobile breakpoint not found"


def test_print_html_structure(client):
    """Debug test: Print HTML structure to verify content."""
    response = client.get("/")
    html = response.data.decode("utf-8")

    print("\n" + "=" * 60)
    print("HTML STRUCTURE VERIFICATION")
    print("=" * 60)

    print(f"\nTotal HTML length: {len(html)} characters")

    # Check body section
    body_start = html.find("<body>")
    if body_start >= 0:
        body_section = html[body_start : body_start + 1000]
        print("\n--- First 1000 chars after <body> ---")
        print(body_section)

    # Check for critical elements
    print("\n--- Critical Elements Check ---")
    critical = {
        "Sidebar div": 'class="sidebar"',
        "Dashboard div": 'id="dashboardView"',
        "Toggle button": 'id="toggleSidebar"',
        "Main content": 'id="mainContent"',
        "Dashboard header": "dashboard-header",
        "Stat cards": "stat-card",
    }

    for name, search_term in critical.items():
        found = search_term in html
        status = "✓" if found else "✗"
        print(f"{status} {name}: {search_term}")

    print("=" * 60)
