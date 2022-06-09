from azure.storage.queue import (
    QueueClient,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy
)

from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route("/bugtriage/api", methods=['GET', 'POST'])
def triage_bugs():
    # forward everything on to the right destination
    # Bugs must be correctly tagged with Priority High/Medium/Low, else they are only logged

    # First check whether priority is valid and otherwise append to the log file
    # Then check whether the bug is high priority, if so it must be sent to SLACK
    # All other valid bugs are sent to JIRA
    if request.method == 'GET':

        return "<h1>Welcome to the Bug Triaging API</h1>\
                <h3>Please ensure your JSON post request conforms to the following schema:</h3>\
                <h4>{title: yourtitle, description: yourdescription, priority: High/Medium/Low}</h4>\
                <h4>High priority bugs will be sent to SLACK, lower priority bugs will be backlogged on TRELLO\
                and invalid requests will be rejected and emailed.</h4>"

    if request.method == 'POST':
        # Validating the API request
        if not request.json or not 'priority' in request.json or request.json['priority'] not in {"High", "Medium", "Low"}:
            app.logger.info(request.json)
            return 'Bad request! This event has been logged.', 400

        if request.json['priority'] == "High":
            # Retrieve the connection string from an environment
            # variable named AZURE_STORAGE_CONNECTION_STRING
            connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

            # Create a unique name for the queue
            q_name = "priorityqueue"

            # Instantiate a QueueClient object which will
            # be used to create and manipulate the queue
            queue_client = QueueClient.from_connection_string(
                connect_str, q_name)

            # Send the bug
            queue_client.send_message(request.json)

        else:
            connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            q_name = "lowerpriorityqueue"

            queue_client = QueueClient.from_connection_string(
                connect_str, q_name)

            queue_client.send_message(request.json)

        return request.json




'''
# Creating an in-memory data structure for demonstration purposes
bugs = [
    {
        'id': 1,
        'title': 'Session state not persisting',
        'description': 'Users are not being persisted properly between pages',
        'priority': 'High'
    },
    {
        'id': 2,
        'title': 'Invalid usernames',
        'description': 'Usernames with special characters are not accepted',
        'priority': 'Medium'
    },
    {
        'id': 3,
        'title': 'Validation E-mail',
        'description': 'Email to validate test account was never receieved',
        'priority': '123'
    },
]

# Implementing logging to a file


@app.before_first_request
def before_first_request():
    log_level = logging.INFO

    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)

    root = os.path.dirname(os.path.abspath(__file__))
    logdir = os.path.join(root, 'logs')
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    log_file = os.path.join(logdir, 'app.log')
    handler = logging.FileHandler(log_file)
    handler.setLevel(log_level)
    app.logger.addHandler(handler)

    app.logger.setLevel(log_level)

    defaultFormatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    handler.setFormatter(defaultFormatter)

'''