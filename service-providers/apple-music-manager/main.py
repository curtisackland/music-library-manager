from flask import Flask

app = Flask(__name__)

@app.route('/applemusicmanager')
def hello_world():
    return 'This is the apple music manager'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002)

