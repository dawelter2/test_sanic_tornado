import sys
from pathlib import Path

import requests
from tqdm import tqdm
from websocket import create_connection, WebSocketConnectionClosedException


def GetLog():
    ws = create_connection("ws://localhost:8000/get_log")
    print("Receiving log...")
    while True:
        try:
            result = ws.recv()
            print(result)
        except WebSocketConnectionClosedException as e:
            if str(e) != 'Connection is already closed.':
                raise
            break


def SendFile(filename):
    print("sending file: ", filename)
    files = {'file': open(f"files/{filename}", "rb")}
    requests.post("http://localhost:8000/upload", files=files)


def GetFile(file_name):
    link = "http://localhost:8000/download"
    file = Path(f"download/{file_name}")
    file_counter = 0
    while True:
        if not file.exists():
            break
        file_counter += 1
        file = Path(f"download/({file_counter}){file_name}")
    print("file name: ", file)
    r = requests.get(link, params={"file_name": file_name}, stream=True)
    total_size = int(r.headers.get("Content-Length", "0"))
    print("total-size: ", total_size/1024, " Kb")
    with open(file, "wb") as f:
        for data in tqdm(r.iter_content(1024), total=total_size/1024, unit="kb", ):
            f.write(data)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise ValueError("parameters: please call as 'python client.py <download/upload/get_log> <Optional[filename]>'")

    if sys.argv[1] == "download":
        GetFile(sys.argv[2])
    elif sys.argv[1] == "upload":
        SendFile(sys.argv[2])
    elif sys.argv[1] == "get_log":
        GetLog()
