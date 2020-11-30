# coding: utf-8
#from PyInstaller.utils.hooks import copy_metadata, collect_data_files

#datas = copy_metadata('google-api-python-client')
#datas += collect_data_files('googleapiclient.discovery')
#datas += collect_data_files('PyInstaller.utils.hooks')

import os, sys, pysftp, re, requests

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime,timedelta
from base64 import b64encode as ENCRYP
from base64 import b64decode as DECRYP

__all__ = ['MyCryp','SFTP','Telegram','GSheet']

class MyCryp ():
    def __init__ (self,key = ''):
        self.__key = ('' if key == '' else key)

    def encryp (self,key = ''):
        if (key != '' ):
            self.__key = key    
        return ENCRYP(ENCRYP(self.__key.encode())).decode()

    def decryp (self,dkey = ''):
        if dkey != '' :                
            self.__key = str(DECRYP(DECRYP(dkey.encode())).decode())
        return self.__key

class GSheet():
    def __init__(self,id,auth_json):
        self.GSheetsID = id
        path = os.path.dirname(sys.argv[0])+'\\'
        auth_json_path = path+auth_json
        #print (path)
        gss_scopes = [  'https://spreadsheets.google.com/feeds',
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive',
                        'https://www.googleapis.com/auth/drive.file']
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_json_path,gss_scopes)
        try :
            self.sheet = build('sheets','v4',credentials=self.credentials).spreadsheets()
        except :
            raise Exception("Cannot connect to Google spreadsheet.")

    def append(self,ranges = 'test!A1:B2', listvalues = {'values':[[1,2],[3,4],],}):
        ''' 參數:
                ranges : 選取範圍。格式:資料表名!起始格代碼:結束格代碼。例如: Sheet1!A1:D2
                listvalues : 數值列表。格式:{'values':[[A1~D1的值],[A2~D2的值],],}。例如: {'values':[[1,2,3,4],[5,6,7,8],],}
            回應:
                {
                    "spreadsheetId": string,
                    "tableRange": string,
                    "updates": {
                                object (UpdateValuesResponse)
                                }
                }
        '''
        req = self.sheet.values().append(spreadsheetId=self.GSheetsID,\
                                            range=ranges, valueInputOption='USER_ENTERED', body=listvalues)
        return req.execute()

    def update(self,ranges='test!A1:B2', listvalues={'values':[[1,2],[3,4],],}):
        req = self.sheet.values().update(spreadsheetId=self.GSheetsID,\
                                            range=ranges, valueInputOption='USER_ENTERED', body=listvalues)
        return req.execute()

    def batchupdate(self,rangevalues={  'value_input_option':'USER_ENTERED',
                                        'data':[{   'range':'test!A1:B2',
                                                    'majorDimension':"ROWS",
                                                    'values':[[1,2],[3,4],],}]}):
        req = self.sheet.values().batchUpdate(spreadsheetId=self.GSheetsID, body=rangevalues)
        return req.execute()

    def get(self,ranges='test!A1:B2',majorDimension='ROWS'):
        #ranges : 'sheetname!lefttop:rightbottom'
        #majorDimension : 'ROWS' | 'COLUMNS'
        req=self.sheet.values().get(spreadsheetId=self.GSheetsID,range=ranges, majorDimension=majorDimension)
        return req.execute()

class SFTP ():
    def __init__(self,un,pw,ip):
        #port = '22'
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        try :
            self.con = pysftp.Connection(ip, username=un, password=pw,cnopts=cnopts)
        except:
            raise Exception("Cannot connect to SFTP server.")
        
    def getFile(self,pName):
        FileList = self.con.listdir()
        fn = list(filter(pName.match,FileList))
        if fn == []:
            return None
        else:
            return self.con.open(fn[0])
        
    def putFile(self,localfile,remotefile=None):
        try :
            if remotefile is None :
                self.con.put(localfile)
            else :
                self.con.put(localfile,remotefile)
        except:
            pass

    def ChangeDir (self,pathname):
        self.con.chdir(pathname)

class Telegram():
    '''
    發送 Telegram 訊息
    token 是發行權杖
    chat_id 是要發送的聊天室id
    '''
    def __init__(self,token,chat_id = ''):
        self.token = token
        self.chat_id = chat_id
        
    @property 
    def token (self):
        return self.__token
    
    @token.setter
    def token (self,val):
        self.__token = val
        self.url = 'https://api.telegram.org/bot{}'.format(val)

    @property 
    def chat_id (self):
        return self.__chat_id
    @chat_id.setter
    def chat_id (self,val):
        self.__chat_id = val
        
    def getUpdate(self):
        url = self.url+'/getUpdates'
        a = requests.get(url).json()
        if a['ok']==True:
            results = a['result']
            d = []
            for r in results:
                id = r['message']['from']['id']
                dt = r['message']['date']
                txt = r['message']['text']
                if txt != '/help':
                    #print (str(int(time.time())))
                    d.append([dt,id,txt])
                    #self.chat_id = id
                    #self.notify(u'請輸入指令,謝謝')
            return d
        pass
    def notify(self, msg):
        '''
        發送 Telegram 訊息
        msg 是要發送的訊息
        return  : 400 網頁服務正常
                : 200 網頁服務異常
                : 1   程式錯誤
        '''
        url = self.url+'/sendMessage'
        payload = {'chat_id': '{0}'.format (self.chat_id) ,
                   'text'   : '{0}'.format (msg)}
        try :
            with requests.get(url, params = payload,timeout = 15) as r:
                res = r.status_code
            return res
        except :
            return 1
