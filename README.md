# Concough Project

------------------
This project is the backend section of greater project that was a startup that got about **+50k** users.

### Prerequisites
- Python Version 2
- Django 1.9.11

All the required dependencies are listed in `requirements.txt` file at root directory. You must create a virtual environment and install them by `pip`.

### Config the project
All the configuration is located in `settings.py` at `digikunkor` app. configurations are seperated into two environments: `local` and `deploy`.
For local development, you must use `local` env. All the settings can be changed based on your environment and ...
<br><br>
For local development you just need `sqlite` for rational database, `memcache` for cache and, `mongod` for NoSql.

### Structure
This project include the following apps:
- **admin** app: the admin panel that includes data entry section, report section, configs section and, many others.
- **api** app: the APIs application that provides the required endpoint to client mobile app.
- **main** app: the main application that handles authentication, helpers, models definition and many others for other apps.
- Note: There's also `script` folder that includes necessary scripts to defining some initial permissions. 

### Run the program
To run the program, you can use the following:
- make change in `settings.py`:
  - `DEV_ENVIRONMENT="local"`
  - make change in this file based on your needs.
- run `makemigrations` command
- run `migrate` command
- run `createsuperuser` command
- run `shell` command and the copy/paste from the `scripts` folder and run them in this order:
  - `auth_create_groups`
  - `auth_create_permissions`
  - `generate_auth_systems` (change its data based on your needs)
- run `runserver` command
