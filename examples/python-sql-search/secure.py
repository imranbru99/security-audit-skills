# Safe counterpart to vulnerable.py. The SQL text does not include the request value.
"""User search with a bound parameter."""


def search_users(cursor, name: str):
    cursor.execute(
        "SELECT id, email FROM users WHERE name LIKE ?",
        (f"%{name}%",),
    )
    return cursor.fetchall()
