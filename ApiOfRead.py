# -*- coding: UTF-8 -*-
import os
import requests as req
import json,sys,time,random

app_num=os.getenv('APP_NUM')
if app_num == '':
    app_num = '1'
access_token_list=['wangziyingwen']*int(app_num)
###########################
# config选项说明
# 0：关闭  ， 1：开启
# api_rand：是否随机排序api （开启随机抽取12个，关闭默认初版10个）。默认1开启
# rounds: 轮数，即每次启动跑几轮。
# rounds_delay: 是否开启每轮之间的随机延时，后面两参数代表延时的区间。默认0关闭
# api_delay: 是否开启api之间的延时，默认0关闭
# app_delay: 是否开启账号之间的延时，默认0关闭
########################################
config = {
         'api_rand': 1,
         'rounds': 3,
         'rounds_delay': [0,60,120],
         'api_delay': [0,2,6],
         'app_delay': [0,30,60],
         }
api_list = [
           r'https://graph.microsoft.com/v1.0/me/',
           r'https://graph.microsoft.com/v1.0/users',
           r'https://graph.microsoft.com/v1.0/me/people',
           r'https://graph.microsoft.com/v1.0/groups',
           r'https://graph.microsoft.com/v1.0/me/contacts',
           r'https://graph.microsoft.com/v1.0/me/drive/root',
           r'https://graph.microsoft.com/v1.0/me/drive/root/children',
           r'https://graph.microsoft.com/v1.0/drive/root',
           r'https://graph.microsoft.com/v1.0/me/drive',
           r'https://graph.microsoft.com/v1.0/me/drive/recent',
           r'https://graph.microsoft.com/v1.0/me/drive/sharedWithMe',
           r'https://graph.microsoft.com/v1.0/me/calendars',
           r'https://graph.microsoft.com/v1.0/me/events',
           r'https://graph.microsoft.com/v1.0/sites/root',
           r'https://graph.microsoft.com/v1.0/sites/root/sites',
           r'https://graph.microsoft.com/v1.0/sites/root/drives',
           r'https://graph.microsoft.com/v1.0/sites/root/columns',
           r'https://graph.microsoft.com/v1.0/me/onenote/notebooks',
           r'https://graph.microsoft.com/v1.0/me/onenote/sections',
           r'https://graph.microsoft.com/v1.0/me/onenote/pages',
           r'https://graph.microsoft.com/v1.0/me/messages',
           r'https://graph.microsoft.com/v1.0/me/mailFolders',
           r'https://graph.microsoft.com/v1.0/me/outlook/masterCategories',
           r'https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages/delta',
           r'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules',
           r"https://graph.microsoft.com/v1.0/me/messages?$filter=importance eq 'high'",
           r'https://graph.microsoft.com/v1.0/me/messages?$search="hello world"',
           r'https://graph.microsoft.com/beta/me/messages?$select=internetMessageHeaders&$top',
           ]

#微软refresh_token获取
def getmstoken(ms_token,appnum):
    headers={'Content-Type':'application/x-www-form-urlencoded'
            }
    data={'grant_type': 'refresh_token',
        'refresh_token': ms_token,
        'client_id':client_id,
        'client_secret':client_secret,
        'redirect_uri':'http://localhost:53682/'
        }
    html = req.post('https://login.microsoftonline.com/common/oauth2/v2.0/token',data=data,headers=headers)
    jsontxt = json.loads(html.text)
    if 'refresh_token' in jsontxt:
        print(r'账号/应用 '+str(appnum)+' 的微软密钥获取成功')
    else:
        print(r'账号/应用 '+str(appnum)+' 的微软密钥获取失败'+'\n'+'请检查secret里 CLIENT_ID , CLIENT_SECRET , MS_TOKEN 格式与内容是否正确，然后重新设置')
    refresh_token = jsontxt['refresh_token']
    access_token = jsontxt['access_token']
    return access_token

#调用函数
def runapi(apilist,a):
    localtime = time.asctime( time.localtime(time.time()) )
    access_token=access_token_list[a-1]
    headers={
            'Authorization': 'bearer ' + access_token,
            'Content-Type': 'application/json'
            }
    for b in range(len(apilist)):	
        if req.get(api_list[apilist[b]],headers=headers).status_code == 200:
            print('第'+str(apilist[b])+"号api调用成功")
        else:
            print("pass")
        if config['api_delay'][0] == 1:
            time.sleep(random.randint(config['api_delay'][1],config['api_delay'][2]))

#一次性获取access_token，降低获取率
for a in range(1, int(app_num)+1):
    client_id=os.getenv('CLIENT_ID_'+str(a))
    client_secret=os.getenv('CLIENT_SECRET_'+str(a))
    ms_token=os.getenv('MS_TOKEN_'+str(a))
    access_token_list[a-1]=getmstoken(ms_token,a)

#随机api序列
fixed_api=[0,1,5,6,20,21]
#保证抽取到outlook,onedrive的api
ex_api=[2,3,4,7,8,9,10,22,23,24,25,26,27,13,14,15,16,17,18,19,11,12]
#额外抽取填充的api
fixed_api.extend(random.sample(ex_api,6))
random.shuffle(fixed_api)
final_list=fixed_api

#实际运行
if int(app_num) > 1:
    print('多账户/应用模式下，日志报告里可能会出现一堆***，属于正常情况')
print("如果api数量少于规定值，则是api赋权没有弄好，或者是onedrive还没有初始化成功。前者请重新赋权并获取微软密钥替换，后者请稍等几天")
print('共 '+str(app_num)+r' 账号/应用，'+r'每个账号/应用 '+str(config['rounds'])+' 轮') 
for r in range(1,config['rounds']+1):
    if config['rounds_delay'][0] == 1:
        time.sleep(random.randint(config['rounds_delay'][1],config['rounds_delay'][2]))		
    for a in range(1, int(app_num)+1):
        if config['app_delay'][0] == 1:
            time.sleep(random.randint(config['app_delay'][1],config['app_delay'][2]))
        client_id=os.getenv('CLIENT_ID_'+str(a))
        client_secret=os.getenv('CLIENT_SECRET_'+str(a))
        print('\n'+'应用/账号 '+str(a)+' 的第'+str(r)+'轮 '+time.asctime(time.localtime(time.time()))+'\n')
        if config['api_rand'] == 1:
            print("已开启随机顺序,共十二个api,自己数")
            apilist=final_list
        else:
            print("原版顺序,共十个api,自己数")
            apilist=[5,9,8,1,20,24,23,6,21,22]
        runapi(apilist,a)
