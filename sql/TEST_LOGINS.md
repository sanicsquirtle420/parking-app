# TEST_LOGINS.md

These are the plaintext demo passwords used before bcrypt hashing.
Keep this file private to the team. The database itself stores only bcrypt hashes.

| user_id | email | password | role | permit |
| --- | --- | --- | --- | --- |
| adm001 | admin@parking.test | Admin123! | admin | None |
| fac001 | faculty@parking.test | Faculty123! | faculty | Faculty |
| stu001 | commuter.blue@parking.test | Blue123! | student | Commuter Blue |
| stu002 | commuter.red@parking.test | Red123! | student | Commuter Red |
| stu003 | campus.walk@parking.test | Walk123! | student | Campus Walk |
| stu004 | res.east@parking.test | East123! | student | Residential East |
| stu005 | res.central@parking.test | Central123! | student | Residential Central |
| stu006 | res.northwest@parking.test | Northwest123! | student | Residential Northwest |
| stu007 | res.south@parking.test | South123! | student | Residential South |
| vis001 | visitor@parking.test | Visitor123! | visitor | Visitor |

Suggested login demos:
- `adm001` or `admin@parking.test` for the admin flow
- `fac001` or `faculty@parking.test` for faculty lot access
- `stu001` / `stu002` / `stu003` / `stu004` / `stu005` / `stu006` / `stu007` for student permit map testing
- `vis001` or `visitor@parking.test` for visitor behavior

New signup behavior:
- New non-admin accounts receive the `Free Day Pass` automatically for their first 24 hours.
- Long-term permit assignment is expected to happen later from the admin permit screen.
