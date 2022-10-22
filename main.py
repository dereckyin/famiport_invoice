from operator import le
import re
from flask import Flask
from flask import request
from flask import Response
import xmltodict
from dict2xml import dict2xml
import traceback

from flask_cors import CORS
import linecache
import logging
import os
import sys
from datetime import date, timedelta, datetime
import json
from public.yahoo_api_utils import YahooApiUtils as yh_utils
from public.yahoo_api_dao import YahooApiDao
from public.custom_exceptions import *
from public.project_variables import *

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from base64 import b64decode
from base64 import b64encode
# from Crypto.Signature import PKCS1_v1_5
from Crypto.Cipher import PKCS1_v1_5
import hashlib

# from flask_sqlalchemy import SQLAlchemy


# basedir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# models
# class FamiRequest(db.Model):
#     __tablename__ = 'famiport_request'
#     id = db.Column(db.Integer, primary_key=True)
#     request_id = db.Column(db.String(255), unique=True)
#     request_date = db.Column(db.DateTime, default=datetime.utcnow)
#     request_status = db.Column(db.String(255))
#     request_type = db.Column(db.String(255))

#     def __init__(self, request_id, request_status, request_type):
#         self.request_id = request_id
#         self.request_status = request_status
#         self.request_type = request_type

#     def __repr__(self):
#         return '<FamiRequest %r>' % self.request_id


class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

# @app.route('/.well-known/pki-validation/24DCBFEEF4F55D73256C199D2F94C9A6.txt')
# def validation():
#     return """02FE21B891F4BC16599FC0925F4E438A3C1CEC4CF7A545B2F7B4E362043000BF
# comodoca.com
# a6400d0847a229a"""

def obj_dict(obj):
    return obj.__dict__

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    logging.error('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def settingLog():
    # 設定
    datestr = datetime.today().strftime('%Y%m%d')
    if not os.path.exists("log/" + datestr):
        os.makedirs("log/" + datestr)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(lineno)s %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S',
                        handlers = [logging.FileHandler('log/' + datestr + '/famiport.log', 'a', 'utf-8'),])

def divide_chunks(me, n): 
    for i in range(0, len(me), n):  
        ret = Object()
        product = me[i:i + n] 
        ret = product
        yield ret

def get_tw_year(sValue):
    # year - 1911
    year = int(sValue[0:4]) - 1911
    # padding 0 
    return str(year).zfill(3)

def get_start_month(sValue):
    month = sValue[4:6]
    if month == '01' or month == '02': 
        return '01'
    elif month == '03' or month == '04':
        return '03'
    elif month == '05' or month == '06':
        return '05'
    elif month == '07' or month == '08':
        return '07'
    elif month == '09' or month == '10':
        return '09'
    elif month == '11' or month == '12':
        return '11'

def get_end_month(sValue):
    month = sValue[4:6]
    if month == '01' or month == '02': 
        return '02'
    elif month == '03' or month == '04':
        return '04'
    elif month == '05' or month == '06':
        return '06'
    elif month == '07' or month == '08':
        return '07'
    elif month == '09' or month == '10':
        return '10'
    elif month == '11' or month == '12':
        return '12'

def get_prize_type(prize):
    if prize == '1': 
        return '頭獎'
    elif prize == '2':
        return '二獎'
    elif prize == '3':
        return '三獎'
    elif prize == '4':
        return '四獎'
    elif prize == '5':
        return '五獎'
    elif prize == '6':
        return '六獎'
    elif prize == 'A':
        return '特別獎'
    elif prize == '0':
        return '特獎'

def get_prize_period_start(sValue):
    year = int(sValue[0:4]) - 1911
    month = sValue[4:6]
    if month == '01' or month == '02': 
        return str(year).zfill(3) + '0406'
    elif month == '03' or month == '04':
        return str(year).zfill(3) + '0606'
    elif month == '05' or month == '06':
        return str(year).zfill(3) + '0806'
    elif month == '07' or month == '08':
        return str(year).zfill(3) + '1006'
    elif month == '09' or month == '10':
        return str(year).zfill(3) + '1206'
    elif month == '11' or month == '12':
        return str(year+1).zfill(3) + '0206'

def get_prize_period_end(sValue):
    year = int(sValue[0:4]) - 1911
    month = sValue[4:6]
    if month == '01' or month == '02': 
        return str(year).zfill(3) + '0705'
    elif month == '03' or month == '04':
        return str(year).zfill(3) + '0905'
    elif month == '05' or month == '06':
        return str(year).zfill(3) + '1105'
    elif month == '07' or month == '08':
        return str(year+1).zfill(3) + '0105'
    elif month == '09' or month == '10':
        return str(year+1).zfill(3) + '0305'
    elif month == '11' or month == '12':
        return str(year+1).zfill(3) + '0505'


