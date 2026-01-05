AX Watchlist Manager
A simple desktop application to manage a personal movie watchlist using Python, Tkinter, and MySQL.

Overview
This project provides a clean GUI-based editor for managing movie records stored in a MySQL database.
It is designed to be generic, extendable, and beginner-friendly.

The project currently supports:
• Viewing all movie records
• Editing a single selected record
• Filtering records using multiple fields
• Non-destructive operations (no delete by default)

Project Files
editor_single.py
A lightweight editor focused only on updating one record at a time.
Best used when you want stability and minimal UI complexity.

manager_master.py
The main application with a tab-based interface.
Includes:
• Editor tab for updating records
• Filter tab for searching and sorting data

Database Requirements
Database name: Watchlist
Required table: Movies

Minimum columns:
• movie_id (PRIMARY KEY)
• name
• year
• rating
• language
• industry

Optional columns (used only if present):
• actors
• director

No errors occur if optional columns are missing.

How to Run

Create the MySQL database and Movies table

Update DB credentials in the Python file

Run the application:

python manager_master.py


Design Philosophy
• Single database, generic structure
• Manual control over data
• Editor-first workflow
• Filters instead of destructive searches
• Beginner-readable code

Future Extensions
• Songs / Series tables
• Checkbox-based filters
• Column sorting
• Import from CSV
• Multi-database support

License
Open for personal and educational use.# AX-MySQL-Manager
