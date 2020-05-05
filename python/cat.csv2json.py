#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Version: v0.2.7
Usage: python cat.csv2json --with-header True csv_file
Author:
Purpose: command line csv to json realtime converter
Comments:
"""
#==customized environment modules==
#==built-in modules==
import argparse
import csv
import re
import json
import traceback
import signal
import logging
import cProfile
#set original encoding to utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#==customized installed modules==
#==customized build modules==

#==Global variables

#---------------------------------------------------------------------
#==customized subroutines==
def signal_handler(signal, frame):
    sys.exit(0)
def csv2json(csv_file,no_header,no_datatype,no_log,only_header):
    if not no_log:
        logging.basicConfig(level=logging.ERROR,
                            filename="/var/log/cat/cat.csv2json.log",
                            format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M'
                            )

        logger = logging.getLogger(__name__)
    #取得csv file handler
    try:
        f = open(csv_file,'rb')
        reader = csv.reader(f,delimiter=",",quotechar="\"")
    except:
        if not no_log:
            logging.error("csv file handler FAILED,csv_file:"+csv_file+",traceback:"+traceback.format_exc())
        raise

    #######處理headers###########
    try:
        if no_header:
            headers = []
            for idx, val in enumerate(reader.next()):
                headers.append('C'+str(idx))
            f.close()
            f = open(csv_file,'rb')
            reader = csv.reader(f,delimiter=",",quotechar="\"")
            pass
        else:
            #若csv file有帶headers, 則將header抽出, 後續做為json的key
            headers = reader.next()
            #去除header欄位名稱中頭尾的空白換行等等
            headers = [w.strip() for w in headers]
            #將header欄位名稱中不想要看到的字元替換
            headers = [re.sub(r'\[.+\]','',w) for w in headers]
            for ch in [" ","]",")","}"]:
                headers = [w.replace(ch,"") for w in headers]
            for ch in ["[","(","{","-"]:
                headers = [w.replace(ch,"_") for w in headers]
            #把每個欄位名稱的最前頭加上#,方便kibana使用時會出現在最上端
            headers = ["#"+w for w in headers]
    except:
        if not no_log:
            logging.error("HEADERS FAILED,csv_file:"+csv_file+",traceback:"+traceback.format_exc())
        raise

    if only_header:
        print headers
        sys.exit(0)

    #######包裝json##########
    for row in reader:
        #清空dict
        try:
            column = {}
            for h,v in zip(headers, row):
                #如果非空白值才做(不然產出的json會過大)
                if v != "":
                    v=v.strip()
                    if no_datatype:
                        #如果no_datatype被設定,則原字串不做處理就放進field
                        column[h] = v
                    else:
                        #若資料為0開頭,則辨識為字串
                        if re.match('^0[A-Za-z0-9][A-Za-z0-9\.]*',v):
                            column[h] = v
                        #帶有或未帶有正負號的浮點數
                        elif re.match('^[+|-]{0,1}\d+\.\d+$', v):
                            column[h] = float(v)
                        #帶有或未帶有正負號的整數
                        elif re.match('^[+|-]{0,1}\d+$', v):
                            column[h] = long(v)
                        #若開頭即為小數點,則為浮點數
                        elif re.match('^\.\d+$',v):
                            column[h] = float(v)
                        #若以上皆不符,則視為字串
                        else:
                            column[h] = v
            #json.dumps為string去除meta符號(比如12345L, u'12345'等等)
            print json.dumps(column)
        except:
            if not no_log:
                logging.error("ROW FAILED,csv_file:"+csv_file+",traceback:"+traceback.format_exc())

def main():
    #抓SIGINT,這樣ctrl+c就不會噴traceback
    signal.signal(signal.SIGINT, signal_handler)
    #定義指令開關
    parser = argparse.ArgumentParser(description='realtime cat csv file as json format')
    parser.add_argument('-v','--version', action="version",
                        version="%(prog)s Python Version v0.2.7")
    parser.add_argument('csv_file', metavar='csv_file', type=str, nargs=1,
                        help='name of csv file')
    parser.add_argument('--no-header', dest="NO_HEADER",action="store_true",
                        help="set this flag if the input csv file does NOT contains headers")
    parser.add_argument('--no-datatype', dest="NO_DATATYPE",action="store_true",
                        help="set this flag if you do NOT want to auto set datatype of each column fields")
    parser.add_argument('--no-log', dest="NO_LOG",action="store_true",
                        help="set this flag if you do NOT want log")
    parser.add_argument('--only-header', dest="ONLY_HEADER",action="store_true",
                        help="set this flag if you do only want to see headers")
    args = parser.parse_args()
    #都ok就叫csv2json出來跑
    if args.csv_file is not None:
        csv2json(csv_file=args.csv_file[0],no_header=args.NO_HEADER,no_datatype=args.NO_DATATYPE,
                 no_log=args.NO_LOG,only_header=args.ONLY_HEADER)
    pass

#---------------------------------------------------------------------
#==main==
if __name__ == "__main__":
    main()
