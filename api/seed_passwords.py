"""
seed_passwords.py
=================
One-time script to replace the fake `hashed_pw_xxx` placeholders in the
sample data with real bcrypt hashes. This lets you actually log in with
the sample users for testing and demos.

RUN IT ONCE:
    cd api
    source venv/bin/activate
    python seed_passwords.py

After this, you can log in to the web app with the credentials printed
at the end.

This only updates 4 test accounts (one per role). The other sample
users are left alone — the rule engine still works for them, but you
can't log in as them. If you need more test accounts, add them to the
TEST_ACCOUNTS list below.
"""

import bcrypt
import mysql.connector
from mysql.connector import Error


# Test accounts to seed with real bcrypt-hashed passwords.
# Each tuple is: (user_id, plain_password)
TEST_ACCOUNTS = [
    ("adm001", "admin123"),    # Karen Davis — admin
    ("stu001", "student123"),  # John Doe — student (RC permit)
    ("fac003", "faculty123"),  # James Williams — faculty (FC + ADA)
    ("vis001", "visitor123"),  # Sarah Miller — visitor
]


def main():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            port=3307,
            user="root",
            password="parking123",
            database="parking_db",
        )
    except Error as e:
        print(f"Could not connect to MySQL: {e}")
        print("Is the Docker container running? Try: docker start olemiss-parking")
        return

    cursor = conn.cursor(dictionary=True)
    print("Updating test account passwords...\n")

    for user_id, plain_pw in TEST_ACCOUNTS:
        # Look up the user to show who we're updating
        cursor.execute(
            "SELECT first_name, last_name, email, role FROM users WHERE user_id = %s",
            (user_id,),
        )
        user = cursor.fetchone()
        if user is None:
            print(f"  [skip] {user_id} — user not found in database")
            continue

        # Hash the password with bcrypt
        hashed = bcrypt.hashpw(plain_pw.encode(), bcrypt.gensalt()).decode()

        # Update the users table
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (hashed, user_id),
        )
        print(f"  [ok]   {user_id} → {user['first_name']} {user['last_name']} ({user['role']})")

    conn.commit()
    cursor.close()
    conn.close()

    print("\nDone. You can now log in with these accounts:\n")
    print(f"  {'EMAIL':<30} {'PASSWORD':<15} {'ROLE':<10}")
    print(f"  {'-' * 30} {'-' * 15} {'-' * 10}")
    # Hard-coded labels so you don't need to re-query the DB just to print them
    account_info = [
        ("kdavis@olemiss.edu",    "admin123",   "admin"),
        ("jdoe@go.olemiss.edu",   "student123", "student"),
        ("jwilliams@olemiss.edu", "faculty123", "faculty"),
        ("smiller@gmail.com",     "visitor123", "visitor"),
    ]
    for email, pw, role in account_info:
        print(f"  {email:<30} {pw:<15} {role:<10}")
    print()


if __name__ == "__main__":
    main()
