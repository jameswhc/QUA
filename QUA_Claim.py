# coding: utf-8
import os,sys,re
import pandas as PD

from datetime import datetime,timedelta
from configparser import ConfigParser
from MyPack import *

def __main__():
    ConfigFile = sys.argv[1] if len(sys.argv) > 1 else (os.path.dirname(sys.argv[0])+'\\QUA_Classify.ini')
    myCrypt = MyCryp()
    Config = ConfigParser(allow_no_value=True)
    Config.optionxform = str
    Config.read(ConfigFile,encoding='utf-8')
    saveto = Config['PATH']['saveto']
    quapath = Config['PATH']['quapath']
    isopath = Config['PATH']['isopath']
    if Config.getboolean('SFTP','encrypt'):
        un = myCrypt.decryp(Config['SFTP']['username'])
        pw = myCrypt.decryp(Config['SFTP']['password'])
        ip = myCrypt.decryp(Config['SFTP']['ip'])
    else:
        un = Config['SFTP']['username']
        pw = Config['SFTP']['password']
        ip = Config['SFTP']['ip']
    A = SFTP(un,pw,ip)

    t11 = datetime.now().strftime('%Y/%m/%d %H')
    if int(datetime.now().strftime('%H')) > 17 :
        t = datetime.now().strftime('%Y%m%d15')
        ta = datetime.now().strftime('%Y%m%d17')
    else: 
        t = datetime.now().strftime('%Y%m%d03')
        ta = datetime.now().strftime('%Y%m%d05')
    p = '^EFENCE_QUARANTINE_{}_[0-9]{}.csv$'.format(t,'{1,5}')
    p1 = '^EFENCE_QUARANTINE_{}_[0-9]{}.csv$'.format(ta,'{1,5}')
    p1QSearch = re.compile(p)
    p2QSearch = re.compile(p1)
    A.ChangeDir(quapath)
    def _search(_A):
        try :
            with  A.getFile (_A) as _qFile2 :
                if _qFile2 is not None: 
                    _sData = PD.read_csv(_qFile2,header = 0,dtype = str)
                    _key = [x for x in _sData.keys()]
                    return [int(_sData[x][0]) for x in _key]
                else:
                    return None
        except :
            raise Exception("Cannot find ISO total count file.")
    d1 = _search(p1QSearch)
    d2 = _search(p2QSearch)
    if (d1 is not None) and (d2 is not None):
        _delta = list(map(lambda x,y : str(x-y),d2,d1))
        _value = [t11]+_delta[2:7]+[str(d2[7])]
        _qgs = GSheet(Config['GSheet']['ID'],Config['GSheet']['auth_json'])
        _qgs.append('QUA_Claims!A1:G',{'values':[_value,]})
        #print (_value)

if __name__ == '__main__':
    __main__()