# -*- coding:utf-8 -*
import os
import os.path
from datetime import datetime
from coolcantonese.util import (
    pathname2url,
    to_string_type,
    to_text_type
)

import logging

logger = logging.getLogger(__name__)

try:
    from sh import ekho
except Exception:
    def mock_ekho(*args):
        if "-l" in args:
            return "nei5 hou2"
        elif "-o" in args:
            filepath = args[5]
            open(filepath, "a").close()
        else:
            raise

    ekho = mock_ekho

_DEFAULT_CONFIG = dict(
    SERVER="auto",
    HOST="0.0.0.0",
    PORT="8888"
)

_MIME_TYPE = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "ogg": "audio/ogg"
}


class Ekho(object):

    def __init__(
            self,
            audio_folder="/tmp",
            url_prefix="http://localhost:8888"):

        super(Ekho, self).__init__()
        if not os.path.exists(audio_folder):
            os.makedirs(audio_folder)
        self.audio_folder = audio_folder
        self.url_prefix = url_prefix
        self._wsgi = None

    def get_text_audio_url(self, text, voice="Cantonese", file_type="mp3"):
        encoded_text = pathname2url(text)
        return "%s/%s/text/%s.%s" % (
            self.url_prefix, voice, encoded_text, file_type)

    def get_symbols_audio_url(
            self, pronounces, voice="Cantonese", file_type="mp3"):
        text = "_".join(pronounces)
        return "%s/%s/symbols/%s.%s" % (
            self.url_prefix, voice, text, file_type)

    def export_text_audio(
            self, text, voice="Cantonese", file_type="mp3", filepath=None):
        if filepath is None:
            temp_name = self.get_temp_file_name(file_type)
            filepath = os.path.join(self.audio_folder, temp_name)
        logger.info(
            "export_text_audio: voice=%s, text=%s, filepath=%s, file_type=%s",
            voice, text, filepath, file_type)
        text = to_string_type(text)
        ret = ekho(
            "-v", voice, "-t", file_type, "-o", filepath, text)
        logger.info("ret %s", ret)
        return filepath

    def export_symbols_audio(
            self, pronounces, voice="Cantonese",
            file_type="mp3", filepath=None):
        text = "[[%s]]" % " ".join(pronounces)
        return self.export_text_audio(text, voice, file_type, filepath)

    def get_symbols(self, voice, text):
        logger.info("get_symbols: voice=%s,text=%s", voice, text)
        return ekho("-v", voice, "-l", text)

    def get_temp_file_name(self, file_type):
        date_str = datetime.now().strftime("%y-%m-%d_%H_%M_%S_%f")
        return "%s.%s" % (date_str, file_type)

    @property
    def wsgi(self):
        if self._wsgi:
            return self._wsgi
        import bottle
        app = bottle.Bottle()

        def get_text_and_type(text_with_ext):
            index = text_with_ext.rindex(".")
            return text_with_ext[0:index], text_with_ext[index+1:]

        @app.get('/<voice>/text/<text_with_ext:re:.+\.(wav|mp3|ogg)>')
        def get_text_audio(voice, text_with_ext):
            text_with_ext = to_text_type(text_with_ext)
            text, file_type = get_text_and_type(text_with_ext)
            filepath = self.export_text_audio(text, voice, file_type)
            # return bottle.static_file(temp_name, root=self.audio_folder)
            with open(filepath, "rb") as f:
                bytes_data = f.read()

            bottle.response.set_header('Content-type', _MIME_TYPE[file_type])
            os.remove(filepath)
            return bytes_data

        @app.get('/<voice>/symbols/<text_with_ext:re:.+\.(wav|mp3|ogg)>')
        def get_symbols_audio(voice, text_with_ext):
            text_with_ext = to_text_type(text_with_ext)
            text, file_type = get_text_and_type(text_with_ext)
            filepath = self.export_symbols_audio(
                text.split("_"), voice, file_type)
            with open(filepath, "rb") as f:
                bytes_data = f.read()

            bottle.response.set_header('Content-type', _MIME_TYPE[file_type])
            os.remove(filepath)
            return bytes_data

        @app.get('/<voice>/symbols/<text>')
        def get_symbols(voice, text):
            text = to_text_type(text)
            return self.get_symbols(voice, text)

        @app.error(404)
        def error404(error):
            return "404"

        self._wsgi = app
        return app

    def run(self, server=None, host=None, port=None):
        if server is None:
            server = _DEFAULT_CONFIG["SERVER"]
        if host is None:
            host = _DEFAULT_CONFIG["HOST"]
        if port is None:
            port = _DEFAULT_CONFIG["PORT"]
        self.wsgi.run(server=server, host=host, port=port)
