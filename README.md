這是一個分類居家者類型的程式

    QUA_Classify.py 用來分類

    QUA_Claim.py 用來統計各電信公司認領的數量

1.用 python QUA_Classify.py Config.ini 來執行，可以設入排程

2.用 python QUA_Claim.py Config.ini 來執行，可以設入排程

Config 檔要有下列 Sections
===================================================================
    [PATH]
    saveto = E:\test #分類結果的本地儲存路徑
    quapath = /pheic/QUARANTINE #遠端居檢資料路徑
    isopath = /pheic/ISOLATION #遠端隔離資料路徑

    [SFTP]
    encrypt = True #敏感資料是否己加密 [yes,True,no,False]
    username = <你的帳號>
    password = <你的密碼>
    ip = <SFTP 的 IP>

    [GSheet]
    ID = <google sheet ID>
    auth_json = <認證檔檔名>


    [Notify]
    Telegram Token = <Telegram token>
    Chat ID = <Telegram chat is>

    [Work]
    last done = 11月27日15時 最後更新日期

    [RE]
    FileQUA = ^EFENCE_{}_{}_{}_[0-9]{}.csv$
    FileCountQUA = ^EFENCE_QUARANTINE_{}_[0-9]{}.csv$
    FileCountISO = ^EFENCE_ISOLATION_{}_[0-9]{}.csv$
    be_punish = 監獄|看守所
    to_ISO = 轉.*衛政|轉.*隔離
