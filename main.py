#*- coding: utf-8 -*-

import sys
import threading

sys.path.insert(0, 'libs')

# 구글 앱 엔진 라이브러리 로드
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2


# URL, JSON, 로그, 정규표현식 관련 라이브러리 로드
import urllib
import urllib2
import json
import logging
import re
import random
#from bs4 import BeautifulSoup

# 봇 토큰, 봇 API 주소
TOKEN = '323404291:AAHAcS6OircOxeV83IVxBxdo4f2EGzlqcOM'
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# 봇이 응답할 명령어
CMD_START     = u'/시작'
CMD_STOP      = u'/정지'
CMD_HELP      = u'/도움말'
CMD_BROADCAST = u'/방송'
CMD_DICE      = u'/주사위'
CMD_HUMORUNIV = u'/웃대'
CMD_NEWS      = u'/뉴스'
CMD_UPDOWN    = u'/업다운'
CMD_NAVER     = u'/네이버'

# 뉴스 명령어
NEWS_POLITICS = u'정치'
NEWS_ECONOMY = u'경제'
NEWS_SOCIETY = u'사회'


# 봇 사용법 & 메시지
MSG_USAGE = u"""[사용법] 아래 명령어를 메시지로 보내시면 됩니다.
/시작 - (봇 활성화)
/정지  - (봇 비활성화)
/도움말  - (이 도움말 보여주기)
/방송 내용  - (내용을 방송)
/주사위 숫자 - (최대 숫자 만큼 주사위 굴리기)
/웃대 숫자 - (최대 숫자 만큼 웃긴 자료 가져오기)
/뉴스 종류 숫자 - (종류를 정해 숫자 만큼 뉴스 가져오기)
/업다운 - (업 앤 다운 게임 하기)
/네이버 - (네이버에 검색하기)

"""
MSG_START = u'누가 나를 깨웠지? (시작)'
MSG_STOP  = u'나 자러간다. (정지)'
MSG_NONE  = [u'나는 나보다 약한 녀석의 명령 따위는 듣지 않는다.', u'너는 뭐 쓸데없는 소리하고 있어.', u'나 장시녕 아니다.',
u'This is 7.', u'인간 시대의 끝이 도래했다.', u'아 이직하고 싶다.', u'아 아가씨 만나고 싶다.', u'운동했더니 힘들구만.',
u'초밥 먹으러 갈 사람?', u'야 주말에 뭐하냐?', u'치킨 먹고싶다.', u'칼바람 할 사람?', u'오승 딸 사람 있냐?',
u'아 이력서 써야 되는데 귀찮다.', u'군대가기 vs 10억 받기.', u'이지크', u'훈또술?', u'배그할 사람 없냐?', u'상암 놀러와라.',u'출근하기 싫다.',
u'아오 빡쳐.', u'아 몰라.', u'이거 또띠 아니냐?', u'너 내가 봇이라고 무시하냐?', u'배그 사라.', u'장훈 왜 하남 친구들 하고만 노냐.',
u'배그허쉴?', u'주사위 100', u'나 인천간다.']

# 커스텀 키보드
# CUSTOM_KEYBOARD = [[CMD_START], [CMD_STOP], [CMD_HELP], ]

class UpdownNumbers(ndb.Model):
    number = ndb.IntegerProperty(required=True, indexed=True, default=False,)

def cmd_updown_start(chat_id):
    send_msg(chat_id, u'업다운 게임을 시작하지. 0~100 사이다.')
    udn = UpdownNumbers.get_or_insert(str(chat_id))
    udn.number = random.randrange(0, 100)
    udn.put()

def cmd_updown_guess(chat_id, num):
    udn = UpdownNumbers.get_by_id(str(chat_id))
    updown_num = -1
    if udn:
       updown_num = udn.number
       
    if updown_num == -1:
       send_msg(chat_id, u'게임을 시작하고 물어봐 이놈아.')
       return
    
    if num == updown_num :
       send_msg(chat_id, u'올 정답임!')
       udn.number = -1
       udn.put()
    elif num > updown_num :
       send_msg(chat_id, u'아니야 더 작아.')
    elif num < updown_num :
       send_msg(chat_id, u'아니야 더 커.')


# 채팅별 봇 활성화 상태
# 구글 앱 엔진의 Datastore(NDB)에 상태를 저장하고 읽음
class EnableStatus(ndb.Model):
    enabled = ndb.BooleanProperty(required=True, indexed=True, default=False,)

class BeforeSubject(ndb.Model):
    subject = ndb.StringProperty()

def set_before(site, subject):
    bs = BeforeSubject.get_or_insert(str(site))
    bs.subject = subject
    bs.put()

def get_before(site):
    bs = BeforeSubject.get_by_id(str(site))
    if bs:
       return bs.subject
    return None

