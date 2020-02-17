from typing import Union, Optional, Awaitable

import aiofiles
import tornado
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from aiofiles import os as async_os


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


SEPARATE = b'\r\n'


@tornado.web.stream_request_body
class Upload(tornado.web.RequestHandler):
    def initialize(self):
        self.meta = dict()
        self.fp = None

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        if self.fp is None:
            split_chunk = chunk.split(SEPARATE)
            self.meta['boundary'] = SEPARATE + split_chunk[0] + b'--' + SEPARATE
            self.meta['header'] = SEPARATE.join(split_chunk[0:3])
            self.meta['header'] += SEPARATE * 2
            self.meta['filename'] = split_chunk[1].split(b'=')[-1].replace(b'"', b'').decode()

            chunk = chunk[len(self.meta['header']):]
            self.fp = open(f"../files/upload/{self.meta['filename']}", "wb")
        self.fp.write(chunk)

    def post(self):
        self.write(f"File {self.meta['filename']} was uploaded")


def main():
    app = tornado.web.Application([
        (r"/get_log", GetLog),
        (r"/download", Download),
        (r"/upload", Upload),
    ])
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
