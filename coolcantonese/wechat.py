#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import os
import logging
import werobot
import werobot.client
from coolcantonese.log import config_logging
from coolcantonese.config import Config
from coolcantonese.default_config import default_config
from coolcantonese.record import Record, RecordService
from coolcantonese.tuling import TulingService
from coolcantonese.translator import SmartTranslator, TranslateResult
from coolcantonese.phonetic import NotationMarker
from coolcantonese.ekho import Ekho
from coolcantonese.session import SmartSession

config_logging()

logger = logging.getLogger(__name__)


cfg = Config(
    default_config, "coolcantonese/conf/config.json", "~/.coolcantonese.json")


client = None
if cfg.enable_client:
    client = werobot.client.Client(cfg.appid, cfg.appsecret)

session = SmartSession(cfg)

robot = werobot.WeRoBot(token=cfg.wechat_token, session_storage=session)

record_services = None
if cfg.enable_record_services:
    record_services = RecordService(cfg.record_services_url_prefix)

tuling_robot = None
if cfg.enable_tuling_robot:
    tuling_robot = TulingService(cfg.tuling_api_key)

notation_marker = NotationMarker(cfg.phonetic_data_path)
ekho = Ekho(cfg.audio_folder, cfg.audio_url_prefix)

translator = SmartTranslator(cfg)


def get_cache_translation(content):
    result = None
    key = "tansalation:" + content
    try:
        logger.debug("try get cached translation")
        result = session.get(key)
        if result:
            logger.debug("find cached translation")
        else:
            logger.debug("no cached translation found")
            result = translator.get_translation(content)
            if result:
                session.set(key, result)
                session.expire(key, cfg.translation_expire_seconds)
    except:
        logger.exception("get cache translation error")
    return result


def get_mediaid(pronounce_list):
    key = ""
    for p in pronounce_list:
        if p:
            key += p
    if "" == key:
        return None
    key = "mediaid:" + key
    mediaid = session.get(key)
    if mediaid:
        return mediaid
    try:
        audio_filename = ekho.export_pronounces_audio(pronounce_list)
        if audio_filename:
            resp = client.upload_media("voice", open(audio_filename, "rb"))
            os.remove(audio_filename)
            mediaid = resp["media_id"]
    except:
        logger.exception("upload audio file error")
    if mediaid:
        session.set(key, mediaid)
        session.expire(key, cfg.mediaid_expire_seconds)
    return mediaid


# text_menu = u"""\
# 功能：
# * ：收听电台
# # ：获得上一条翻译的语音
# 1 ：进入微社区论坛
# 2 ：星爷粉丝大考验
# 发送文字或语音获得文字翻译及注音
# 发送#+文字获得粤语语音翻译
# 发送@+文字获得文字粤语注音
# 发送单个中文字符获得粤语注音及解析
# 发送注音获得语音及对应发音的字
# 发送！进入机器聊天模式
# 发送？获得菜单

# tips:
# 如果语音没有声音，请暂停再播放
# """
article_menu = [
    ["", "", "http://7sbpek.com1.z0.glb.clouddn.com/img/menu6.png", ""],
    [u"收听《粤讲粤酷》电台", "",
     "http://7sbpek.com1.z0.glb.clouddn.com/img/radio.jpg",
     "http://music.163.com/djradio?id=225001"],
    [u"听电影答对白，星爷粉丝大考验", "",
     "http://7sbpek.com1.z0.glb.clouddn.com/img/stephen.jpg",
     "http://stephen.kkee.tk"]
]


@robot.filter(re.compile(u"[\?？]"))
def get_menu():
    return article_menu


@robot.filter(re.compile(u"[!！]"))
def toggle_chat_mode(txtMsg):
    userid = txtMsg.source
    if toggle_user_chat_mode(userid):
        return u"你已进入聊天模式，欢迎跟我聊天！5分钟没有响应将自动退出聊天模式，回复！可以直接退出。"
    else:
        return u"你已退出进入聊天模式。"


def toggle_user_chat_mode(userid, check_and_refresh=False):
    key = userid+"_chat_mode"
    in_chat_mode = session.exists(key)
    if check_and_refresh:
        if in_chat_mode:
            session.set(key, "")
            session.expire(key, 5*60)
            return True
        else:
            return False
    else:
        if in_chat_mode:
            session.delete(key)
            return False
        else:
            session.set(key, "")
            session.expire(key, 5*60)
            return True


def check_and_refresh_user_chat_mode(userid):
    return toggle_user_chat_mode(userid, True)


@robot.filter(re.compile(u"^[a-z]+\d$"))
def get_chars(txtMsg):
    content = txtMsg.content
    logger.debug("content:%s", content)
    r = notation_marker.get_characters_result(content)
    if r:
        try:
            url = ekho.get_pronounces_audio_url([content])
            return [content, r.pretty(), url]
        except Exception:
            logger.exception("get_chars error")
            return r.pretty()

    else:
        return u"暂无解析"


def cache_user_msg(userid, msg):
    key = userid + "_last_content"
    session.set(key, msg)
    session.expire(key, cfg.translation_expire_seconds)
    return True


def cache_notations(userid, result):
    if session:
        key = userid + "_last_notations"
        session.set(key, result)
        session.expire(key, cfg.translation_expire_seconds)
        return True
    else:
        return False


def get_cache_notations(userid):
    if session:
        key = userid + "_last_notations"
        result = session.get(key)
        return result
    else:
        return None

chn = re.compile(u"^[\u4e00-\u9fa5]$")


