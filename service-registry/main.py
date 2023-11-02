from flask import Flask

app = Flask(__name__)

@app.route('/serviceregistry')
def hello_world():
    return 'This is the service-registry'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