key = "7pou9h3raef45tr5l0u4rkk6hyu8oag2" # 測試環境
# key = "95yt4hpoicj98ieuoj7u4mo41hmu2h5m" # 正式環境

def pkcs7padding(data, block_size=16):
  if type(data) != bytearray and type(data) != bytes:
    raise TypeError("Only support bytearray/bytes !")
  pl = block_size - (len(data) % block_size)
  return data + bytearray([pl for i in range(pl)])

def pkcs5padding(data):
    return pkcs7padding(data, 8)

def encrypt(inv_no, random):
    encrypted = ""
    data = inv_no + random
    try:
        # md5 key as iv
        iv = hashlib.md5(key.encode('ascii')).digest()
        cipher = AES.new(key.encode("ascii"), AES.MODE_CBC, iv=iv)

        encrypted = cipher.encrypt(pkcs7padding(data.encode("utf-8")))
        encrypted = b64encode(encrypted)

    except Exception as e:
            error, = e.args
          
            logging.error(error)
            msg_log = "get_invoice_data FAIL : %s" % (error) 
            logging.info(msg_log)
    return encrypted

def get_invoice_data_01(VALIDATE_01, VALIDATE_02, VALIDATE_03):
    INV_DATA = []

    today = date.today()
    INV_TODAY = get_tw_year(today.strftime('%Y')) + today.strftime('%m%d')

    with YahooApiDao() as master_dao:
        master_dao.get_inv_award_mail_ctn_main(VALIDATE_01, VALIDATE_02, VALIDATE_03)

        try:
            row = master_dao.fetchall()

            if len(row) == 0:
                return INV_DATA

            n = 100
        
            chunks = list(divide_chunks(row, n)) 
            for chunk in chunks:
                for item in chunk:

                    invoice = Object()
                    invoice.EINVOICE_01 = item['INV_NO'][0:2]
                    invoice.EINVOICE_02 = item['INV_NO'][2:]
                    invoice.PRZ_PERIOD_01 = get_tw_year(item['INV_AD_DATE'])
                    invoice.PRZ_PERIOD_02 = get_start_month(item['INV_AD_DATE'])
                    invoice.PRZ_PERIOD_03 = get_end_month(item['INV_AD_DATE'])
                    invoice.PRZ_TYPE = "<![CDATA[" + get_prize_type(item['PRIZE_TYPE']) + "]]>"
                    invoice.PRZ_AMT = item['PRIZE_AMT']
                    invoice.PURCHASE_AMT = item['TTL_AMOUNT']
                    invoice.IS_PRINT = item['IS_PRINT']

                    prize_start = get_prize_period_start(item['INV_AD_DATE'])
                    prize_end = get_prize_period_end(item['INV_AD_DATE'])

                    # 列印期限中
                    if INV_TODAY >= prize_start and INV_TODAY <= prize_end:
                        INV_DATA.append(invoice)

        except Exception as e:
            error, = e.args
          
            logging.error(error)
            msg_log = "get_invoice_data FAIL : %s" % (error) 
            logging.info(msg_log)

    return INV_DATA