@robot.filter(chn)
def get_pronus(txtMsg):
    userid = txtMsg.source
    content = txtMsg.content
    r = notation_marker.get_pronunciations_result(content)
    if r:
        if cache_user_msg(userid, content):
            return r.pretty() + u"\n--回复#获得语音--"
        else:
            return r.pretty()
    else:
        return u"暂无解析"


def get_notations_result(userid, content):
    r = notation_marker.get_notations_result(content)
    if r:
        if cache_user_msg(userid, "@"+content):
            result = TranslateResult()
            result.words = r.in_str
            result.pronounce_list = r.plist
            result.has_pronounce = True
            cache_notations(userid, result)
            return r.pretty() + u"\n--回复#获得语音--"
        else:
            return r.pretty()

    else:
        return u"暂无解析1"


# @robot.filter("*")
# def get_radio():
#     return [[u"《粤讲粤酷》电台",
#              u"《粤讲粤酷》电台在网易云音乐开播啦！每期邀请嘉宾以脱口秀的形式教学粤语，"
#              u"希望大家能够在轻松愉快的氛围中学会粤语。喜欢的朋友更课使用网易"
#              u"云音乐客户端订阅电台，这样每期更新都会有提醒哟！",
#              "http://7sbpek.com1.z0.glb.clouddn.com/img/radio.jpg",
#              "http://music.163.com/djradio?id=225001"]]


# @robot.filter("1")
# def get_forum():
#     return [[u"粤讲粤酷交流论坛",
#              u"欢迎反馈公众号问题，交流粤语学习经验，分享粤语学习资源",
#              "http://dzqun.gtimg.cn/qpanel/images/banner1.jpg",
#              "http://m.wsq.qq.com/264028609"]]


# @robot.filter("2")
# def get_stephen_game():
#     return [[u"星爷粉丝大考验",
#              u"听对白答电影，星爷粉丝大考验",
#              "http://7sbpek.com1.z0.glb.clouddn.com/img/stephen.jpg",
#              "http://stephen.kkee.tk"]]


def get_last_msg_audio(userid):
    key = userid + "_last_content"
    content = session.get(key)
    if content:
        if chn.search(content):  # 单个汉字
            r = notation_marker.get_pronunciations_result(content)
            prons = []
            for p in r.plist:
                prons.append(p.pronunciation)
            url = ekho.get_pronounces_audio_url(prons)
            return [content, ",".join(prons), url]
        elif content.startswith("@"):
            content = content[1:]
            result = get_cache_notations(userid)
            return get_music_msg(result)
        else:
            result = get_cache_translation(content)
            return get_music_msg(result)
    else:
        return u"抱歉，找不到上一条消息"
    pass


def get_music_msg(result):
    if result.has_pronounce:
        logger.debug("result.words: %s", result.words)
        url = ekho.get_text_audio_url(result.words)
        return [result.words, result.get_words_with_pronounces(), url]
    else:
        return u"暂无语音翻译,下面是文字翻译\n" + result.words


@robot.text
def handle_text_msg(txtMsg):
    userid = txtMsg.source
    content = txtMsg.content
    logger.info("revice text message from: %s, content: %s", userid, content)
    if content.startswith(u"@"):
        content = content[1:]
        return get_notations_result(userid, content)
    if u"#" == content or u"＃" == content:
        return get_last_msg_audio(userid)
    need_translation_content = content
    in_chat_mode = check_and_refresh_user_chat_mode(userid)
    if in_chat_mode:
        ret, response = tuling_robot.send_msg(userid, content)
        if ret:
            need_translation_content = response
        else:
            return response

    return translate(userid, need_translation_content, in_chat_mode, content)


@robot.voice
def handle_voice_msg(voiceMsg):
    userid = voiceMsg.source
    content = voiceMsg.recognition
    logger.info("revice voice message from %s, recognition content: %s" % (
        userid, content))
    if content is None:
        return u"无法识别语音"
    reply = translate(userid, content)
    return "%s\n-----\n%s" % (content, reply)


def translate(userid, content, in_chat_mode=False, user_content=None):
    try:
        return_audio = False
        if content.startswith(u"#") or content.startswith(u"＃"):
            content = content[1:]
            return_audio = True
        result = get_cache_translation(content)

        # save tranlation record of user
        if record_services:
            if not in_chat_mode:
                reply = Record(
                    "translator", result.pretty(), Record.TRANSLATION_RESULT)
                record = Record(
                    userid, content, Record.TRANSLATION_REQUEST, reply)
            else:
                reply = Record(
                    "tuling_robot", content + "\n----\n" + result.pretty(),
                    Record.CHAT_RESPONSE)
                record = Record(
                    userid, user_content, Record.CHAT_REQUEST, reply)
            try:
                record_services.add_record(record)
            except Exception as e:
                logger.exception(e)

        logger.info("get translation:%s" % result.words)
        if client:
            client.send_text_message(userid, result.words)
            mediaid = get_mediaid(result.pronounce_list)
            if mediaid:
                client.send_voice_message(userid, mediaid)
            return result.pretty()
        elif return_audio:
            return get_music_msg(result)
        else:
            key = userid + "_last_content"
            session.set(key, content)
            session.expire(key, cfg.translation_expire_seconds)
            resp_text = result.pretty() + u"\n--回复#获得语音--"
            if in_chat_mode:
                resp_text = content + "\n----\n"+resp_text
            return resp_text

    except Exception as e:
        logger.exception(e.message)
        return e.message


@robot.subscribe
def subscribe(message):
    return cfg.subscribe_msg

if __name__ == '__main__':
    ekho.wsgi.merge(robot.wsgi)
    ekho.run(None, cfg.host, cfg.port)
    # ekho.run(None, cfg.host, cfg.port)
