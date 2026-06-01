#!/usr/bin/env python3
import sys
import sqlite3
import json

def main():
    args = sys.argv[1:]
    db_path = None
    query = None
    header = False
    column = False
    interactive = False

    # Simple parsing of command-line options
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '-batch':
            pass
        elif arg == '-header':
            header = True
        elif arg == '-column':
            column = True
        elif arg == '-cmd':
            i += 1  # Skip the command string (e.g. PRAGMA foreign_keys = ON;)
        elif arg.startswith('-'):
            pass # Ignore other flags
        elif db_path is None:
            db_path = arg
        else:
            query = arg
        i += 1

    if not db_path:
        print("Error: No database path specified", file=sys.stderr)
        sys.exit(1)

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        # If no query is provided, read from stdin
        if query is None:
            query = sys.stdin.read()

        # Split multiple statements if any (like in 001-init.sql)
        statements = query.split(';')
        for stmt in statements:
            stmt_stripped = stmt.strip()
            if not stmt_stripped:
                continue
            cursor.execute(stmt_stripped)
        
        conn.commit()

        # If there are rows to fetch, format them
        if cursor.description:
            colnames = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            if header:
                if column:
                    # Column formatting
                    widths = [len(c) for c in colnames]
                    for row in rows:
                        for idx, val in enumerate(row):
                            widths[idx] = max(widths[idx], len(str(val if val is not None else '')))
                    # Print headers
                    header_str = "  ".join(colnames[idx].ljust(widths[idx]) for idx in range(len(colnames)))
                    print(header_str)
                    print("-" * len(header_str))
                    # Print rows
                    for row in rows:
                        print("  ".join(str(val if val is not None else '').ljust(widths[idx]) for idx, val in enumerate(row)))
                else:
                    # Standard pipe/comma or raw output
                    print("|".join(colnames))
                    for row in rows:
                        print("|".join(str(val if val is not None else '') for val in row))
            else:
                for row in rows:
                    if len(row) == 1:
                        print(row[0] if row[0] is not None else '')
                    else:
                        print("|".join(str(val if val is not None else '') for val in row))

    except Exception as e:
        print(f"sqlite3_fallback error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
