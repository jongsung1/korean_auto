import requests
import json
import datetime
import time
import yaml
import symbol_list as SL
from numpy import diff
import pandas as pd
import all_companys_list as COM ####### 종목 코드 리스트
from tqdm import tqdm ####### 진행률 표시 - for문에 사용
import openpyxl

with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
ACCESS_TOKEN = ""
CANO = _cfg['CANO']
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
DISCORD_WEBHOOK_URL = _cfg['DISCORD_WEBHOOK_URL']
URL_BASE = _cfg['URL_BASE']
PERCENT = _cfg['PERCENT']   ##현재가가 최고가의 $percent% 범위 이내(0 ~ 1)
K = _cfg['K']   ## 변동성 상수

def send_message(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(DISCORD_WEBHOOK_URL, data=message)
    print(message)

def get_access_token():
    """토큰 발급"""
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
    "appkey":APP_KEY, 
    "appsecret":APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN
    
def hashkey(datas):
    """암호화"""
    PATH = "uapi/hashkey"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
    'content-Type' : 'application/json',
    'appKey' : APP_KEY,
    'appSecret' : APP_SECRET,
    }
    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    hashkey = res.json()["HASH"]
    return hashkey

def get_symbol_list(symbol_list):
    symbol_list_temp = []
    for sym in symbol_list:
        yday_start = get_start_price(sym,1)    ## 전일 시가 조회
        today_start = get_start_price(sym,0)    ## 당일 시가 조회
        if int(today_start-yday_start) > 0:
            symbol_list_temp.append(sym)
    return symbol_list_temp

def get_current_price(code="005930",symbol="aspr_unit"):
    """호가 조회"""
    PATH = "/uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {ACCESS_TOKEN}",
            "appkey":APP_KEY,
            "appsecret":APP_SECRET,
            "tr_id":"FHKST01010100"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    }
    res = requests.get(URL, headers=headers, params=params)
    #return int(res.json()['output'][symbol])
    #return res.json()['output'][symbol]
    try:
        return res.json()['output'][symbol]
    except KeyError:
        return 0

def get_target_price(code="005930"):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    "fid_org_adj_prc":"1",
    "fid_period_div_code":"D"
    }
    res = requests.get(URL, headers=headers, params=params)
    #stck_oprc = int(res.json()['output'][0]['stck_oprc']) #오늘 시가
    #stck_lwpr = int(res.json()['output'][1]['stck_lwpr']) #전일 저가
    #stck_clpr = int(res.json()['output'][1]['stck_clpr']) #전일 종가
    stck_hgpr = int(res.json()['output'][1]['stck_hgpr']) #전일 고가
    target_price = stck_hgpr
    return target_price

def get_price(code="005930",day=0,ohlc="stck_oprc"):
    """종가 조회"""
    # day : 1 => 전일 시가 // 0 => 오늘 시가
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    "fid_org_adj_prc":"1",
    "fid_period_div_code":"D"
    }
    res = requests.get(URL, headers=headers, params=params)
    price = int(res.json()['output'][day][ohlc])
    # if ohlc == "o":
    #     price = int(res.json()['output'][day]['stck_oprc']) #오늘 시가
    # elif ohlc == "h":
    #     price = int(res.json()['output'][day]['stck_hgpr']) #오늘 고가
    # elif ohlc == "l":
    #     price = int(res.json()['output'][day]['stck_lwpr']) #오늘 저가
    # elif ohlc == "c":
    #     price = int(res.json()['output'][day]['stck_clpr']) #오늘 종가

    try:
        return price
    except KeyError:
        return 0

def get_start_price(code="005930",day=0):
    """시가 조회"""
    # day : 1 => 전일 시가 // 0 => 오늘 시가
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    "fid_org_adj_prc":"1",
    "fid_period_div_code":"D"
    }
    res = requests.get(URL, headers=headers, params=params)
    stck_oprc = int(res.json()['output'][day]['stck_oprc']) # day : 1 => 전일 시가 // 0 => 오늘 시가
    start_price = stck_oprc
    return start_price

print(get_start_price(code="005930",day=0))

# for company in tqdm(COM.tickers.keys()):
#     open_price=0
#     open_price=get_price(company,"1","stck_oprc")    ## 어제 시가 조회
#     close_price=0
#     close_price=get_price(company,1,"stck_clpr")    ## 어제 종가 조회
    
#     UNIT_PRICE=get_current_price(company,"aspr_unit")   ## 호가 조회
#     COMPANY_NAME=COM.tickers[company]

#     dotgi_check=0
#     dotgi_check=close_price-open_price

#     if dotgi_check < 0:
#         dotgi_check=dotgi_check*(-1)

#     if dotgi_check < 2*UNIT_PRICE:
#         high_price=0
#         high_price=get_price(company,1,"stck_hgpr")    ## 어제 고가 조회
#         low_price=0
#         low_price=get_price(company,1,"stck_lwpr")    ## 어제 저가 조회
#         variability=0
#         variability=high_price-low_price    ## 고가 저가 변동성

#         print("%s 종목 어제 최고가 : %s , 최고값 간 차이 : %s" % (COMPANY_NAME,high_price,variability))
