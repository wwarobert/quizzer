"""
Quick verification that Version 4.0 dashboard features are present
"""
import sys
sys.path.insert(0, 'C:/Users/NIBRSK/Workspace/quizzer')
from web_quiz import HTML_TEMPLATE

print('🔍 Verifying Version 4.0 - Narrower Sidebar + Comprehensive Dashboard')
print('=' * 75)

checks = [
    # Layout dimensions
    ('Sidebar width 200px', 'width: 200px'),
    ('Main content margin 200px', 'margin-left: 200px'),
    ('Toggle button position 210px', 'left: 210px'),
    
    # Dashboard sections
    ('Performance Trends section', 'id="performanceTrends"'),
    ('Quiz Breakdown section', 'id="quizBreakdown"'),
    ('Recent Activity section', 'id="recentRunsList"'),
    ('Pass/Fail Analysis section', 'id="passFailAnalysis"'),
    
    # Stat cards (6 total)
    ('Total Quizzes stat', 'id="totalQuizzes"'),
    ('Total Runs stat', 'id="totalRuns"'),
    ('Avg Score stat', 'id="avgScore"'),
    ('Pass Rate stat', 'id="passRate"'),
    ('Best Score stat', 'id="bestScore"'),
    ('Total Questions stat', 'id="totalQuestions"'),
    
    # Report styling
    ('Report section CSS', '.report-section {'),
    ('Report table CSS', '.report-table {'),
    ('Trend bar CSS', '.trend-bar {'),
    ('Timeline CSS', '.timeline {'),
    ('Analysis grid CSS', '.analysis-grid {'),
    ('Badge CSS', '.badge {'),
    
    # JavaScript functions
    ('displayPerformanceTrends function', 'function displayPerformanceTrends()'),
    ('displayQuizBreakdown function', 'function displayQuizBreakdown()'),
    ('displayPassFailAnalysis function', 'function displayPassFailAnalysis()'),
]

passed = 0
failed = 0

for name, check_str in checks:
    if check_str in HTML_TEMPLATE:
        print(f'✓ {name:<40} FOUND')
        passed += 1
    else:
        print(f'✗ {name:<40} MISSING')
        failed += 1

print('=' * 75)
print(f'\n📊 Results: {passed}/{len(checks)} checks passed')

if failed == 0:
    print('\n✅ SUCCESS! Version 4.0 is complete!')
    print('   ✓ Narrow sidebar (200px)')
    print('   ✓ 6 stat cards')
    print('   ✓ Performance Trends report')
    print('   ✓ Quiz Breakdown table')
    print('   ✓ Recent Activity timeline')
    print('   ✓ Pass/Fail Analysis')
    print('\n🌐 Open: http://127.0.0.1:5000')
    print('⚠️  Remember to hard refresh: Ctrl+Shift+R')
else:
    print(f'\n❌ {failed} checks failed!')

sys.exit(0 if failed == 0 else 1)
