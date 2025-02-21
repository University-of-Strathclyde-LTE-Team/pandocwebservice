# Converter
This is a Python webservice that will take an uploaded file and use pandoc to convert it 
into a different format.

When a request is sent with a payload, an identifier is returned which can be used to check the progress of the
conversion.

This service uses:
* python3.12 - A high-level, interpreted programming language known for its readability and versatility.
* flask - Microframework for building web applications and APIs.
* celery - Celery is a Python library used for executing asynchronous and scheduled tasks in a distributed system. (https://docs.celeryq.dev/en/stable/)
* redis - Redis is an in-memory data structure store used as a database, cache, and message broker.

# Installation
## Run the following commands in the terminal
`sudo apt-get install redis-server`

`sudo service redis-server start`

`cd /home/igs03102/moodle/docconverter/converter`

`source venv/bin/activate`

`pip install -r requirements.txt`

# Usage
## Start the Flask application
`python app.py`

## In a new terminal, start the Celery worker
`cd /home/igs03102/moodle/docconverter/converter`
`source venv/bin/activate`
`celery -A app.celery worker --loglevel=info`