def get_invoice_data_02(EINVOICE_01, EINVOICE_02, PRINT_TIME, TRAN_NO):
    INV_DATA = []

    with YahooApiDao() as master_dao:
        master_dao.get_inv_detail(EINVOICE_01, EINVOICE_02, PRINT_TIME)

        try:
            row = master_dao.fetchall()

            if len(row) == 0:
                return INV_DATA

            for item in row:
                invoice = Object()

                if item['IS_PRINT'] == "Y":
                    invoice.IS_CAN_PRINT = 'Y' if item['IS_PRINT']  == 'N' else 'N'
                else:
                    invoice.IS_CAN_PRINT = 'Y' if item['IS_PRINT']  == 'N' else 'N'
                    invoice.DATA_1_01 = item['INV_NO'][0:2]
                    invoice.DATA_1_02 = item['INV_NO'][2:]
                    invoice.DATA_2 = "<![CDATA[" + "學思行股份有限公司" + "]]>"
                    invoice.DATA_3 = "24342999"
                    invoice.DATA_4 = ""
                    invoice.DATA_5 = "<![CDATA[" + "讀冊會員載具" + "]]>"
                    invoice.DATA_6 = "EG0637"
                    invoice.DATA_7 = item['INV_DT']
                    invoice.DATA_8 = item['TTL_AMOUNT']
                    invoice.DATA_9 = item['INV_RN']
                    invoice.DATA_10 = ""
                    invoice.DATA_11 = item['INV_ROC_DATE'][0:5]
                    invoice.DATA_12 = ""
                    invoice.DATA_13_01 = get_tw_year(item['INV_AD_DATE'])
                    invoice.DATA_13_02 = get_start_month(item['INV_AD_DATE'])
                    invoice.DATA_13_03 = get_end_month(item['INV_AD_DATE'])

                    prize_start = get_prize_period_start(item['INV_AD_DATE'])
                    prize_end = get_prize_period_end(item['INV_AD_DATE'])

                    invoice.DATA_14 = "<![CDATA[" + prize_start[0:3] + "年" + prize_start[3:5] + "月" + prize_start[5:7] + "日" + "至" + prize_end[0:3] + "年" + prize_end[3:5] + "月" + prize_end[5:7] + "日" + "]]>"
                    invoice.DATA_15 = item['PRIZE_AMT']
                    invoice.DATA_16 = PRINT_TIME
                    invoice.DATA_17 = TRAN_NO

                    aes = encrypt(item['INV_NO'], item['INV_RN']).decode('UTF-8')
                    amount = format(int(item['TTL_AMOUNT']), '08x')
                    cnt = str(item['CNT'])
                    invoice.DATA_18 = "<![CDATA[" + item['INV_NO'] + item['INV_ROC_DATE'] + item['INV_RN'] + "00000000" + amount + "00000000" + "24342999" + aes + "**********:" + cnt + ":" + cnt + ":1" + ":]]>"

                    invoice.DATA_19 = ""
                    invoice.DATA_20 = ""
                    invoice.PRINTWEB = ""
                

            INV_DATA.append(invoice)

        except Exception as e:
            error, = e.args
          
            logging.error(error)
            msg_log = "update_invoice_data FAIL : %s" % (error) 
            logging.info(msg_log)

    return INV_DATA


def get_invoice_data_03(INV_NO, HG_TRAN_NO):
    INV_DATA = []

    with YahooApiDao() as master_dao:
        master_dao.get_inv_award_mail_ctn_main_tran_no(INV_NO, HG_TRAN_NO)

        try:
            row = master_dao.fetchall()

            if len(row) == 0:
                return INV_DATA

            n = 100
        
            chunks = list(divide_chunks(row, n)) 
            for chunk in chunks:
                for item in chunk:

                    invoice = Object()
                    invoice.EINVOICE_01 = item['INV_NO'][0:2]
                    invoice.EINVOICE_02 = item['INV_NO'][2:]
                    invoice.PRZ_PERIOD_01 = get_tw_year(item['INV_AD_DATE'])
                    invoice.PRZ_PERIOD_02 = get_start_month(item['INV_AD_DATE'])
                    invoice.PRZ_PERIOD_03 = get_end_month(item['INV_AD_DATE'])
                    invoice.PRZ_TYPE = "<![CDATA[" + get_prize_type(item['PRIZE_TYPE']) + "]]>"
                    invoice.PRZ_AMT = item['PRIZE_AMT']
                    invoice.PURCHASE_AMT = item['TTL_AMOUNT']
                    invoice.IS_PRINT = item['IS_PRINT']
                    invoice.INV_PNT_DT = item['INV_PNT_DT']


                    INV_DATA.append(invoice)

        except Exception as e:
            error, = e.args
          
            logging.error(error)
            msg_log = "get_invoice_data FAIL : %s" % (error) 
            logging.info(msg_log)

    return INV_DATA

def update_invoice_as_printed(EINVOICE_01, EINVOICE_02, TRAN_NO, PRINT_TIME):
    with YahooApiDao() as master_dao:
        master_dao.update_inv_award_mail_ctn_main(EINVOICE_01 + EINVOICE_02, TRAN_NO, PRINT_TIME)
        master_dao.commit_changes()

def revise_invoice_as_printed(EINVOICE_01, EINVOICE_02, TRAN_NO):
    with YahooApiDao() as master_dao:
        master_dao.revise_inv_award_mail_ctn_main(EINVOICE_01 + EINVOICE_02, TRAN_NO)
        master_dao.commit_changes()

