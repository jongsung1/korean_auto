from numpy import diff
import pandas as pd
import mojito
import all_companys_list as COM ####### 종목 코드 리스트
import requests
import json
import yaml
import config as c

####
##현재가가 최고가의 $percent% 범위 이내(0 ~ 1)
percent = 0.9
####
with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
ACCESS_TOKEN = ""
CANO = _cfg['CANO']
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
DISCORD_WEBHOOK_URL = _cfg['DISCORD_WEBHOOK_URL']
URL_BASE = _cfg['URL_BASE']

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
    return res.json()['output'][symbol]

ACCESS_TOKEN = get_access_token()
UNIT_PRICE=get_current_price("000660","aspr_unit")  ## 종목의 호가
EPS=get_current_price("000660","eps")  ## 종목의 EPS
BPS=get_current_price("000660","bps")  ## 종목의 BPS
PER=get_current_price("000660","per")  ## 종목의 EPS
PBR=get_current_price("000660","pbr")  ## 종목의 PBR

print("종목 호가 : %s " % (UNIT_PRICE))
print("종목 EPS : %s " % (EPS))
print("종목 BPS : %s " % (BPS))
print("종목 PER : %s " % (PER))
print("종목 PBR : %s " % (PBR))

# broker = mojito.KoreaInvestment(api_key=APP_KEY, api_secret=APP_SECRET)
# for company in COM.tickers.keys():
#     resp = broker.fetch_daily_price(company)
#     price = resp['output'][0]['stck_clpr']  ## 현재가
#     company_name=COM.tickers[company]
#     j = len(resp['output']) ## 총 자료의 길이

#     ### 종목의 고가를 hprice 리스트에 저장
#     hprice = []
#     for i in range(0, j):
#         hprice.append(resp['output'][i]['stck_hgpr'])

#     hprice.sort()   ## hprice 크기 순 정렬
#     hgpr1 = hprice[-1]    ## 최고가
#     hgpr2 = hprice[-2]    ## 2번째 최고가

#     target = int(hgpr1) * float(percent)

#     differnce = int(hgpr1) - int(hgpr2)
#     if differnce < diff_val:
#         if hgpr1 > price:
#             if (float(target)-int(price) < 0):  ##현재가가 최고가의 일정 범위 이내
#                 print("%s 종목 현재가 : %s , 최고가 : %s , 최고값 간 차이 : %s" % (company_name,price,hgpr1,differnce))
    





# df = pd.DataFrame(resp['output'])
# dt = pd.to_datetime(df['stck_bsop_date'], format="%Y%m%d")
# df.set_index(dt, inplace=True)
# df = df[['stck_oprc', 'stck_hgpr', 'stck_lwpr', 'stck_clpr']]
# df.columns = ['open', 'high', 'low', 'close']
# df.index.name = "date"
#print(df)


# print(resp['output'][0]['stck_bsop_date']) ## 특정 종목정보 날짜 0 1 2 3 4 ...
# print(resp['output'][0]['stck_oprc']) ## 특정 종목의 시가
# print(resp['output'][0]['stck_hgpr']) ## 특정 종목의 고가
# print(resp['output'][0]['stck_lwpr']) ## 특정 종목의 저가
# print(resp['output'][0]['stck_clpr']) ## 특정 종목의 종가
#print(resp['output'])



#pprint.pprint(resp)