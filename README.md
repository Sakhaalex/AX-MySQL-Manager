A lightweight, tab-based desktop application to manage records in a MySQL database using Python, Tkinter, and pymysql. Designed to be beginner-friendly, generic, and extendable for personal or small-scale data management projects.

Overview

This project provides a clean GUI-based interface for managing records stored in a MySQL database. It emphasizes:

Easy data entry and editing via forms

Filtering and searching without destructive operations

CSV import/export for batch operations

Beginner-friendly and extendable code

While originally designed for a movie watchlist, the structure is generic and can be adapted for other datasets.

Features

Editor Tab – View and edit single records in detail

Filter Tab – Search and filter data by multiple fields

Insert Tab – Add new records and dynamically manage table fields

CSV → SQL Tab – Import CSV files into a MySQL table

SQL → CSV Tab – Export selected data to CSV with optional filters

Non-destructive operations – No records are deleted by default

Project Structure

editor_single.py – Lightweight editor for updating individual records

manager_master.py – Full tab-based application with all features

README.md – Project documentation

Database Requirements

The application works with MySQL databases. Minimal required setup:

Database Name: Any (update in code)

Table Name: Movies (or any table, as long as columns match)

Minimum Columns
Column	Type	Notes
movie_id	PRIMARY KEY	Unique identifier
name	TEXT	Movie or record name
year	INT	Optional
rating	FLOAT	Optional
language	TEXT	Optional
industry	TEXT	Optional

Optional columns such as actors or director are supported but not required. The app is designed to ignore missing optional columns gracefully.

Installation & Setup

Install Python 3.8+

Install dependencies:

pip install pymysql


Create a MySQL database and table, or use an existing one.

Update database credentials in the Python script (host, user, password, database).

Run the application:

python manager_master.py

Design Philosophy

Generic & Extendable – Designed to adapt to different datasets beyond movies

Manual Control – Focus on explicit data entry, field management, and editing

Editor-First Workflow – Prevents accidental data loss, emphasizes safe operations

Beginner-Friendly – Clean code and UI to understand and extend easily

Future Extensions

Add support for additional tables (songs, series, etc.)

Multi-database support

Advanced filtering with checkboxes and dynamic queries

Column sorting in the GUI

More robust CSV import/export with field mapping

License

Open for personal, educational, or non-commercial use.
