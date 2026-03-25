/**
 * Sidebar Management
 * Handles sidebar toggle, hamburger menu, and responsive behavior
 */

import { sidebarCollapsed, setSidebarCollapsed } from '../state/quiz-state.js';

/**
 * Toggle sidebar visibility
 */
export function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const hamburgerCheckbox = document.getElementById('hamburgerCheckbox');
    
    const newState = !sidebarCollapsed;
    setSidebarCollapsed(newState);
    
    if (newState) {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('expanded');
        hamburgerCheckbox.checked = false;
    } else {
        sidebar.classList.remove('collapsed');
        mainContent.classList.remove('expanded');
        hamburgerCheckbox.checked = true;
    }
}

/**
 * Handle hamburger checkbox change event
 */
export function handleHamburgerChange() {
    const checkbox = document.getElementById('hamburgerCheckbox');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    
    console.log('Hamburger changed! Checked:', checkbox.checked);
    
    if (checkbox.checked) {
        // Open sidebar
        console.log('Opening sidebar');
        sidebar.classList.remove('collapsed');
        mainContent.classList.remove('expanded');
        setSidebarCollapsed(false);
    } else {
        // Close sidebar
        console.log('Closing sidebar');
        sidebar.classList.add('collapsed');
        mainContent.classList.add('expanded');
        setSidebarCollapsed(true);
    }
}

/**
 * Initialize sidebar button on page load
 */
export function initSidebarButton() {
    const hamburgerCheckbox = document.getElementById('hamburgerCheckbox');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const isMobile = window.innerWidth <= 768;
    
    console.log('Initializing hamburger menu. Mobile:', isMobile);
    
    // Add event listener to hamburger checkbox
    hamburgerCheckbox.addEventListener('change', handleHamburgerChange);
    console.log('Event listener attached to hamburger checkbox');
    
    if (isMobile) {
        // On mobile, sidebar starts hidden
        setSidebarCollapsed(true);
        sidebar.classList.add('collapsed');
        mainContent.classList.add('expanded');
        hamburgerCheckbox.checked = false; // Shows 3 lines
        console.log('Mobile: Sidebar collapsed, checkbox unchecked');
    } else {
        // On desktop, sidebar starts visible
        setSidebarCollapsed(false);
        sidebar.classList.remove('collapsed');
        mainContent.classList.remove('expanded');
        hamburgerCheckbox.checked = true; // Shows X
        console.log('Desktop: Sidebar visible, checkbox checked');
    }
}

/**
 * Toggle quiz menu in sidebar
 */
export function toggleQuizMenu(loadQuizzesCallback) {
    const content = document.getElementById('quizMenuContent');
    const chevron = document.getElementById('quizChevron');
    const toggleBtn = document.getElementById('quizMenuToggle');
    
    if (content.classList.contains('expanded')) {
        content.classList.remove('expanded');
        chevron.classList.remove('rotated');
        if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
    } else {
        content.classList.add('expanded');
        chevron.classList.add('rotated');
        if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'true');
        // Load quizzes if callback provided
        if (loadQuizzesCallback) {
            loadQuizzesCallback();
        }
    }
}
