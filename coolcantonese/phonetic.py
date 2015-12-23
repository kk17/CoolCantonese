#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urlencode
import six
import bs4
from codecs import open
import logging

logger = logging.getLogger(__name__)


@six.python_2_unicode_compatible
class NotedChar(object):

    """标记了音标的文字"""

    def __init__(
            self, char, symbols,
            use_cases=None, explanation=None):

        super(NotedChar, self).__init__()
        # 文字
        self.char = char
        # 音标
        self.symbols = symbols
        # 用例
        self.use_cases = use_cases
        # 解释
        self.explanation = explanation
        # 异读字
        self.variant = False
        # 粤语用词
        self.cantonese = False
        # 人名，地名
        self.specific = False
        # 通假字
        self.interchangeable = False

    def pretty(self):
        ret = "%s\t%s" % (self.char, self.symbols)
        if self.explanation:
            ret += "\n"
            ret += self.explanation
        if self.use_cases:
            ret += "\n"
            ret += u"，".join(self.use_cases)
        return ret

    def __str__(self):
        ret = self.pretty()
        ret += "\nvariant:" + str(self.variant)
        ret += "\ncantonese:" + str(self.cantonese)
        ret += "\nspecific:" + str(self.specific)
        ret += "\ninterchangeable:" + str(self.interchangeable)
        return ret


# 异读字
_p_variant = re.compile(u"异读字|異讀字")
# 粤语用词
_p_cantonese = re.compile(u"粤语用字|粵語用字")
# 人名，地名
_p_specific = re.compile(u"人名|地名|姓氏|复姓|複姓|县名|縣名|国名|國名")
# 通假字
_p_interchangeable = re.compile(u"同「.」字|通「.」字")

_p_other = re.compile(u"助词|助詞")

#  m = _p_interchangeable.search(u"同「與」fd通「拯」字")
#  if m:
#    g = m.group()
#    print type(g)
#    print repr(g)
#    ge = g.encode("utf-8")
#    print repr(ge)
#    print ge
#  else:
#    print "not found"


def _parse_line(line):
    line = line.strip()
    sp = line.split("\t")
    if len(sp) == 3:
        char = sp[0]
        #  print char.encode("utf-8")
        symbols = sp[1]
        #  print symbols.encode("utf-8")
        p = NotedChar(char, symbols)
        use_cases = None
        explanation = None
        ue = sp[2]
        if ue:
            flag = False
            if _p_variant.search(ue):
                p.variant = True
                flag = True
            if _p_interchangeable.search(ue):
                p.interchangeable = True
                flag = True
            if _p_cantonese.search(ue):
                p.cantonese = True
                flag = True
            if _p_specific.search(ue):
                p.specific = True
                flag = True
            if _p_other.search(ue):
                flag = True
            #  print sp[2].encode("utf-8")
            sp2 = ue.split(u"；")
            if len(sp2) > 1 and not sp2[0].startswith("("):
                use_cases = sp2[0].split(u"，")
                explanation = u"；".join(sp2[1:])
            else:
                #  if sp2[0].startswith("("):
                if flag:
                    explanation = ue
                else:
                    use_cases = ue.split(u"，")
        p.use_cases = use_cases
        p.explanation = explanation
        return p

    return None


def mix_notations(in_str, rlist):
    result = ""
    for c, p in zip(in_str, rlist):
        result += c
        if p:
            result += "("+p+")"
    return result


@six.python_2_unicode_compatible
class NotedCharsResult(object):

    """一段文字语音标记结果"""

    def __init__(self, in_str, noted_chars):
        super(NotedCharsResult, self).__init__()
        self.in_str = in_str
        self.noted_chars = noted_chars

    def pretty(self):
        return mix_notations(self.in_str, self.noted_chars)

    def __str__(self):
        return self.pretty()


@six.python_2_unicode_compatible
class SymbolsResult(object):

    """某个字的粤语音标列表"""

    def __init__(self, char, noted_chars):
        super(SymbolsResult, self).__init__()
        self.char = char
        self.noted_chars = noted_chars

    def pretty(self):
        prettys = [p.pretty() for p in self.noted_chars]
        return "\n---------\n".join(prettys)

    def __str__(self):
        return self.pretty()


@six.python_2_unicode_compatible
class CharsResult(object):

    """某个音标的对应的粤语文字列表"""

    def __init__(self, symbols, noted_chars):
        super(CharsResult, self).__init__()
        self.symbols = symbols
        self.noted_chars = noted_chars

    def pretty(self):
        prettys = [p.char for p in self.noted_chars]
        return ",".join(prettys)

    def __str__(self):
        return self.pretty()


_p = re.compile(u"\[ 粤　语 \]：(\s* *[a-z]+\d)+")
_p2 = re.compile(u"[a-z]+\d")
_p3 = re.compile(u"基本解释\n(.*)(?=笔画数)")

