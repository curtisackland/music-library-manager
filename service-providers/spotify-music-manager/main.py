from flask import Flask

app = Flask(__name__)

@app.route('/spotifymusicmanager')
def hello_world():
    return 'This is the spotify music manager'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

