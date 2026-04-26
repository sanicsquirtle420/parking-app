# Parking App
Csci 387 Group 6 Project. 

## Members
* [Murodjon Abduganiev](https://github.com/a-muratuch)
* [Md Jannatul Ferdous](https://github.com/mferdous9900)
* [Joshua Jones-Reed](https://github.com/joshreed48)
* [Diego Ruiz](https://github.com/sanicsquirtle420)

## Documentation
This app uses Python version `3.11` and Kivy version `2.3.1`

### Initial Setup
> [!IMPORTANT]
> The following instructions are for [Ubuntu/WSL](https://learn.microsoft.com/en-us/windows/wsl/install):

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
cd [PATH_TO_PROJECT]
python3.11 -m venv venv311
source venv311/bin/activate
```

Dependencies:
```bash
pip install kivy kivy_garden dotenv sshtunnel mariadb paramiko bcrypt
```

Ubuntu / Debian
```bash
sudo apt install libmariadb3 libmariadb-dev
```

### Environment setup

Create a `.env` file in either the project root or `/database` with the database settings the app expects:

```bash
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=your_database_name

# Required because this branch follows the tunnel-first db.py setup
SSH_HOST=
SSH_PORT=22
SSH_USER=
SSH_PASSWORD=
```

This branch follows the Diego `db.py` flow and connects through the SSH tunnel. That means `SSH_HOST`, `SSH_USER`, and `SSH_PASSWORD` need real values, and `DB_HOST` / `DB_PORT` should point to the database from the SSH server's point of view.

### Database setup
Use the compatibility-first SQL files in `/sql` in this order:

1. `schema.sql`
2. `seed_reference.sql`
3. `seed_lots_and_rules.sql`
4. `views.sql`

`tables2.sql`, `tables_data.sql`, and `parkingData.sql` are older branch files and should not be the primary setup path for this branch.
