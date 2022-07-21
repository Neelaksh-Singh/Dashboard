# Stock-Analysis-Dashboard
Dashboard App for Stock analysis and discussion using Streamlit and Python.

## 💻 Installation

`!!! Having Python is a must. !!!` <br>

<b>Port 8501 must be reserverd</b> <br>

Python 3.6+ is required to run code from this repo. 

```console
$ git clone https://github.com/Neelaksh-Singh/Dashboard.git
$ cd Dashboard/
$ python -m venv stockEnv
$ stockEnv\Scripts\activate.bat
$ pip install -r requirements.txt 
```
#### Create a `.env` file *locally* 

Create a `.env` file in the root of your project and insert
key/value pairs in the following format of `KEY=VALUE`:
```sh
api_key='<your_finnhub_api_key>'
```
Now once the setup is done do the following 

```console
$ streamlit run stock_app.py
```
