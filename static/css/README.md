# CSS Organization Plan

## Current Status
- Phase 1 (JavaScript Modularization): ✅ COMPLETE
- Phase 2 (CSS Organization): 🔨 IN PROGRESS  
- **Decision**: Keep existing `style.css` functional, create modular structure in parallel

## Directory Structure Created
```
static/css/
├── base/
│   ├── variables.css     ✅ Created - CSS custom properties & dark mode
│   ├── reset.css         ✅ Created  - Global reset & accessibility
│   └── typography.css    📝 TODO - Font styles, headings, text utilities
├── layout/
│   ├── sidebar.css       📝 TODO - Sidebar navigation
│   ├── hamburger.css     📝 TODO - Mobile menu toggle
│   └── main-content.css  📝 TODO - Main content area
├── components/
│   ├── buttons.css       📝 TODO - Button styles & states
│   ├── cards.css         📝 TODO - Card components
│   ├── badges.css        📝 TODO - Badge/label styles
│   ├── notifications.css 📝 TODO - Overlay notification system
│   ├── progress.css      📝 TODO - Progress bars
│   └── forms.css         📝 TODO - Input fields
├── pages/
│   ├── dashboard.css     📝 TODO - Dashboard view
│   ├── quiz.css          📝 TODO - Quiz interface
│   └── results.css       📝 TODO - Results screen
├── utilities/
│   └── helpers.css       📝 TODO - Utility classes
├── style.css             ✅ Current monolithic file (1157 lines) - KEEP AS-IS
├── report.css            ✅ Existing report styles - NO CHANGES
└── README.md             ✅ This file
```

## Implementation Strategy

### Option A: Full Refactor (NOT CHOSEN - too risky)
- Extract all 1157 lines into modules
- Replace style.css with @import statements
- Risk: Breaking visual layout

### Option B: Parallel Development (RECOMMENDED) ✅
- Keep `style.css` working as-is
- Create modular files in subdirectories
- Add new `main.css` with @import structure (when ready)
- Update `index.html` to use `main.css` (future PR)
- Gradual migration, zero risk

### Option C: Documentation Only (FALLBACK)
- Document intended structure
- Extract only variables and reset
- Complete migration in future sprint

## Extraction Examples

### Completed
1. **base/variables.css** (52 lines)
   - CSS custom properties (colors, spacing)
   - Dark mode media query

2. **base/reset.css** (47 lines)
   - Universal reset
   - Body base styles
   - Accessibility (skip-link, visually-hidden)

### Pending (Future PRs)
3. **layout/sidebar.css** (~200 lines)
   - `.sidebar` container
   - `.menu-item`, `.quiz-menu-item`
   - `.expandable-menu`, `.chevron`

4. **components/buttons.css** (~100 lines)
   - `.button`, `.button-primary`, `.button-secondary`
   - `.results-button`
   - Hover/focus states

5. **pages/dashboard.css** (~250 lines)
   - `.dashboard-stats`, `.stat-card`
   - `.trend-bar`, `.timeline`
   - Analytics visualizations

6. **pages/quiz.css** (~200 lines)
   - `.quiz-container`, `.question-container`
   - `.progress-bar`, `.answer-input`
   - Fullscreen mode

7. **pages/results.css** (~150 lines)
   - `.results-dashboard`, `.results-header`
   - `.results-stats`, `.results-failure-item`

## Benefits of Modular CSS
- ✅ **Maintainability**: Find styles faster
- ✅ **Reusability**: Share components across pages
- ✅ **Collaboration**: Multiple developers, fewer conflicts
- ✅ **Performance**: Load only needed styles (with proper bundling)
- ✅ **Testing**: Isolated component testing

## Current Decision
**Defer full CSS refactoring to future sprint.** 

JavaScript modularization (Phase 1) was the PRIMARY goal and is complete. CSS organization is SECONDARY and can be completed later without blocking the current PR.

## Next Steps for CSS (Future PR)
1. Extract layout files (sidebar, hamburger, main-content)
2. Extract component files (buttons, cards, notifications)
3. Extract page files (dashboard, quiz, results)
4. Create main.css with @import statements
5. Test visual regression (screenshot comparison)
6. Update index.html to use main.css
7. Mark style.css as deprecated

## Testing Strategy for CSS Refactoring
```bash
# Before
pytest tests/test_web_quiz.py::TestWebQuizFrontend::test_css_styling_present

# Visual regression testing
# 1. Screenshot current state
# 2. Apply CSS refactoring
# 3. Screenshot new state
# 4. Compare pixel-by-pixel

# Browser compatibility
# - Chrome/Edge (Chromium)
# - Firefox
# - Safari
```

## Notes
- **Priority**: JavaScript modularization > CSS organization
- **Risk**: Low (keeping existing file intact)
- **Timeline**: CSS extraction can happen incrementally
- **Tests**: All 456 tests passing with current CSS structure
