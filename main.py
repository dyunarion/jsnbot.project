# import logging

from flask import Flask,request
import re
import json
import urllib.parse as parse
import urllib.request as req

import random

# 봇 토큰, 봇 API 주소
TOKEN = '323404291:AAHAcS6OircOxeV83IVxBxdo4f2EGzlqcOM'
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

# 봇이 응답할 명령어
CMD_DICE = u'/주사위'

MSG_NONE = [u'나는 나보다 약한 녀석의 명령 따위는 듣지 않는다.', u'너는 뭐 쓸데없는 소리하고 있어.', u'나 장시녕 아니다.',
u'This is 7.', u'인간 시대의 끝이 도래했다.', u'아 이직하고 싶다.', u'아 아가씨 만나고 싶다.', u'운동했더니 힘들구만.',
u'초밥 먹으러 갈 사람?', u'야 주말에 뭐하냐?', u'치킨 먹고싶다.', u'칼바람 할 사람?', u'오승 딸 사람 있냐?',
u'아 이력서 써야 되는데 귀찮다.', u'군대가기 vs 10억 받기.', u'이지크', u'훈또술?', u'배그할 사람 없냐?', u'상암 놀러와라.',u'출근하기 싫다.',
u'아오 빡쳐.', u'아 몰라.', u'이거 또띠 아니냐?', u'너 내가 봇이라고 무시하냐?', u'배그 사라.', u'장훈 왜 하남 친구들 하고만 노냐.',
u'배그허쉴?', u'주사위 100?', u'나 인천간다.', u'훈또공?', u'닭가슴살 먹는다.', u'메카 장시녕 죽인다.', u'아니.', u'사침하는 사람 죽인다.',
u'아 김학준 뭐하냐고.', u'아 장훈 뭐하냐고.', u'아 유시영 뭐하냐고.', u'아 이대빈 뭐하냐고.', u'아 최동규 뭐하냐고.', u'아 이준용 뭐하냐고.',
u'뭐 임마.', u'아님. 아무튼 아님.', u'조치.', u'ㅋ.', u'업데이트 중... 사실 아님.',]

app = Flask(__name__)

def processCommands(data):
    u"""사용자 메시지를 분석해 봇 명령을 처리
    chat_id: (integer) 채팅 ID
    text:    (string)  사용자가 보낸 메시지 내용
    """

    # message_id = message['message_id']
    chat_id = data['message']['chat']['id']
    text = data ['message']['text']

    if not text:
        return
        
    diceMatch = re.match('^' + u'/주사위' + ' (.*)', text)
    if diceMatch:
        diceMax = re.findall('\d+',text)
        count = getCount(chat_id, dice_max, 1)
        if count == 0:
           return
        commandDice(chat_id, count)
        return

    text = MSG_NONE[random.randrange(0, len(MSG_NONE))]
    sendMessage(chat_id,text)
    return

def commandDice(chat_id, maxCount):
    rand = str(random.randrange(1, maxCount + 1))
    text = u'주사위를 굴려 ' + rand + u'이(가) 나옴.'
    if rand == maxCount:
        text += u'\n 와 님, 1년 운 다 씀.'
    elif rand == 1:
        text += u'\n 이거 뭐임? 버그임?'
     
    sendMessage(chat_id, u'주사위를 굴려 ' + rand + u'이(가) 나옴.')

def getCount(chat_id, list, min = 0):
    if len(list) == 0:
       sendMessage(chat_id, u'범위를 정해주삼.')
       return 0

    count = int(list[0])
    if count <= min:
       sendMessage(chat_id, u'똑바로 안하냐? 정신 안차려?')
       return 0

    return count

def baseRequest(command="getMe"):
     res = req.urlopen(BASE_URL + command)
     result = json.loads(res.read())['result']
     return result

# 메시지 발송
def sendMessage(chat_id, text):
    query = parse.urlencode([
        ('chat_id', chat_id),
        ('text', text)
        ])
    baseRequest('sendMessage?' + query)

@app.route('/')
def jsnBot() -> str:
    return 'This is 7'

@app.route('/webhook', methods=['POST','GET'])
def telegram():
    data = request.get_json()
    processCommands(data)
    return json.dumps({'success':True})

@app.errorhandler(500)
def server_error(e):
    # logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)    