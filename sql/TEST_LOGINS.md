# TEST_LOGINS.md

These are the plaintext demo passwords used before bcrypt hashing.
Keep this file private to the team. The database itself stores only bcrypt hashes.

| user_id | email | password | role | permit |
| --- | --- | --- | --- | --- |
| admin001 | admin@parking.test | Admin123! | admin | None |
| fac001 | faculty@parking.test | Faculty123! | faculty | Faculty |
| cb001 | commuter.blue@parking.test | Blue123! | student | Commuter Blue |
| cr001 | commuter.red@parking.test | Red123! | student | Commuter Red |
| cw001 | campus.walk@parking.test | Walk123! | student | Campus Walk |
| re001 | res.east@parking.test | East123! | student | Residential East |
| rc001 | res.central@parking.test | Central123! | student | Residential Central |
| rnw001 | res.northwest@parking.test | Northwest123! | student | Residential Northwest |
| rs001 | res.south@parking.test | South123! | student | Residential South |
| vis001 | visitor@parking.test | Visitor123! | visitor | Visitor |

Suggested login demos:
- `admin001` or `admin@parking.test` for the admin flow
- `fac001` or `faculty@parking.test` for faculty lot access
- `cb001` / `cr001` / `cw001` / `re001` / `rc001` / `rnw001` / `rs001` for student permit map testing
- `vis001` or `visitor@parking.test` for visitor behavior