#  l = u"[ 粤　语 ]：zung1   zung3   ◎ 基本解释"
#  m = _p.search(l)
#  if m:
#    g = m.group()
#    print type(g)
#    print g.encode("utf-8")


def fetch_symbols(char):
    url = "http://ykyi.net/dict/index.php?" + \
        urlencode({"char": char.encode("utf-8")})
    #  print char.encode("utf-8")
    html = urlopen(url).read()
    # print(html)
    s = bs4.BeautifulSoup(html, "lxml")
    coliseum = s.select_one("#coliseum")
    if not coliseum:
        return []
    text = coliseum.text.strip()
    #  print text.encode("utf-8")
    m = _p.search(text)
    if m:
        g = m.group()
        #  print g.encode("utf-8")
        pronus = _p2.findall(g)
        #  print pronus
    else:
        return []

    m = _p3.search(text)
    if m:
        g = m.group(1)
        sp = re.split(char+"\s\w*\W*\w*\s", g)
        #  print len(sp)
        #  print sp
        exps = []
        for e in sp:
            if not e:
                continue
            #  print e.encode("utf-8")
            exps.append(e.strip())
        #  print exps
    noted_chars = []
    for p, e in zip(pronus, exps):
        if not p:
            continue
        pObj = NotedChar(char, p, None, e)
        noted_chars.append(pObj)
    return noted_chars


_p_chn_char = re.compile(u"[\u4e00-\u9fa5]")


class NotationMarker(object):

    """用于给文字标记粤语语言的工具"""

    def __init__(self, datafile):
        super(NotationMarker, self).__init__()
        self.datafile = datafile
        char_key_dict = {}
        symbols_key_dic = {}
        lines = open(datafile, "r", "utf-8").readlines()
        for line in lines:
            #  print line
            p = _parse_line(line)
            if p:
                #  print p
                #  print
                if p.char not in char_key_dict:
                    char_key_dict[p.char] = []
                char_key_dict[p.char].append(p)

                if p.symbols not in symbols_key_dic:
                    symbols_key_dic[p.symbols] = []
                symbols_key_dic[p.symbols].append(p)
        self.char_key_dict = char_key_dict
        self.symbols_key_dic = symbols_key_dic
        #  print len(char_key_dict)
        #  print len(symbols_key_dic)

    def choose_one(self, noted_chars, in_str):
        maxlen = 0
        longp = None
        for p in noted_chars:
            lenp = 0
            if p.use_cases:
                for u in p.use_cases:
                    lenp += len(u)
                    if "(" in u:
                        i = u.index("(")
                        u = u[0:i]
                    if u in in_str:
                        return p
            if p.explanation:
                lenp += len(p.explanation)

            # 异读字
            if p.variant:
                lenp *= 0.05
            # 粤语用词
            if p.cantonese:
                lenp *= 2
            # 人名，地名
            if p.specific:
                lenp *= 0.6
            if lenp > maxlen:
                maxlen = lenp
                longp = p
            #  print lenp,p
        return longp

    def get_notations(self, in_str):
        rlist = []
        for c in in_str:
            #  print c.encode("utf-8")
            noted_chars = self.char_key_dict.get(c)

            if not noted_chars and _p_chn_char.search(c):
                try:
                    logger.info("miss %s", c)
                    noted_chars = fetch_symbols(c)
                    self.char_key_dict[c] = noted_chars
                    with open(self.datafile, "a", "utf-8") as f:
                        for p in noted_chars:
                            exp = p.explanation
                            if not exp:
                                exp = u"暂无解释"
                            line = "%s\t%s\t%s\n" % (
                                p.char, p.symbols, exp)
                            logger.info(line)
                            f.write(line)
                except Exception as e:
                    logger.info("fetch %s symbols error", c)
                    logger.error(e)

            if noted_chars:
                if len(noted_chars) == 1:
                    rlist.append(noted_chars[0].symbols)
                else:
                    bestp = self.choose_one(noted_chars, in_str)
                    rlist.append(bestp.symbols)
            else:
                rlist.append(None)
        return rlist

    def get_noted_chars(self, in_str):
        noted_chars = self.get_notations(in_str)
        return NotedCharsResult(in_str, noted_chars)

    def _get_symbols(self, char):
        return self.char_key_dict.get(char, None)

    def get_symbols(self, char):
        noted_chars = self._get_symbols(char)
        if noted_chars:
            return SymbolsResult(char, noted_chars)
        else:
            return None

    def _get_chars(self, symbols):
        return self.symbols_key_dic.get(symbols, None)

    def get_chars(self, symbols):
        noted_chars = self._get_chars(symbols)
        if noted_chars:
            #  for p in noted_chars:
            #    print p
            return CharsResult(symbols, noted_chars)
        else:
            return None