# curl -H "Content-Type: application/x-www-form-urlencoded; charset=big5" -X POST -d "PRZ_001_01=<?xml version=\"1.0\" encoding=\"big5\"?><SEND_DATA><TRAN_NO>18C00000052</TRAN_NO><TEN_CODE>009979</TEN_CODE><VALIDATE_CNT>3</VALIDATE_CNT><VALIDATE_01><![CDATA[AB12345678]]></VALIDATE_01><VALIDATE_02><![CDATA[ABC]]></VALIDATE_02><VALIDATE_03><![CDATA[DEF]]></VALIDATE_03><VALIDATE_04></VALIDATE_04><VALIDATE_05></VALIDATE_05><VALIDATE_06></VALIDATE_06><VALIDATE_07></VALIDATE_07><VALIDATE_08></VALIDATE_08><VALIDATE_09></VALIDATE_09><VALIDATE_10></VALIDATE_10></SEND_DATA>" https://service.taaze.tw/famiport/prz_001
# curl -H "Content-Type: application/x-www-form-urlencoded; charset=big5" -X POST -d "PRZ_001_01=<?xml version=\"1.0\" encoding=\"big5\"?><SEND_DATA><TRAN_NO>18C00000052</TRAN_NO><TEN_CODE>009979</TEN_CODE><VALIDATE_CNT>3</VALIDATE_CNT><VALIDATE_01><![CDATA[WP23898321]]></VALIDATE_01><VALIDATE_02><![CDATA[2308]]></VALIDATE_02><VALIDATE_03><![CDATA[DEF]]></VALIDATE_03><VALIDATE_04></VALIDATE_04><VALIDATE_05></VALIDATE_05><VALIDATE_06></VALIDATE_06><VALIDATE_07></VALIDATE_07><VALIDATE_08></VALIDATE_08><VALIDATE_09></VALIDATE_09><VALIDATE_10></VALIDATE_10></SEND_DATA>" http://127.0.0.1:8080/famiport/prz_001
@app.route('/famiport/prz_001', methods=['POST'])
def famiport_001():
    settingLog()

    # xml = request.get_data()
    xml = request.form.get('PRZ_001_01')
    logging.info(xml)

    try:
        content = dict(xmltodict.parse(xml, encoding='utf-8'))
        TRAN_NO = content['SEND_DATA']['TRAN_NO']
        TEN_CODE = content['SEND_DATA']['TEN_CODE']
        VALIDATE_CNT = content['SEND_DATA']['VALIDATE_CNT']
        VALIDATE_01 = content['SEND_DATA']['VALIDATE_01']
        VALIDATE_02 = content['SEND_DATA']['VALIDATE_02']
        VALIDATE_03 = content['SEND_DATA']['VALIDATE_03']

        RTN_DATA = Object()

        INV_DATA = get_invoice_data_01(VALIDATE_01, VALIDATE_02, VALIDATE_03)

        RTN_DATA.TRAN_NO = TRAN_NO
        RTN_DATA.TEN_CODE = TEN_CODE
        RTN_DATA.STATUS_CODE = "0000"
        RTN_DATA.STATUS_DESC = "<![CDATA[成功]]>"
        RTN_DATA.RTN_CNT = len(INV_DATA)

        RTN_DATA.INV_DATA = INV_DATA

        rtn_json = json.dumps(RTN_DATA, default=obj_dict)

        obj = json.loads(rtn_json)

        data = dict2xml(obj, wrap ='RTN_DATA', indent ="   ")

        data = data.replace('&lt;', '<').replace('&gt;', '>')

        logging.info(data)

        return Response("<?xml version=\"1.0\" encoding=\"big5\"?>\n" + data, mimetype='text/xml')
    except Exception as e:
        error, = e.args
        logging.error(error)
        return Response("<?xml version=\"1.0\" encoding=\"big5\"?><RTN_DATA><STATUS_CODE>9999</STATUS_CODE><STATUS_DESC><![CDATA[失敗:%s]]></STATUS_DESC><RTN_CNT>0</RTN_CNT></RTN_DATA>" % (error), mimetype='text/xml')
        
        
