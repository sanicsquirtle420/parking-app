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
pip install kivy kivy_garden dotenv sshtunnel mariadb paramiko
```

Ubuntu / Debian
```bash
sudo apt install libmariadb3 libmariadb-dev
```

> [!NOTE]
> The `.env` file should be in `/database` to work properly.