from functools import partial
from typing import Union, Optional, Awaitable
from urllib.parse import unquote
from uuid import uuid4

import aiofiles
import tornado
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpserver
import tornado.websocket
from aiofiles import os as async_os
from tornado import gen, httpclient


class GetLog(tornado.websocket.WebSocketHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    async def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        print("got message: ", message)
        async with aiofiles.open("../files/log.txt", 'r') as f:
            async for line in f:
                await self.write_message(line)
        # self.close(code=1000, reason="Job is done!")
        return


class Download(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    async def get(self):
        print("filename: ", self.request.arguments.get("filename"))
        filename = self.request.arguments.get("filename")[0].decode("utf-8")
        file_path = f"../files/{filename}"
        file_stat = await async_os.stat(file_path)
        self.set_header('Content-Type', 'application/text')
        self.set_header('Content-Length', str(file_stat.st_size))
        self.set_header('Content-Disposition', f"attachment;filename={filename}")
        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk = await f.read(1024 * 1024)
                if not chunk:
                    break
                self.write(chunk)
                await self.flush()


@tornado.web.stream_request_body
class Upload(tornado.web.RequestHandler):
    def initialize(self):
        print("initializing upload..\n", self.request.headers)
        self.bytes_read = 0
        filename = self.request.headers.get("filename")
        self.file_path = f"../files/upload/{filename}"
        self.file = None

    async def data_received(self, chunk):
        if self.file is None:
            self.file = await aiofiles.open(self.file_path, 'wb')
        await self.file.write(chunk)
        self.bytes_read += len(chunk)

    async def post(self):
        mtype = self.request.headers.get("Content-Type")
        print(f'PUT "{self.filename}" "{mtype}" {self.bytes_read} bytes')
        await self.file.close()
        self.write("OK")


def main():
    app = tornado.web.Application([
        (r"/get_log", GetLog),
        (r"/download", Download),
        (r"/upload", Upload),
    ])
    server = tornado.httpserver.HTTPServer(app, max_buffer_size=1024 * 1024 * 1024 * 10)  # 10G
    server.listen(8888)
    # app.listen(8888)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
