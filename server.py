from pathlib import Path

import aiofiles
from aiofiles import os as async_os
from sanic import Sanic
import asyncio
from sanic.response import file_stream, redirect

app = Sanic(__name__)


@app.route('/upload', methods=["POST"])
async def ProcessUpload(request):
    print("upload required:", dir(request.files))
    print("items: ", len(request.files.get("file")))
    item = request.files.get("file")
    name = item.name
    body = item.body
    async with aiofiles.open(f"upload/{name}", 'wb') as f:
        await f.write(body)


@app.route('/download')
async def ProcessDownload(request):
    print("sending file...")
    file_path = f"files/{request.args['file_name'][0]}"
    file_stat = await async_os.stat(file_path)
    headers = {"Content-Length": str(file_stat.st_size)}

    return await file_stream(
        file_path,
        headers=headers,
        chunked=None
    )


@app.websocket('/get_log')
async def GetLog(request, ws):
    async with aiofiles.open("log.txt", 'r') as f:
        async for line in f:
            await ws.send(line)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
