# Book-A-Meal UI Prototype

This folder contains a standalone, Figma-style prototype for the Book-A-Meal product.

## Purpose

Use this prototype to validate user flows and UI direction before full React and Flask implementation.

## Files

- index.html - Main prototype screens and structure
- styles.css - Full visual design system and responsive layout
- script.js - Screen switching and demo navigation behavior

## How To Preview

1. Open ui/index.html directly in your browser.
2. Or run a static server from the ui folder and open that URL.

## Prototype Screens

1. Auth screen:
Login form and quick demo access for Customer and Caterer roles.
2. Customer screen:
Daily menu view, special items, general menu, meal selection, and change-order action.
3. Caterer screen:
Meal option CRUD layout, daily menu builder, and recipe API category chips.
4. Revenue screen:
End-of-day stats, order statuses, refunds with penalty, and financial summary.

## Product Requirements Covered

- User account login flow (and sign-up placeholder path)
- Caterer meal management (add, edit, delete)
- Daily menu setup for a specific day
- Customer selection from specials and general menu
- Customer ability to change meal choice
- Notification concept when menu is published
- Caterer view of user orders
- End-of-day revenue and refund-with-penalty visualization

## Integration Notes

- Public meal API concept used: TheMealDB.
- The current prototype is static UI and does not call backend APIs yet.
- Clarification points (fulfilment ownership, notification channel, pricing rules) should be finalized before backend implementation.