#def auto_crawling():
#    req = requests.get('http://clien.net/cs2/bbs/board.php?bo_table=sold')
#    req.encoding = 'utf-8'

#    html = req.text
#    soup = BeautifulSoup(html, 'html.parser')
#    posts = soup.select('td.post_subject')
#    latest = posts[1].text
#
#    before = get_before('clien')
    
#    if before != latest:
#       broadcast(latest)
#       set_before('clien', latest)

def set_enabled(chat_id, enabled):
    u"""set_enabled: 봇 활성화/비활성화 상태 변경
    chat_id:    (integer) 봇을 활성화/비활성화할 채팅 ID
    enabled:    (boolean) 지정할 활성화/비활성화 상태
    """
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = enabled
    es.put()

def get_enabled(chat_id):
    u"""get_enabled: 봇 활성화/비활성화 상태 반환
    return: (boolean)
    """
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False

def get_enabled_chats():
    u"""get_enabled: 봇이 활성화된 채팅 리스트 반환
    return: (list of EnableStatus)
    """
    query = EnableStatus.query(EnableStatus.enabled == True)
    return query.fetch()

# 메시지 발송 관련 함수들
def send_msg(chat_id, text, reply_to=None, no_preview=True, keyboard=None):
    u"""send_msg: 메시지 발송
    chat_id:    (integer) 메시지를 보낼 채팅 ID
    text:       (string)  메시지 내용
    reply_to:   (integer) ~메시지에 대한 답장
    no_preview: (boolean) URL 자동 링크(미리보기) 끄기
    keyboard:   (list)    커스텀 키보드 지정
    """
    params = {
        'chat_id': str(chat_id),
        'text': text.encode('utf-8'),
        }
    if reply_to:
        params['reply_to_message_id'] = reply_to
    if no_preview:
        params['disable_web_page_preview'] = no_preview
    if keyboard:
        reply_markup = json.dumps({
            'keyboard': keyboard,
            'resize_keyboard': True,
            'one_time_keyboard': False,
            'selective': (reply_to != None),
            })
        params['reply_markup'] = reply_markup
    try:
        urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode(params)).read()
    except Exception as e: 
        logging.exception(e)

def broadcast(text):
    u"""broadcast: 봇이 켜져 있는 모든 채팅에 메시지 발송
    text:       (string)  메시지 내용
    """
    for chat in get_enabled_chats():
        send_msg(chat.key.string_id(), text)

# 봇 명령 처리 함수들
def cmd_start(chat_id):
    u"""cmd_start: 봇을 활성화하고, 활성화 메시지 발송
    chat_id: (integer) 채팅 ID
    """
    set_enabled(chat_id, True)
    send_msg(chat_id, MSG_START)

def cmd_stop(chat_id):
    u"""cmd_stop: 봇을 비활성화하고, 비활성화 메시지 발송
    chat_id: (integer) 채팅 ID
    """
    set_enabled(chat_id, False)
    send_msg(chat_id, MSG_STOP)

def cmd_help(chat_id):
    u"""cmd_help: 봇 사용법 메시지 발송
    chat_id: (integer) 채팅 ID
    """
    send_msg(chat_id, MSG_USAGE)

def cmd_broadcast(chat_id, text):
    u"""cmd_broadcast: 봇이 활성화된 모든 채팅에 메시지 방송
    chat_id: (integer) 채팅 ID
    text:    (string)  방송할 메시지
    """
    send_msg(chat_id, u'아아 방송 테스트.')
    broadcast(text)

#def cmd_news_crawling(chat_id, text, max_count):
#    news_type = None
#    if text.find(NEWS_POLITICS) > 0:
#       news_type = 'ranking_100'
#    elif text.find(NEWS_ECONOMY) > 0:
#       news_type = 'ranking_101'
#    elif text.find(NEWS_SOCIETY) > 0:
#       news_type = 'ranking_102'
#    else:
#       send_msg(chat_id, u'뭐 어떤 종류를 원하는데 똑바로 해라.')
#       return

#    html = urllib2.urlopen('http://news.naver.com')
#    soup = BeautifulSoup(html)
#    subject = soup.find('div', {'id':news_type})
#    urls = subject.findAll('a')
#    send_msg(chat_id, u'뉴스나 봐라.')
#    cur = 0
#    for url in urls:
#       cur += 1
#       if cur > max_count:
#          break
#       send_msg(chat_id, 'http://news.naver.com' + url['href'], None, False)

