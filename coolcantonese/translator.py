# -*- coding: utf-8 -*-

import random
import hashlib
import bs4
import logging
import requests
import six
from coolcantonese.exceptions import TranslationException
from coolcantonese.phonetic import NotationMarker

logger = logging.getLogger(__name__)


@six.python_2_unicode_compatible
class TranslateResult(object):

    """docstring for TranslateResult"""

    def __init__(self, words="", pronounce_list=None):
        super(TranslateResult, self).__init__()
        self.words = words
        self.pronounce_list = pronounce_list
        if self.pronounce_list is None:
            self.pronounce_list = []
        self.has_symbols = False

    def pretty(self):
        if not self.has_symbols:
            return self.words
        return self.words + "\n\n" + self.get_words_with_pronounces()

    def get_words_with_pronounces(self):
        words = self.words
        # logger.debug("words: %s", words)
        result = ""
        for i, w in enumerate(words):
            result += w
            pronounce = self.pronounce_list[i]
            if pronounce:
                result += "(" + pronounce + ")"
        return result

    def add(self, word, pronounce):
        # logger.debug("word:%, pronounce: %s", word, pronounce)
        self.words += word
        self.pronounce_list.append(pronounce)
        if pronounce:
            self.has_symbols = True

    def get_filename(self, ext=".mp3"):
        filename = ""
        for pronounce in self.pronounce_list:
            if pronounce:
                filename += pronounce
        if "" == filename:
            return None
        filename += ext
        return filename

    def __str__(self):
        return self.pretty()


class Translator(object):

    """提供普通话到粤语的翻译接口"""

    def __init__(self):
        super(Translator, self).__init__()

    def get_translation(self, text):
        pass


class L2ChinaTranslator(Translator):

    """通过调用l2china的接口实现翻译功能"""

    def __init__(self):
        super(L2ChinaTranslator, self).__init__()

    def _paser_response(self, resp_text):
        if None:
            return None
        soup = bs4.BeautifulSoup(resp_text, "lxml")
        texts = soup.select("div.generated_text")
        if texts and len(texts) > 0:
            result = TranslateResult()
            span_list = texts[0].select("span")
            for span in span_list:
                word = span.text
                pronounce = span["title"]
                if "null" == pronounce:
                    pronounce = None
                result.add(word, pronounce)
            return result
        raise TranslationException("暂无翻译结果")

    def get_translation(self, text):
        traslate_url = "http://www.l2china.com/yueyu/"
        text_len_limit = 100

        if isinstance(text, six.text_type):
            # unicode text
            txt_len = len(text)
            utf8_txt = text.encode('utf-8')
        else:
            txt_len = len(text.decode('utf-8'))
            utf8_txt = text
        if txt_len > text_len_limit:
            raise TranslationException(
                "需要翻译的文本超过" + str(text_len_limit) + "个字符")
        params = {"srctxt": utf8_txt, "RadioGroup1": "tocan"}
        resp = requests.get(traslate_url, params=params)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            # logger.debug("reponse text: %s", resp.text)
            result = self._paser_response(resp.text)
            return result
        return None


def utf8(text):
    if isinstance(text, six.text_type):
        utf8_txt = text.encode('utf-8')
    else:
        utf8_txt = text
    return utf8_txt


def md5(text):
    utf8_txt = utf8(text)
    m = hashlib.md5()
    m.update(utf8_txt)
    return m.hexdigest()


class BaiduTranslator(Translator):

    """通过调用百度翻译接口实现翻译功能"""

    def __init__(self, app_id, app_secret, notation_marker):
        super(BaiduTranslator, self).__init__()
        self.app_id = app_id
        self.app_secret = app_secret
        self.notation_marker = notation_marker

    def _paser_response(self, resp_json):
        trans_result = resp_json["trans_result"]
        result_text = ""
        for t in trans_result:
            dst = t["dst"]
            result_text = result_text + "\n" + dst
        result_text = result_text[1:]
        r = self.notation_marker.get_noted_chars(result_text)
        logger.debug(r.noted_chars)
        result = TranslateResult()
        result.words = r.in_str
        result.pronounce_list = r.noted_chars
        result.has_symbols = True
        return result

# 字段名 类型  必填参数    描述  备注
# q   TEXT    Y   请求翻译query   UTF-8编码
# from    TEXT    Y   翻译源语言   语言列表(可设置为auto)
# to  TEXT    Y   译文语言    语言列表(不可设置为auto)
# appid   INT Y   APP ID  可在管理控制台查看
# salt    INT Y   随机数
# sign    TEXT    Y   签名  appid+q+salt+密钥 的MD5值
    def get_translation(self, text):
        api_url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
        salt = str(random.randint(0, 1000000000000000))
        if isinstance(text, six.text_type):
            utf8_txt = text.encode('utf-8')
        else:
            utf8_txt = text
        sign = md5(self.app_id + text + salt + self.app_secret)
        params = {
            "from": "zh",
            "to": "yue",
            "appid": self.app_id,
            "q": utf8_txt,
            "salt": salt,
            "sign": sign,
        }

        resp = requests.get(api_url, params=params)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            logger.debug("reponse json: %s", resp.json())
            result = self._paser_response(resp.json())
            return result
        return None


class SmartTranslator(object):

    """提供普通话到粤语的翻译接口"""

    def __init__(self, cfg):
        super(SmartTranslator, self).__init__()
        self.translators = []
        if cfg.use_baidu_translator:
            notation_marker = NotationMarker(cfg.phonetic_data_path)
            self.translators.append(
                BaiduTranslator(
                    cfg.baidu_app_id, cfg.baidu_app_secret, notation_marker
                )
            )
        self.translators.append(L2ChinaTranslator())

    def get_translation(self, text):
        last_exception = None
        for translator in self.translators:
            try:
                result = translator.get_translation(text)
                if result:
                    return result
            except Exception as e:
                last_exception = e
        if last_exception:
            raise last_exception
        return None