# curl -H "Content-Type: application/x-www-form-urlencoded; charset=big5" -X POST -d "PRZ_002_01=<?xml version=\"1.0\" encoding=\"big5\"?><SEND_DATA><TRAN_NO>18C00000052</TRAN_NO><TEN_CODE>009979</TEN_CODE><PRINT_TIME>20191209130201</PRINT_TIME><INV_DATA><EINVOICE_01>XC</EINVOICE_01><EINVOICE_02>76945226</EINVOICE_02></INV_DATA><INV_DATA><EINVOICE_01>XC</EINVOICE_01><EINVOICE_02>76945227</EINVOICE_02></INV_DATA></SEND_DATA>" https://service.taaze.tw/famiport/prz_002
# curl -H "Content-Type: application/x-www-form-urlencoded; charset=big5" -X POST -d "PRZ_002_01=<?xml version=\"1.0\" encoding=\"big5\"?><SEND_DATA><TRAN_NO>18C00000052</TRAN_NO><TEN_CODE>009979</TEN_CODE><PRINT_TIME>20191209130201</PRINT_TIME><INV_DATA><EINVOICE_01>LW</EINVOICE_01><EINVOICE_02>47312903</EINVOICE_02></INV_DATA><INV_DATA><EINVOICE_01>XC</EINVOICE_01><EINVOICE_02>76945227</EINVOICE_02></INV_DATA></SEND_DATA>" http://127.0.0.1:8080/famiport/prz_002
@app.route('/famiport/prz_002', methods=['POST'])
def famiport_002():
    settingLog()
    # xml = request.get_data()
    xml = request.form.get('PRZ_002_01')
    logging.info(xml)

    INV_DETAIL = []

    try:
        content = dict(xmltodict.parse(xml, encoding='utf-8'))
        TRAN_NO = content['SEND_DATA']['TRAN_NO']
        TEN_CODE = content['SEND_DATA']['TEN_CODE']
        PRINT_TIME = content['SEND_DATA']['PRINT_TIME']
        INV_DATA = content['SEND_DATA']['INV_DATA']
       
        RTN_DATA = Object()

        #loop each INV_DATA
        for inv in INV_DATA:
            EINVOICE_01 = inv['EINVOICE_01']
            EINVOICE_02 = inv['EINVOICE_02']

            TEMP_INV_DETAIL = get_invoice_data_02(EINVOICE_01, EINVOICE_02, PRINT_TIME, TRAN_NO)
            
            if len(TEMP_INV_DETAIL) > 0:
                INV_DETAIL.append(TEMP_INV_DETAIL)
                update_invoice_as_printed(EINVOICE_01, EINVOICE_02, TRAN_NO, PRINT_TIME)

  
        RTN_DATA.TRAN_NO = TRAN_NO
        RTN_DATA.TEN_CODE = TEN_CODE
        RTN_DATA.STATUS_CODE = "0000"
        RTN_DATA.STATUS_DESC = "<![CDATA[成功]]>"
        RTN_DATA.RTN_CNT = len(INV_DETAIL)

        RTN_DATA.INV_DATA = INV_DETAIL

        rtn_json = json.dumps(RTN_DATA, default=obj_dict)

        obj = json.loads(rtn_json)

        data = dict2xml(obj, wrap ='RTN_DATA', indent ="   ")

        data = data.replace('&lt;', '<').replace('&gt;', '>')

        logging.info(data)

        return Response("<?xml version=\"1.0\" encoding=\"big5\"?>\n" + data, mimetype='text/xml')
    except Exception as e:
        error, = e.args
        logging.error(error)
        return Response("<?xml version=\"1.0\" encoding=\"big5\"?><RTN_DATA><STATUS_CODE>9999</STATUS_CODE><STATUS_DESC><![CDATA[失敗:%s]]></STATUS_DESC><RTN_CNT>0</RTN_CNT></RTN_DATA>" % (error), mimetype='text/xml')
        

