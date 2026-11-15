# INTENTIONALLY VULNERABLE — teaching fixture for security-audit-skills.
# Do not deploy. Do not run against real data.
"""User search that builds SQL with an f-string."""


def search_users(cursor, name: str):
    statement = f"SELECT id, email FROM users WHERE name LIKE '%{name}%'"
    cursor.execute(statement)
    return cursor.fetchall()
