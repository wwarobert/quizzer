# User Flow: Web Quiz (Certification Prep)

## Entry Point
- **Dashboard** with breadcrumb (“Dashboard”)
- **Available Quizzes** in sidebar, keyboard-activatable

## Flow Steps
1. **Choose Quiz**
   - Expand “Available Quizzes”
   - Select quiz (no transform, compact item)
2. **Practice Mode**
   - Timer visible, progress bar updates
   - Question centered; input with label and ARIA
   - Submit → instant feedback (no layout shift)
3. **Finish Quiz**
   - Confirm dialog (accessible, minimal styles)
   - Exit fullscreen (if on) and show results overlay
4. **Results & Review**
   - Score, pass/fail, light stat cards
   - Failure list: question, your answer, correct answer with subtle accent
   - Auto-generate HTML report
5. **Return to Dashboard**
   - Update recent runs, pass rate

## Design Principles
- **Minimal Friction**: One-click start, consistent spacing
- **No Layout Shifts**: Buttons keep borders; no hover transforms
- **Clear Feedback**: Concise, readable success/fail messages
- **Stable Navigation**: Breadcrumb with consistent spacing
- **Accessible by Default**: Roles, labels, focus-visible, keyboard support

## Accessibility Requirements
- **Keyboard Navigation**: Tab order predictable; Enter/Space activate items
- **Dialog Semantics**: `role="dialog"`, `aria-modal`, labelled by title
- **Labels**: Inputs have visible or visually-hidden labels
- **Announcements**: Timer `aria-live="polite"`; dynamic feedback readable
- **Visual Accessibility**: High-contrast text, focus outline, touch targets ≥24px

## Success Metrics
- **Start time**: < 15s from dashboard to question
- **Score clarity**: Users understand results at a glance
- **Review speed**: Fail list scannable in < 2 minutes
- **Consistency**: No hover-induced layout movement
