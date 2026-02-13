#!/usr/bin/env python3
"""Quick test to check if HTML contains sidebar and dashboard"""

import requests

response = requests.get("http://127.0.0.1:5000")
html = response.text

print("HTML length:", len(html))
print("\n=== Checking for sidebar ===")
if "sidebar" in html.lower():
    print("✓ 'sidebar' found in HTML")
    # Find and print the sidebar section
    idx = html.lower().find("sidebar")
    print(f"Context: ...{html[max(0,idx-50):idx+100]}...")
else:
    print("✗ 'sidebar' NOT found in HTML")

print("\n=== Checking for dashboard ===")
if "dashboard" in html.lower():
    print("✓ 'dashboard' found in HTML")
    idx = html.lower().find("dashboard")
    print(f"Context: ...{html[max(0,idx-50):idx+100]}...")
else:
    print("✗ 'dashboard' NOT found in HTML")

print("\n=== Checking for key elements ===")
checks = [
    'id="sidebar"',
    'id="dashboardView"',
    'class="sidebar"',
    "toggleSidebar",
    "menu-item",
]

for check in checks:
    if check in html:
        print(f"✓ Found: {check}")
    else:
        print(f"✗ Missing: {check}")

print("\n=== First 500 chars of body ===")
body_idx = html.find("<body>")
if body_idx > 0:
    print(html[body_idx : body_idx + 500])
