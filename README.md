## Search and collection of vacancies for a programmer
This project collects data on vacancies on HeadHunter and SuperJob, placing them in a table.

### Download and installation
You need to download this project to run it.

After downloading, you need to unzip the project and open it in any development environment.

You need to create an additional `.env` file to specify a Secret Key with which you can connect to the API.

Get Secret key: [clickable](https://api.superjob.ru/info/).

Example:
```env
SECRET_KEY_SUPERJOB=YOUR_SJ_KEY
```

### Launch
To start, you need to open a terminal and write the following:
```
python3 main.py
```
The project will be launched after this command.

You will have to wait some time until the vacancies collection process is completed.