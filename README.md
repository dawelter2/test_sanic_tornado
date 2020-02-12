#### To create a new env

Clone this repository, then create a new env by:

``` 
    python -3.6 -m venv venv
    venv\Scripts\activate.bat
    python -m pip install -U pip
    pip install -r requirements.txt

```    

#### Start the server

```
    python server.py
```

#### Download
Download a file by calling `client.py` with the filename as argument, e.g:

```
    python client.py small-size.jpg

```
* Please make sure that the required file is in `file` directory
