# User Flow: Web Quiz (Students & Certification)

## Entry Points
- **Dashboard** with breadcrumb (“Dashboard”) and clear view titles
- **Available Quizzes** in sidebar, keyboard-activatable, `aria-expanded` managed
- Optional **Practice vs Exam Mode** selection (future enhancement)

## Flow Steps
1. **Choose Quiz**
   - Expand “Available Quizzes” (chevron rotates; `aria-expanded` toggles)
   - Select quiz (compact item, no hover transforms; mobile-friendly)
2. **Practice Mode**
   - Timer visible, progress bar updates
   - Question area with proper heading level (`h2`), labeled input
   - Submit → instant feedback (no layout shift); optional hint button (future)
3. **Finish Quiz**
   - Accessible confirm dialog (focus trap, Esc-close)
   - Exit fullscreen (if active) and show results
4. **Results & Review**
   - Score, pass/fail, light stat cards
   - Failures: question, your answer, correct answer; optional explanations (future)
   - HTML report saved via API
5. **Retake or Back to Dashboard**
   - Retake same quiz (results screen hides before restart)
   - Dashboard updates trends, pass rate, history

## Design Principles
- **Minimal Friction**: One-click start, consistent spacing
- **No Layout Shifts**: Stable components; avoid transform-based hover effects
- **Clear Feedback**: Concise copy; status region with `aria-live="polite"`
- **Stable Navigation**: Breadcrumb, active states with `aria-current`
- **Accessible by Default**: Roles, labels, focus-visible, keyboard support
- **Mobile-Friendly**: Responsive layout; touch targets ≥24px; skip link visible on focus
- **Reduced Motion**: Respect `prefers-reduced-motion` to disable animations

## Accessibility Requirements
- **Keyboard Navigation**: Predictable tab order; Enter/Space activate items
- **Dialog Semantics**: `role="dialog"`, `aria-modal`, labelled by title; focus trap; Esc-close
- **Labels**: Inputs have visible or visually-hidden labels
- **Announcements**: Timer and feedback `aria-live="polite"`; view title focus on change
- **Visual Accessibility**: High-contrast text, visible focus outline, touch targets ≥24px

## Success Metrics
- **Start time**: < 15s from dashboard to question
- **Score clarity**: Users understand results at a glance
- **Review speed**: Fail list scannable in < 2 minutes
- **Consistency**: No hover-induced layout movement
- **Mobile usability**: Students can complete quizzes on small screens comfortably
