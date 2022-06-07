from flask import Flask, jsonify, request, make_response
import logging
import os

app = Flask(__name__)

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


@app.route("/bugtriage/api", methods=['GET', 'POST'])
def triage_bugs():
    # forward everything on to the right destination
    # Bugs must be correctly tagged with Priority High/Medium/Low, else they are only logged

    # First check whether priority is valid and otherwise append to the log file
    # Then check whether the bug is high priority, if so it must be sent to SLACK
    # All other valid bugs are sent to JIRA
    if request.method == 'GET':
        for bug in bugs:
            if bug['priority'] not in {"High", "Medium", "Low"}:
                app.logger.info(bug)

        return jsonify({'bugs': bugs})

    if request.method == 'POST':
        #Validating the API request
        if not request.json or not 'priority' in request.json or request.json['priority'] not in {"High", "Medium", "Low"}:
            app.logger.info(request.json)
            return 'Bad request! This event has been logged.', 400

        return request.json