# curl -H "Content-Type: application/x-www-form-urlencoded; charset=big5" -X POST -d "PRZ_003_01=<?xml version=\"1.0\" encoding=\"big5\"?><SEND_DATA><TRAN_NO>18C00000052</TRAN_NO><TEN_CODE>009979</TEN_CODE><TRANS_DEP>FM</TRANS_DEP><EINVOICE_01>LW</EINVOICE_01><EINVOICE_02>47312903</EINVOICE_02><HG_TRAN_NO>18C00000052</HG_TRAN_NO></SEND_DATA>" https://service.taaze.tw/famiport/prz_003
# curl -H "Content-Type: application/x-www-form-urlencoded; charset=big5" -X POST -d "PRZ_003_01=<?xml version=\"1.0\" encoding=\"big5\"?><SEND_DATA><TRAN_NO>18C00000052</TRAN_NO><TEN_CODE>009979</TEN_CODE><TRANS_DEP>FM</TRANS_DEP><EINVOICE_01>LW</EINVOICE_01><EINVOICE_02>47312903</EINVOICE_02><HG_TRAN_NO>18C00000052</HG_TRAN_NO></SEND_DATA>" http://127.0.0.1:8080/famiport/prz_003
@app.route('/famiport/prz_003', methods=['POST'])
def famiport_003():
    settingLog()

    # xml = request.get_data()
    xml = request.form.get('PRZ_003_01')
    logging.info(xml)

    try:
        content = dict(xmltodict.parse(xml, encoding='utf-8'))
        TRAN_NO = content['SEND_DATA']['TRAN_NO']
        TEN_CODE = content['SEND_DATA']['TEN_CODE']
        TRANS_DEP = content['SEND_DATA']['TRANS_DEP']
        EINVOICE_01 = content['SEND_DATA']['EINVOICE_01']
        EINVOICE_02 = content['SEND_DATA']['EINVOICE_02']
        HG_TRAN_NO = content['SEND_DATA']['HG_TRAN_NO']

        RTN_DATA = Object()

        RTN_DATA.TRAN_NO = TRAN_NO
        RTN_DATA.TEN_CODE = TEN_CODE
        RTN_DATA.TRANS_DEP = TRANS_DEP
        RTN_DATA.EINVOICE_01 = EINVOICE_01
        RTN_DATA.EINVOICE_02 = EINVOICE_02
        RTN_DATA.HG_TRAN_NO = HG_TRAN_NO

        RTN_DATA.RESULT = "N"

        TEMP_INV_DETAIL = get_invoice_data_03(EINVOICE_01 + EINVOICE_02, HG_TRAN_NO)
        if len(TEMP_INV_DETAIL) > 0:
            RTN_DATA.PRINTTIME =  TEMP_INV_DETAIL[0].INV_PNT_DT
            RTN_DATA.RESULT = "Y"
            revise_invoice_as_printed(EINVOICE_01, EINVOICE_02, TRAN_NO)

        
        rtn_json = json.dumps(RTN_DATA, default=obj_dict)

        obj = json.loads(rtn_json)

        data = dict2xml(obj, wrap ='RTN_DATA', indent ="   ")

        data = data.replace('&lt;', '<').replace('&gt;', '>')

        logging.info(data)

        return Response("<?xml version=\"1.0\" encoding=\"big5\"?>\n" + data, mimetype='text/xml')
    except Exception as e:
        error, = e.args
        logging.error(error)
        return Response("<?xml version=\"1.0\" encoding=\"big5\"?><RTN_DATA><STATUS_CODE>9999</STATUS_CODE><STATUS_DESC><![CDATA[失敗:%s]]></STATUS_DESC><RTN_CNT>0</RTN_CNT></RTN_DATA>" % (error), mimetype='text/xml')
        
# curl -H "Content-Type: application/x-www-form-urlencoded; charset=big5" -X POST -d "PRZ_001_01=<?xml version=\"1.0\" encoding=\"big5\"?><SEND_DATA><TRAN_NO>18C00000052</TRAN_NO><TEN_CODE>009979</TEN_CODE><VALIDATE_CNT>3</VALIDATE_CNT><VALIDATE_01><![CDATA[AB12345678]]></VALIDATE_01><VALIDATE_02><![CDATA[ABC]]></VALIDATE_02><VALIDATE_03><![CDATA[DEF]]></VALIDATE_03><VALIDATE_04></VALIDATE_04><VALIDATE_05></VALIDATE_05><VALIDATE_06></VALIDATE_06><VALIDATE_07></VALIDATE_07><VALIDATE_08></VALIDATE_08><VALIDATE_09></VALIDATE_09><VALIDATE_10></VALIDATE_10></SEND_DATA>" https://service.taaze.tw/famiport/prz_001
# curl -H "Content-Type: application/x-www-form-urlencoded; charset=big5" -X POST -d "PRZ_001_01=<?xml version=\"1.0\" encoding=\"big5\"?><SEND_DATA><TRAN_NO>18C00000052</TRAN_NO><TEN_CODE>009979</TEN_CODE><VALIDATE_CNT>3</VALIDATE_CNT><VALIDATE_01><![CDATA[WP23898321]]></VALIDATE_01><VALIDATE_02><![CDATA[2308]]></VALIDATE_02><VALIDATE_03><![CDATA[DEF]]></VALIDATE_03><VALIDATE_04></VALIDATE_04><VALIDATE_05></VALIDATE_05><VALIDATE_06></VALIDATE_06><VALIDATE_07></VALIDATE_07><VALIDATE_08></VALIDATE_08><VALIDATE_09></VALIDATE_09><VALIDATE_10></VALIDATE_10></SEND_DATA>" http://127.0.0.1:8080/famiport/prz_001
@app.route('/famiport/prz_001/test', methods=['POST'])
def famiport_001_test():
    settingLog()

    # xml = request.get_data()
    xml = request.form.get('PRZ_001_01')
    logging.info(xml)

    try:
        content = dict(xmltodict.parse(xml, encoding='utf-8'))
        TRAN_NO = content['SEND_DATA']['TRAN_NO']
        TEN_CODE = content['SEND_DATA']['TEN_CODE']
        VALIDATE_CNT = content['SEND_DATA']['VALIDATE_CNT']
        VALIDATE_01 = content['SEND_DATA']['VALIDATE_01']
        VALIDATE_02 = content['SEND_DATA']['VALIDATE_02']
        VALIDATE_03 = content['SEND_DATA']['VALIDATE_03']

        RTN_DATA = Object()

        INV_DATA = get_invoice_data_01(VALIDATE_01, VALIDATE_02, VALIDATE_03)

        RTN_DATA.TRAN_NO = TRAN_NO
        RTN_DATA.TEN_CODE = TEN_CODE
        RTN_DATA.STATUS_CODE = "0000"
        RTN_DATA.STATUS_DESC = "<![CDATA[成功]]>"
        RTN_DATA.RTN_CNT = len(INV_DATA)

        RTN_DATA.INV_DATA = INV_DATA

        rtn_json = json.dumps(RTN_DATA, default=obj_dict)

        obj = json.loads(rtn_json)

        data = dict2xml(obj, wrap ='RTN_DATA', indent ="   ")

        data = data.replace('&lt;', '<').replace('&gt;', '>')

        logging.info(data)

        return Response("<?xml version=\"1.0\" encoding=\"big5\"?>\n" + data, mimetype='text/xml')
    except Exception as e:
        error, = e.args
        logging.error(error)
        return Response("<?xml version=\"1.0\" encoding=\"big5\"?><RTN_DATA><STATUS_CODE>9999</STATUS_CODE><STATUS_DESC><![CDATA[失敗:%s]]></STATUS_DESC><RTN_CNT>0</RTN_CNT></RTN_DATA>" % (error), mimetype='text/xml')
        
        
