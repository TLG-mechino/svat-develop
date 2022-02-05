Init project
- Ubuntu/debian: sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

### How to install
- Copy .env.example => .env
- Fill DB info => .env (Mysql)
- npm install (install node (windows) if npm has not installed yet)
- python install -r requirements.txt
- Run server for develop:
    `python svat/manage.py runserver`

- Seeder:
  `python svat/manage.py loaddata data`
 
- Version: Demo V0.1