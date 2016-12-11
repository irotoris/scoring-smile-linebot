# -*- coding:utf-8 -*-
import logging
import requests
import json
import os
from multiprocessing import Process

LINE_REPLY_ENDPOINT = 'https://api.line.me/v2/bot/message/reply'
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_REQUEST_HEADER = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + LINE_CHANNEL_ACCESS_TOKEN
}
EMOTION_API_ENDPOINT = 'https://api.projectoxford.ai/emotion/v1.0/recognize'
EMOTION_API_SUBSCRIPTION_KEY = os.getenv('EMOTION_API_SUBSCRIPTION_KEY')
EMOTION_API_HEADER = {
    "Content-Type": "application/octet-stream",
    "Ocp-Apim-Subscription-Key": EMOTION_API_SUBSCRIPTION_KEY
}
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

SEND_MESSAGES ={
    "no_face": u"顔を認識出ませんでした…\U0001f62b",
    "no_good": u"点！笑えよベジータ\U0001f617",
    "good": u"点！なかなかいい笑顔だ\U0001f609",
    "nice": u"点！いい笑顔だ\U0001f60a",
    "great": u"点！最高の笑顔だ\U0001f606",
    "usage": u"写真を送ると笑顔を100点満点で採点できるよ\U0001f606\n写真に複数人写ってる場合はみんなの笑顔の平均点になるよ\U0001f617"
}


def get_smile_score(message_id):
    # Get content from LINE
    line_content_url = "https://api.line.me/v2/bot/message/" + message_id +"/content"
    res_get_content = requests.get(line_content_url, headers=LINE_REQUEST_HEADER)

    # Get smile score from Emotion API
    res_get_e_score = requests.post(EMOTION_API_ENDPOINT, headers=EMOTION_API_HEADER, data=res_get_content.content)
    logger.debug(res_get_e_score.json())

    if not res_get_e_score.status_code == 200:
        return -1

    e_scores = res_get_e_score.json()
    if not e_scores == []:
        smile_score = 0.0
        for score in e_scores:
            smile_score = float(smile_score) + float(score['scores']['happiness'])
        smile_score_av = smile_score / len(e_scores)
        return smile_score_av
    else:
        return -1


def reply_line_bot(webhook_event_object):
    logger.debug(webhook_event_object)
    send_text = ''
    reply_token = webhook_event_object['replyToken']
    event_type = webhook_event_object['type']

    if event_type == 'follow' or event_type == 'join':
        send_text = SEND_MESSAGES['usage']
    elif event_type == 'message':
        msg_id = webhook_event_object['message']['id']
        msg_type = webhook_event_object['message']['type']

        if msg_type == 'image':
            smile_score = round(get_smile_score(msg_id) * 100, 5)
            if smile_score < 0:
                send_text = SEND_MESSAGES['no_face']
            elif smile_score <= 25:
                send_text = str(smile_score) + SEND_MESSAGES['no_good']
            elif smile_score <= 50:
                send_text = str(smile_score) + SEND_MESSAGES['good']
            elif smile_score <= 75:
                send_text = str(smile_score) + SEND_MESSAGES['nice']
            elif smile_score <= 100:
                send_text = str(smile_score) + SEND_MESSAGES['great']
            else:
                logger.error("Invalid smile_score: " + str(smile_score))
        elif msg_type == 'text':
            if webhook_event_object['message']['text'] == "使い方":
                send_text = SEND_MESSAGES['usage']
    else:
        logger.info("no support event type: " + event_type)

    logger.debug("send_text: " + send_text)

    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": send_text
            }
        ]
    }

    if not send_text == '':
        res = requests.post(LINE_REPLY_ENDPOINT,headers=LINE_REQUEST_HEADER, data=json.dumps(payload))
        logger.debug(res)
        logger.debug(res.text)


def lambda_handler(event, context):
    jobs = []
    if 'body' in event:
        line_webhook_events_object = json.loads(event['body'])
        for line_webhook_event in line_webhook_events_object['events']:
            job = Process(target=reply_line_bot, args=(line_webhook_event, ))
            job.start()
            jobs.append(job)

        [job.join() for job in jobs]
    else:
        logger.warning('Invalid request data.')
    logger.info('Finished.')