# curl -H "Content-Type: application/x-www-form-urlencoded; charset=big5" -X POST -d "PRZ_002_01=<?xml version=\"1.0\" encoding=\"big5\"?><SEND_DATA><TRAN_NO>18C00000052</TRAN_NO><TEN_CODE>009979</TEN_CODE><PRINT_TIME>20191209130201</PRINT_TIME><INV_DATA><EINVOICE_01>XC</EINVOICE_01><EINVOICE_02>76945226</EINVOICE_02></INV_DATA><INV_DATA><EINVOICE_01>XC</EINVOICE_01><EINVOICE_02>76945227</EINVOICE_02></INV_DATA></SEND_DATA>" https://service.taaze.tw/famiport/prz_002
# curl -H "Content-Type: application/x-www-form-urlencoded; charset=big5" -X POST -d "PRZ_002_01=<?xml version=\"1.0\" encoding=\"big5\"?><SEND_DATA><TRAN_NO>18C00000052</TRAN_NO><TEN_CODE>009979</TEN_CODE><PRINT_TIME>20191209130201</PRINT_TIME><INV_DATA><EINVOICE_01>LW</EINVOICE_01><EINVOICE_02>47312903</EINVOICE_02></INV_DATA><INV_DATA><EINVOICE_01>XC</EINVOICE_01><EINVOICE_02>76945227</EINVOICE_02></INV_DATA></SEND_DATA>" http://127.0.0.1:8080/famiport/prz_002
@app.route('/famiport/prz_002/test', methods=['POST'])
def famiport_002_test():
    settingLog()
    # xml = request.get_data()
    xml = request.form.get('PRZ_002_01')
    logging.info(xml)

    INV_DETAIL = []

    try:
        content = dict(xmltodict.parse(xml, encoding='utf-8'))
        TRAN_NO = content['SEND_DATA']['TRAN_NO']
        TEN_CODE = content['SEND_DATA']['TEN_CODE']
        PRINT_TIME = content['SEND_DATA']['PRINT_TIME']
        INV_DATA = content['SEND_DATA']['INV_DATA']
       
        RTN_DATA = Object()

        #loop each INV_DATA
        for inv in INV_DATA:
            EINVOICE_01 = inv['EINVOICE_01']
            EINVOICE_02 = inv['EINVOICE_02']

            TEMP_INV_DETAIL = get_invoice_data_02(EINVOICE_01, EINVOICE_02, PRINT_TIME, TRAN_NO)
            
            if len(TEMP_INV_DETAIL) > 0:
                INV_DETAIL.append(TEMP_INV_DETAIL)
                update_invoice_as_printed(EINVOICE_01, EINVOICE_02, TRAN_NO, PRINT_TIME)

  
        RTN_DATA.TRAN_NO = TRAN_NO
        RTN_DATA.TEN_CODE = TEN_CODE
        RTN_DATA.STATUS_CODE = "0000"
        RTN_DATA.STATUS_DESC = "<![CDATA[成功]]>"
        RTN_DATA.RTN_CNT = len(INV_DETAIL)

        RTN_DATA.INV_DATA = INV_DETAIL

        rtn_json = json.dumps(RTN_DATA, default=obj_dict)

        obj = json.loads(rtn_json)

        data = dict2xml(obj, wrap ='RTN_DATA', indent ="   ")

        data = data.replace('&lt;', '<').replace('&gt;', '>')

        logging.info(data)

        return Response("<?xml version=\"1.0\" encoding=\"big5\"?>\n" + data, mimetype='text/xml')
    except Exception as e:
        error, = e.args
        logging.error(error)
        return Response("<?xml version=\"1.0\" encoding=\"big5\"?><RTN_DATA><STATUS_CODE>9999</STATUS_CODE><STATUS_DESC><![CDATA[失敗:%s]]></STATUS_DESC><RTN_CNT>0</RTN_CNT></RTN_DATA>" % (error), mimetype='text/xml')
        

