# coding: utf-8
#from PyInstaller.utils.hooks import copy_metadata, collect_data_files

#datas = copy_metadata('google-api-python-client')
#datas += collect_data_files('googleapiclient.discovery')
#datas += collect_data_files('PyInstaller.utils.hooks')

import os, sys, re
import pandas as PD
from datetime import datetime,timedelta
from configparser import ConfigParser
from MyPack import *

_R = None
_notify = True
_tk = ''
_id = ''

def isinduty (A):
    p1 = '[0|1]?[0-9]/[0-3]?[0-9]集'
    rp = re.compile (p1)
    m = rp.search(A)
    if m is not None:
        lastday = m[0].split('集')[0]
        if datetime.strptime (lastday,'%m/%d') >= datetime.strptime(datetime.now().strftime('%m/%d'),'%m/%d'):
            return True
        else:
            return False
    else:
        return True

def fun_classify(qData):
    global _R
    #Others = qData.filter(items=['Seq','IdNo','OtherIdNo','Name','CellPhone','Addr','Remark','ErrorType'])
    Others = qData.copy()
    Others['classify'] = ''

    try :
        de2 = Others[(Others['TownCode'].str.contains('^[0-9]{4}$',na = False)
                            & Others['ErrorType'].str.contains('地址異常',na = False)
                            #& ~(Others['CellPhone']=='0900000000')
                            )]
        Others = Others[~(Others['TownCode'].str.contains('^[0-9]{4}$',na = False)
                            & Others['ErrorType'].str.contains('地址異常',na = False)
                            #& ~(Others['CellPhone']=='0900000000')
                            )]
        de2['classify'] = 'DC程式錯誤'
        de3 = Others[(Others['CellPhone'].isnull() | Others['Addr'].isnull())
                    &~(Others['Name'].str.contains('集中檢疫',na = False)|Others['Nationality'].str.contains('PH',na = False))]
        Others = Others[~((Others['CellPhone'].isnull() | Others['Addr'].isnull())
                    &~(Others['Name'].str.contains('集中檢疫',na = False)|Others['Nationality'].str.contains('PH',na = False)))]
        de3['classify'] = '部分確認'
        dataError = PD.concat([de2,de3])
        Z = dataError.copy()
    except :
        dataError = []

    #=================================================================
    try:
        de1 = Others[Others['Name'].str.contains('未入境',na = False)]
        Others = Others[~(Others['Name'].str.contains('未入境',na = False))]
        de1['classify'] = '未入境'
        Z = PD.concat([Z,de1]) 
    except:
        pass

    try :
        be_punish = Others[Others['Name'].str.contains(_R['be_punish'],na = False)]
        Others = Others[~Others['Name'].str.contains(_R['be_punish'],na = False)]
        be_punish['classify'] = '服刑中'
        Z = PD.concat([Z,be_punish])
    except :
        be_punish = []

    try :
        A2N = Others[Others['CellPhone'].isnull() |Others['Name'].str.contains('集中檢疫|特定.*檢疫',na = False)| Others['Remark'].str.contains('強制',na = False)]
        Others = Others[~(Others['CellPhone'].isnull() |Others['Name'].str.contains('集中檢疫|特定.*檢疫',na = False)| Others['Remark'].str.contains('強制',na = False))]
        for _A2 in A2N.iterrows():
            try :
                if isinduty(_A2[1]['Name']):
                    _A2[1]['classify'] = '集中檢疫'
                    A2N.update(_A2)
                elif _A2[1]['Name'].find('安置') != -1:
                    _A2[1]['classify'] = '集中檢疫'
                    A2N.update(_A2)
                elif _A2[1]['Name'].find('違規') != -1:
                    _A2[1]['classify'] = '集中檢疫'
                    A2N.update(_A2)
                elif _A2[1]['Name'].find('移工') != -1:
                    _A2[1]['classify'] = '集中檢疫'
                    A2N.update(_A2)
                elif _A2[1]['Name'].find('（集中檢疫）') != -1:
                    _A2[1]['classify'] = '集中檢疫'
                    A2N.update(_A2)
                elif _A2[1]['Name'].find('(集中檢疫)') != -1:
                    _A2[1]['classify'] = '集中檢疫'
                    A2N.update(_A2)
                elif _A2[1]['Nationality'] == 'PH':
                    _A2[1]['classify'] = '集中檢疫'
                    A2N.update(_A2)
                elif _A2[1]['Remark'].find('強制') != -1:
                    _A2[1]['classify'] = '集中檢疫'
                    A2N.update(_A2)
            except:
                continue
        A2 = A2N[A2N['classify'].str.contains('集中檢疫')]
        Others = PD.concat([Others,A2N[~A2N['classify'].str.contains('集中檢疫',na = False)]])
        Z = PD.concat([Z,A2])
    except :
        A2 = []

    try :
        A11 = Others[Others['Name'].str.contains(_R['to_ISO'],na = False)|Others['Remark'].str.contains(_R['to_ISO'],na = False)]
        Others = Others[~(Others['Name'].str.contains(_R['to_ISO'],na = False)|Others['Remark'].str.contains(_R['to_ISO'],na = False))]
        A11['classify'] = '轉隔離'
        Z = PD.concat([Z,A11])
    except :
        A11 = []

    try :
        outgoing = Others[Others['Remark'].str.contains('奔喪|外出|探病|就診|就醫|採檢|篩檢',na = False) & ~Others['Remark'].str.contains('入住|住院|治療|違規',na = False) & ~Others['Name'].str.contains('住院',na = False)]
        Others = Others[~(Others['Remark'].str.contains('奔喪|外出|探病|就診|就醫|採檢|篩檢',na = False) & ~Others['Remark'].str.contains('入住|住院|治療|違規',na = False)& ~Others['Name'].str.contains('住院',na = False))]
        outgoing['classify'] = '暫時解列'
        Z = PD.concat([Z,outgoing])
    except :
        outgoing = []

    try :
        in_hospital = Others[Others['Remark'].str.contains('醫院|病房|治療|入住|住院|開刀|手術',na = False) | Others['Name'].str.contains('住院|醫院',na = False)]
        Others = Others[~(Others['Remark'].str.contains('醫院|病房|治療|入住|住院|開刀|手術',na = False) | Others['Name'].str.contains('住院|醫院',na = False))]
        in_hospital['classify'] = '住院中'
        Z = PD.concat([Z,in_hospital])
    except :
        outgoing = []
        in_hospital = []

    try:
        foreign_Student = Others[(Others['TownCode'].str.contains('^[0-9]{4}$',na = False))]
        Others = Others[~(Others['TownCode'].str.contains('^[0-9]{4}$',na = False))]
        foreign_Student['classify'] = '外籍學生'
        Z = PD.concat([Z,foreign_Student])
    except:
        foreign_Student = []

    try :
        D1 = Others[Others['Remark'].str.contains('船上聯絡人|籍、船員|漁工',na = False) | Others['Addr'].str.contains('原船檢疫|船號|船員',na = False)]
        onboard_native = D1[D1['IdNo'].str.contains('[A-Z][1|2][0-9]{8}',na = False)]
        onboard_aboard = D1[~D1['IdNo'].str.contains('[A-Z][1|2][0-9]{8}',na = False)]
        Others = Others[~(Others['Remark'].str.contains('船上聯絡人|籍、船員|漁工',na = False) | (Others['Addr'].str.contains('原船檢疫|船號|船員',na = False)))]
        onboard_native['classify'] = '本籍船員原船檢疫'
        onboard_aboard['classify'] = '外籍船員原船檢疫'
        #print (D2.filter(['Seq','IdNo','OtherIdNo','Remark']))
        Z = PD.concat([Z,onboard_native])
        Z = PD.concat([Z,onboard_aboard])
    except:
        onboard_native = []
        onboard_aboard = []

    try :
        achild = Others[Others['Remark'].str.contains('幼童|幼兒|嬰兒|未成年|小朋友|小孩|共用|[0|1]?[0-9]歲',na = False) | Others['Name'].str.contains('嬰兒|未成年|小孩|[0|1]?[0-9]歲',na = False)]
        Others = Others[~(Others['Remark'].str.contains('幼童|幼兒|嬰兒|未成年|小朋友|小孩|共用|[0|1]?[0-9]歲',na = False) | Others['Name'].str.contains('嬰兒|未成年|小孩|[0|1]?[0-9]歲',na = False))]
        achild['classify'] = '兒童'
        Z = PD.concat([Z,achild])
    except:
        achild = []

    try :
        no_mobile = Others[(Others['Remark'].str.contains('發罄|發謦|發磬|手機已罄',na = False))|(Others['Addr'].str.contains('發罄|發謦|發磬|手機已罄',na = False))|(Others['Name'].str.contains('發罄|發謦|發磬|手機已罄',na = False))]
        Others = Others[~((Others['Remark'].str.contains('發罄|發謦|發磬|手機已罄',na = False))|(Others['Addr'].str.contains('發罄|發謦|發磬|手機已罄',na = False))|(Others['Name'].str.contains('發罄|發謦|發磬|手機已罄',na = False)))]
        no_mobile['classify'] = '手機發罄'
        Z = PD.concat([Z,no_mobile])
    except:
        no_mobile = []

    try :
        wait_mobile = Others[Others['Remark'].str.contains('待送|待發|發防疫手機|需要防疫手機|申請防疫手機',na = False)|(Others['Name'].str.contains('防疫手機',na = False))]
        Others = Others[~(Others['Remark'].str.contains('待送|待發|發防疫手機|需要防疫手機|申請防疫手機',na = False)|(Others['Name'].str.contains('防疫手機',na = False)))]
        wait_mobile['classify'] = '待發手機'
        Z = PD.concat([Z,wait_mobile])
    except:
        wait_mobile = []

    try :
        no_signal = Others[Others['Name'].str.contains('訊號|收訊|手機異常',na = False)|Others['Remark'].str.contains('訊號|收訊|手機異常',na = False)]
        Others= Others[~(Others['Name'].str.contains('訊號|收訊|手機異常',na = False)|Others['Remark'].str.contains('訊號|收訊|手機異常',na = False))]
        no_signal['classify'] = '訊號不良'
        Z = PD.concat([Z,no_signal])
    except:
        no_signal = []

    try :
        wait_employ = Others[Others['Remark'].str.contains('移工|雇主|僱主|仲介',na = False)|(Others['Name'].str.contains('公司',na = False))]
        Others = Others[~(Others['Remark'].str.contains('移工|雇主|僱主|仲介',na = False)|(Others['Name'].str.contains('公司',na = False)))]
        wait_employ['classify'] = '仲介雇主'
        Z = PD.concat([Z,wait_employ])
    except :
        wait_employ = []

    try :
        Business = Others[(Others['VisitPurpose'] == '1')]
        Others =  Others[~(Others['VisitPurpose'] == '1')]
        Business['classify'] = '商務人士'
        Z = PD.concat([Z,Business])
    except :
        Business = []

    try :
        in_rest = Others[Others['Remark'].str.contains('防疫旅宿|防疫旅館|飯店',na = False)]
        Others = Others[~Others['Remark'].str.contains('防疫旅宿|防疫旅館|飯店',na = False)]
        in_rest['classify'] = '防疫旅館'
        Z = PD.concat([Z,in_rest])
    except :
        in_rest = []

    try :
        wait_modify = Others
        wait_modify['classify'] = '待修正' 
        Z = PD.concat([Z,wait_modify])
    except :
        wait_modify = []
    return Z

