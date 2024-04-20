# tv-backend-server

# B - How to run project

## 1. install poetry
```
    pip install poetry
```

## 2. install dependencies
```
    poetry install
```

## 3. run project
```
    poetry run gunicorn -c gunicorn_config.py
```
or if you set the virtual environment as your default python environment
```
    gunicorn -c gunicorn_config.py
```