# curl -H "Content-Type: application/x-www-form-urlencoded; charset=big5" -X POST -d "PRZ_003_01=<?xml version=\"1.0\" encoding=\"big5\"?><SEND_DATA><TRAN_NO>18C00000052</TRAN_NO><TEN_CODE>009979</TEN_CODE><TRANS_DEP>FM</TRANS_DEP><EINVOICE_01>LW</EINVOICE_01><EINVOICE_02>47312903</EINVOICE_02><HG_TRAN_NO>18C00000052</HG_TRAN_NO></SEND_DATA>" https://service.taaze.tw/famiport/prz_003
# curl -H "Content-Type: application/x-www-form-urlencoded; charset=big5" -X POST -d "PRZ_003_01=<?xml version=\"1.0\" encoding=\"big5\"?><SEND_DATA><TRAN_NO>18C00000052</TRAN_NO><TEN_CODE>009979</TEN_CODE><TRANS_DEP>FM</TRANS_DEP><EINVOICE_01>LW</EINVOICE_01><EINVOICE_02>47312903</EINVOICE_02><HG_TRAN_NO>18C00000052</HG_TRAN_NO></SEND_DATA>" http://127.0.0.1:8080/famiport/prz_003
@app.route('/famiport/prz_003/test', methods=['POST'])
def famiport_003_test():
    settingLog()

    # xml = request.get_data()
    xml = request.form.get('PRZ_003_01')
    logging.info(xml)

    try:
        content = dict(xmltodict.parse(xml, encoding='utf-8'))
        TRAN_NO = content['SEND_DATA']['TRAN_NO']
        TEN_CODE = content['SEND_DATA']['TEN_CODE']
        TRANS_DEP = content['SEND_DATA']['TRANS_DEP']
        EINVOICE_01 = content['SEND_DATA']['EINVOICE_01']
        EINVOICE_02 = content['SEND_DATA']['EINVOICE_02']
        HG_TRAN_NO = content['SEND_DATA']['HG_TRAN_NO']

        RTN_DATA = Object()

        RTN_DATA.TRAN_NO = TRAN_NO
        RTN_DATA.TEN_CODE = TEN_CODE
        RTN_DATA.TRANS_DEP = TRANS_DEP
        RTN_DATA.EINVOICE_01 = EINVOICE_01
        RTN_DATA.EINVOICE_02 = EINVOICE_02
        RTN_DATA.HG_TRAN_NO = HG_TRAN_NO

        RTN_DATA.RESULT = "N"

        TEMP_INV_DETAIL = get_invoice_data_03(EINVOICE_01 + EINVOICE_02, HG_TRAN_NO)
        if len(TEMP_INV_DETAIL) > 0:
            RTN_DATA.PRINTTIME =  TEMP_INV_DETAIL[0].INV_PNT_DT
            RTN_DATA.RESULT = "Y"
            revise_invoice_as_printed(EINVOICE_01, EINVOICE_02, TRAN_NO)

        
        rtn_json = json.dumps(RTN_DATA, default=obj_dict)

        obj = json.loads(rtn_json)

        data = dict2xml(obj, wrap ='RTN_DATA', indent ="   ")

        data = data.replace('&lt;', '<').replace('&gt;', '>')

        logging.info(data)

        return Response("<?xml version=\"1.0\" encoding=\"big5\"?>\n" + data, mimetype='text/xml')
    except Exception as e:
        error, = e.args
        logging.error(error)
        return Response("<?xml version=\"1.0\" encoding=\"big5\"?><RTN_DATA><STATUS_CODE>9999</STATUS_CODE><STATUS_DESC><![CDATA[失敗:%s]]></STATUS_DESC><RTN_CNT>0</RTN_CNT></RTN_DATA>" % (error), mimetype='text/xml')
        

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080)
