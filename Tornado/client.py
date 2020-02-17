import sys
from pathlib import Path

import requests
from tqdm import tqdm
from websocket import create_connection, WebSocketConnectionClosedException


def GetLog():
    ws = create_connection("ws://localhost:8888/get_log")
    print("Receiving log...")
    ws.send("Give me the log, please!")
    while True:
        try:
            result = ws.recv()
            print(result)
        except WebSocketConnectionClosedException as e:
            if str(e) != 'Connection is already closed.':
                raise
            print("Connection closed...")
            break


def GetFile(file_name):
    link = "http://localhost:8888/download"
    file = Path(f"../files/download/{file_name}")
    file_counter = 0
    while True:
        if not file.exists():
            break
        file_counter += 1
        file = Path(f"../files/download/({file_counter}){file_name}")
    print("file name: ", file)
    r = requests.get(link, params={"filename": file_name}, stream=True)
    total_size = int(r.headers.get("Content-Length", "0"))
    print("total-size: ", total_size/1024, " Kb")
    with open(file, "wb") as f:
        for data in tqdm(r.iter_content(1024), total=total_size/1024, unit="kb", ):
            f.write(data)


def SendFile(filename):
    print("sending file: ", filename)
    files = {'file': open(f"../files/{filename}", "rb")}
    r = requests.post("http://localhost:8888/upload", files=files)
    # r = requests.post("https://httpbin.org/post", files=files)
    print(r.status_code)
    print(r.text)
    if r.status_code not in range(200, 299):
        raise ValueError(f"Error sending file. code {r.status_code}")


if __name__ == '__main__':
    # GetLog()
    # GetFile("large-size.zip")
    SendFile("small-size.jpg")
    SendFile("medium-size.msi")
    SendFile("large-size.zip")
