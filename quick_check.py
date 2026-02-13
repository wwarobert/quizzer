import sys

sys.path.insert(0, "C:/Users/NIBRSK/Workspace/quizzer")
from web_quiz import HTML_TEMPLATE

print("Checking two-column layout elements...")
print("Sidebar class:", 'class="sidebar"' in HTML_TEMPLATE)
print("Dashboard view:", 'id="dashboardView"' in HTML_TEMPLATE)
print("Main content:", 'class="main-content"' in HTML_TEMPLATE)
print("Sidebar width 260px:", "width: 260px" in HTML_TEMPLATE)
print("Main margin 260px:", "margin-left: 260px" in HTML_TEMPLATE)