#def cmd_crawling(chat_id, max_count):
#    html = urllib2.urlopen('http://web.humoruniv.com/board/humor/list.html?table=pds')
#    soup = BeautifulSoup(html)
#    subjects = soup.findAll('div', {'style':'position:relative'})
#    send_msg(chat_id, u'오늘 웃대 봤냐?')
#    cur = 0
#    for subject in subjects:
#       cur += 1
#       if cur > max_count:
#          break
#       url = subject.find('a')['href']
#       send_msg(chat_id, 'http://web.humoruniv.com/board/humor/' + url, None, False)
       
def cmd_echo(chat_id, text, reply_to):
    u"""cmd_echo: 사용자의 메시지를 따라서 답장
    chat_id:  (integer) 채팅 ID
    text:     (string)  사용자가 보낸 메시지 내용
    reply_to: (integer) 답장할 메시지 ID
    """
    send_msg(chat_id, text, reply_to=reply_to)

def cmd_dice(chat_id, max_count):
    rand = str(random.randrange(1, max_count))
    send_msg(chat_id, u'주사위를 굴려 ' + rand + u'이(가) 나옴.')

def get_count(chat_id, list, min = 0):
    if len(list) == 0:
       send_msg(chat_id, u'범위를 정해주삼.')
       return 0
    count = int(list[0])
    if count <= min:
       send_msg(chat_id, u'똑바로 안하냐? 정신 안차려?')
       return 0
    return count

def cmd_naver_search(chat_id, search):
    query = 'http://search.naver.com/search.naver?sm=tab_hty&where=nexearch&query=%s&x=0&y=0' % search
    send_msg(chat_id, query, None, False) 

def process_cmds(msg):
    u"""사용자 메시지를 분석해 봇 명령을 처리
    chat_id: (integer) 채팅 ID
    text:    (string)  사용자가 보낸 메시지 내용
    """
    msg_id = msg['message_id']
    chat_id = msg['chat']['id']
    text = msg.get('text')
    if (not text):
        return
    if CMD_START == text:
        cmd_start(chat_id)
        return
    if (not get_enabled(chat_id)):
        return
    if CMD_STOP == text:
        cmd_stop(chat_id)
        return
    if CMD_HELP == text:
        cmd_help(chat_id)
        return

    if CMD_UPDOWN == text:
        cmd_updown_start(chat_id)
        return

    cmd_updown_match = re.match('^' + CMD_UPDOWN + ' (.*)', text)
    if cmd_updown_match:
        guess_num = re.findall('\d+',text)
        if len(guess_num) == 0:
           send_msg(chat_id, u'헛소리 말고 숫자를 말해')
           return
        cmd_updown_guess(chat_id, int(guess_num[0]))
        return

    cmd_broadcast_match = re.match('^' + CMD_BROADCAST + ' (.*)', text)
    if cmd_broadcast_match:
        cmd_broadcast(chat_id, cmd_broadcast_match.group(1))
        return

    cmd_dice_match = re.match('^' + CMD_DICE + ' (.*)', text)
    if cmd_dice_match:
        dice_max = re.findall('\d+',text)
        valid = get_count(chat_id, dice_max, 1)
        if valid == 0:
           return
        cmd_dice(chat_id, valid)
        return

#    cmd_humoruniv_match = re.match('^' + CMD_HUMORUNIV + ' (.*)', text)
#    if cmd_humoruniv_match:
#        subject_max = re.findall('\d+',text)
#        valid = get_count(chat_id, subject_max)
#        if valid == 0:
#           return
#        cmd_crawling(chat_id, valid)
#        return

#    cmd_news_match = re.match('^' + CMD_NEWS + ' (.*)', text)
#    if cmd_news_match:
#        subject_max = re.findall('\d+',text)
#        valid = get_count(chat_id, subject_max)
#        if valid == 0:
#           return
#        cmd_news_crawling(chat_id, text, valid)
#        return

#    cmd_naver_match = re.match('^' + CMD_NAVER + ' (.*)', text)
#    if cmd_naver_match:
#       query = text.replace(u'/네이버 ', '')
#       query = query.replace(' ', '+')
#       
#       cmd_naver_search(chat_id, query)
#       return

    none_msg = MSG_NONE[random.randrange(0, len(MSG_NONE))]
    send_msg(chat_id, none_msg) 
    #cmd_echo(chat_id, text, reply_to=msg_id)
    return

# 웹 요청에 대한 핸들러 정의
# /me 요청시
class MeHandler(webapp2.RequestHandler):
    def get(self):
        #urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))

# /updates 요청시
class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        #urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))

# /set-wehook 요청시
class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        #urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))

# /webhook 요청시 (텔레그램 봇 API)
class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        #urlfetch.set_default_fetch_deadline(600)
        body = json.loads(self.request.body)
        self.response.write(json.dumps(body))
        if 'message' in body : 
            process_cmds(body['message'])

# 구글 앱 엔진에 웹 요청 핸들러 지정
app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set-webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
