# HTML Reports

This directory contains HTML quiz reports generated automatically after each quiz completion.

## Report Format

Each report contains:
- **Quiz metadata**: Quiz ID, completion date, source file
- **Summary statistics**: Total questions, correct answers, failures, percentage score
- **Pass/Fail status**: Visual banner indicating result (80% threshold)
- **Failed questions breakdown**: Detailed list showing:
  - Question number and text
  - Your incorrect answer
  - The correct answer

## File Naming

Reports are named: `{quiz_id}_report.html`

**Example**: `quiz_20260206_103000_report.html`

## Overwrite Behavior

Each quiz run overwrites the previous report for that quiz ID. This ensures you always have the latest result without accumulating old reports.

## Viewing Reports

Open any HTML file in your web browser:
- Double-click the file in Explorer
- Right-click → Open with → Browser
- Use `start data/reports/quiz_xxx_report.html` from command line

## Report Features

- **Responsive design**: Works on mobile and desktop
- **Print-friendly**: Formatted for paper output
- **Color-coded status**: Green for pass, red for fail
- **Detailed failure breakdown**: See exactly what you got wrong
- **Professional styling**: Modern gradient backgrounds and cards
