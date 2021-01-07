import logging

from flask import Flask,request
import json
import urllib.parse as parse
import urllib.request as req

# 봇 토큰, 봇 API 주소
TOKEN = '323404291:AAHAcS6OircOxeV83IVxBxdo4f2EGzlqcOM'
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

app = Flask(__name__)

# 메시지 발송
def sendMessage(chat_id, text):
    params = {
        'chat_id': str(chat_id),
        'text': text.encode('utf-8'),
        }
    res = req.urlopen(BASE_URL + 'sendMessage', urllib.urlencode(params))
    result = json.loads(res.read())['result']
    return result

@app.route('/')
def JSNBot() -> str:
    return 'This is 7'

@app.route('/Webhook', methods=['POST','GET'])
def telegram():
    data = request.get_json()
    chat_id = data['message']['chat_id']['id']
    text = data ['message']['text']
    sendMessage(chat_id,text)
    return json.dumps({'success':True})

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)    