def __main__():
    global _R
    global _tk
    global _id
    ConfigFile = sys.argv[1] if len(sys.argv) > 1 else (os.path.dirname(sys.argv[0])+'\\QUA_Classify.ini')
    #print (ConfigFile)
    myCrypt = MyCryp()
    Config = ConfigParser(allow_no_value=True)
    Config.optionxform = str
    Config.read(ConfigFile,encoding='utf-8')
    _R = Config['RE']
    _tk = Config['Notify']['Telegram Token']
    _id = Config['Notify']['Chat ID']
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
        Config['SFTP']['username'] = myCrypt.encryp(un)
        Config['SFTP']['password'] = myCrypt.encryp(pw)
        Config['SFTP']['ip'] = myCrypt.encryp(ip)
        Config['SFTP']['encrypt'] = 'True'
    A = SFTP(un,pw,ip)

    t11 = datetime.now().strftime('%Y/%m/%d')
    if int(datetime.now().strftime('%H')) > 15 :
        t = datetime.now().strftime('%Y%m%d15')
        t1 = datetime.now().strftime(u'%m月%d日15時')
        ta = datetime.now().strftime('%Y%m%d15')
        #tta = datetime.now().strftime('%Y%m%d16')
        yt = datetime.now().strftime('%Y%m%d03')
        tmpmsg = '下午'
    else: 
        t = datetime.now().strftime('%Y%m%d03')
        t1 = datetime.now().strftime(u'%m月%d日03時')
        ta = datetime.now().strftime('%Y%m%d03')
        yt = datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d15')
        #yt = datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d16')
        tmpmsg = '今早'
    p = _R['FileQUA']
    p1 = _R['FileCountQUA'].format(ta,'{1,5}')
    p2 = _R['FileCountISO'].format(ta,'{1,5}')
    #====QUA================================
    pQSearch = re.compile(p.format('QUARANTINE','ABNORMAL_',t,'{1,5}'))
    pISearch = re.compile(p.format('ISOLATION','ABNORMAL',t,'{1,5}'))
    p1QSearch = re.compile(p1)
    p2ISearch = re.compile(p2)
    pyQSearch = re.compile(p.format('QUARANTINE','ABNORMAL_',yt,'{1,5}'))
    pyISearch = re.compile(p.format('ISOLATION','ABNORMAL',yt,'{1,5}'))

    #print (pQSearch)
    A.ChangeDir(isopath)
    try :
        with  A.getFile (p2ISearch) as qFile2 :
            if qFile2 is not None: 
                sData = PD.read_csv(qFile2,header = 0,dtype = str)
                itotal,iefence,iabnormal = sData['Totalnum'][0],sData['efencenum'][0],sData['unoffernum'][0]
            else:
                itotal,iefence,iabnormal = '0','0','0'
    except :
        raise Exception("Cannot find ISO total count file.")

    try:
        with A.getFile (pyISearch) as iyFile :
            yData = PD.read_csv(iyFile,header = 0,dtype = str)
            ySeq = yData['Seq']
    except :
        raise Exception("Cannot find last ISO file.")

    try:
        with A.getFile( pISearch) as iFile:
            iData = PD.read_csv(iFile,header = 0,dtype = str,encoding= 'utf-8')
            NewI = iData.query("Seq not in @ySeq")
            nNewI = str(len(NewI))
    except:
        raise Exception("Cannot find ISO file.")

    A.ChangeDir(quapath)
    try :
        with  A.getFile (p1QSearch) as qFile1 :
            if qFile1 is not None:
                sData = PD.read_csv(qFile1,header = 0,dtype = int)
                total,efence,abnormal = sData['Totalnum'][0],sData['efencenum'][0],sData['unoffernum'][0]
            else:
                total,efence,abnormal = 0,0,0
    except :
        raise Exception("Cannot find QUA total count file.")

    try:
        with A.getFile (pyQSearch) as qyFile :
            yData = PD.read_csv(qyFile,header = 0,dtype = str)
            ySeq = yData['Seq']
    except :
        raise Exception("Cannot find last QUA file.")

    try:
        with A.getFile( pQSearch) as qFile:
            qData = PD.read_csv(qFile,header = 0,dtype = str,encoding= 'utf-8')
            NewQ = qData.query("Seq not in @ySeq")
            nNewQ = str(len(NewQ))
    except:
        raise Exception("Cannot find QUA file.")

    Z = fun_classify(qData)
    dataError = PD.concat([Z.query("classify == 'DC程式錯誤'") , Z.query("classify == '部分確認'")])
    Others = Z.query("(classify != '部分確認') and (classify != 'DC程式錯誤')")
    len_dataError = len(dataError)
    if len(dataError) != 0:
    #重新計算相關數據
        NewQ = Others.query("Seq not in @ySeq")
        nNewQ = str(len(NewQ))
        total = total - len_dataError
        abnormal = abnormal - len_dataError

    remoteFilename = 'QUA_{}.xlsx'.format(t) 
    localFilename = saveto+'\\{}'.format(remoteFilename)
    
    Z.to_excel(localFilename,sheet_name = 'ALL')
    A.ChangeDir(quapath+'/ABNORMAL_Classified')
    A.putFile(localFilename,remoteFilename)

    ZZ = Z.filter(items=['classify','Nationality','VisitPurpose','Name','Remark','Addr','ErrorType','TownCode','CellPhone','Seq','IdNo','OtherIdNo'])
    ZZ.to_excel(saveto+'\\QUA_{}_Classify_Check.xlsx'.format(t),sheet_name = 'ALL')
    dataError.to_excel(saveto+'\\QUA_{}_dataError_{}.xlsx'.format(t,len_dataError),sheet_name = 'ALL')

    qgs = GSheet(Config['GSheet']['ID'],Config['GSheet']['auth_json'])
    ranges = u'QUA_1!B1:B13'
    ranges1 = u'QUA_1!B15:B22'
    ranges2 = u'QUA_1!B25'
    values = [[t1]
            ,[str(total)]
            ,[str(abnormal)]
            ,[str(efence)]
            ,[str(len(Z.query("classify == u'手機發罄'")))]
            ,[str(len(Z.query("classify == u'待發手機'")))]
            ,[str(len(Z.query("classify == u'仲介雇主'")))]
            ,[str(len(Z.query("classify == u'商務人士'")))]
            ,[str(len(Z.query("classify == u'兒童'")))]
            ,[str(len(Z.query("classify == u'外籍學生'")))]
            ,[str(len(Z.query("classify == u'防疫旅館'")))]
            ,[str(len(Z.query("classify == u'待修正'")))]
            ,[str(len(Z.query("classify == u'未入境'")))]
            ,]
    values1 =[[str(len(Z.query("classify == u'訊號不良'")))]
            ,[str(len(Z.query("classify == u'外籍船員原船檢疫'")))]
            ,[str(len(Z.query("classify == u'本籍船員原船檢疫'")))]
            ,[str(len(Z.query("classify == u'服刑中'")))]
            ,[str(len(Z.query("classify == u'住院中'")))]
            ,[str(len(Z.query("classify == u'集中檢疫'")))]
            ,[str(len(Z.query("classify == u'轉隔離'")))]
            ,[str(len(Z.query("classify == u'暫時解列'")))]
            ,]
    values2 = [[nNewQ,],]

    dd = {  'value_input_option': 'USER_ENTERED',
            'data':[{   'range': ranges,
                        'majorDimension': "ROWS",
                        'values': values
                    },
                    {   'range':ranges1,
                        'majorDimension': "ROWS",
                        'values': values1
                    },
                    {   'range':ranges2,
                        'majorDimension': "ROWS",
                        'values': values2
                    },],
            }
    ranges3 = u'QUA!A1:D1'
    ranges4 = u'ISO!A1:D1'
    values3 =[[t11,str(total),str(efence),str(abnormal), ], ]
    values4 =[[t11,str(itotal),str(iefence),str(iabnormal), ], ]
    #print (dd)
    #'''
    qgs.batchupdate(dd)
    tmpData = qgs.get('QUA_1!B1:B25','COLUMNS')
    qgs.append('QUA_ROWS!A1:X',{'values':tmpData['values']})
    if (tmpmsg == '今早'):
        qgs.append(ranges3,{'values':values3})
        qgs.append(ranges4,{'values':values4})

    Config['Work']['last done'] = t1
    Config.write(open (ConfigFile,'w+',encoding='utf-8'))
    if  _notify == True:
        T = Telegram(_tk,_id)
        msg = ''
        msg += '{}應管{},送出{},未送出{} #居檢統計\n'.format (t1,str(total),str(efence),str(abnormal))
        msg += '{}應管{},送出{},未送出{} #隔離統計\n'.format (t1,itotal,iefence,iabnormal)
        msg += '{} 本次居檢新增: {}, 資料錯誤: {}(未入境: {}) #居檢分析'.format(t1,nNewQ,len_dataError,len(Z.query("classify == u'未入境'")))
        T.notify(msg)
        msg = '報告，{}未送出給圍籬計 {} 筆，資料分類統計如下：'.format(tmpmsg,str(abnormal))
        T.notify(msg)


if __name__ == '__main__' :
    try:
        __main__()
    except Exception as e:
        T = Telegram(_tk,_id)
        msg = '{}'.format(str(e))
        T.notify(msg)