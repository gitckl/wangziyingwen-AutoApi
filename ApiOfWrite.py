# -*- coding: UTF-8 -*-
import os
import xlsxwriter
import requests as req
import json,sys,time,random

#reload(sys)
#sys.setdefaultencoding('utf-8')
emailaddress=os.getenv('EMAIL')
app_num=os.getenv('APP_NUM')
###########################
# config选项说明
# 0：关闭  ， 1：开启
# allstart：是否全api开启调用，关闭默认随机抽取调用。默认0关闭
# rounds: 轮数，即每次启动跑几轮。
# rounds_delay: 是否开启每轮之间的随机延时，后面两参数代表延时的区间。默认0关闭
# api_delay: 是否开启api之间的延时，默认0关闭
# app_delay: 是否开启账号之间的延时，默认0关闭
########################################
config = {
         'allstart': 0,
         'rounds': 1,
         'rounds_delay': [0,0,5],
         'api_delay': [0,0,5],
         'app_delay': [0,0,5],
         }        
if app_num == '':
    app_num = '1'
city=os.getenv('CITY')
if city == '':
    city = 'Beijing'
access_token_list=['wangziyingwen']*int(app_num)

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
        print(r'账号/应用 '+str(appnum)+' 的微软密钥获取失败\n'+'请检查secret里 CLIENT_ID , CLIENT_SECRET , MS_TOKEN 格式与内容是否正确，然后重新设置')
    refresh_token = jsontxt['refresh_token']
    access_token = jsontxt['access_token']
    return access_token

#api延时
def apiDelay():
    if config['api_delay'][0] == 1:
        time.sleep(random.randint(config['api_delay'][1],config['api_delay'][2]))
        
def apiReq(method,a,url,data='QAQ'):
    apiDelay()
    access_token=access_token_list[a-1]
    headers={
            'Authorization': 'bearer ' + access_token,
            'Content-Type': 'application/json'
            }
    if method == 'post':
        posttext=req.post(url,headers=headers,data=data)
    elif method == 'put':
        posttext=req.put(url,headers=headers,data=data)
    elif method == 'delete':
        posttext=req.delete(url,headers=headers)
    else :
        posttext=req.get(url,headers=headers)
    if posttext.status_code < 300:
        print('        操作成功')
    else:
        print('        操作失败')
#    if posttext.status_code > 300:
#        print('        操作失败')
#        #成功不提示
    return posttext.text
          

#上传文件到onedrive(小于4M)
def UploadFile(a,filesname,f):
    url=r'https://graph.microsoft.com/v1.0/me/drive/root:/AutoApi/App'+str(a)+r'/'+filesname+r':/content'
    apiReq('put',a,url,f)
    
        
# 发送邮件到自定义邮箱
def SendEmail(a,subject,content):
    url=r'https://graph.microsoft.com/v1.0/me/sendMail'
    mailmessage={'message': {'subject': subject,
                             'body': {'contentType': 'Text', 'content': content},
                             'toRecipients': [{'emailAddress': {'address': emailaddress}}],
                             },
                 'saveToSentItems': 'true'}            
    apiReq('post',a,url,json.dumps(mailmessage))	
	
#修改excel(这函数分离好像意义不大)
#api-获取itemid: https://graph.microsoft.com/v1.0/me/drive/root/search(q='.xlsx')?select=name,id,webUrl
def excelWrite(a,filesname,sheet):
    url=r'https://graph.microsoft.com/v1.0/me/drive/root:/AutoApi/App'+str(a)+r'/'+filesname+r':/workbook/worksheets/add'
    data={
         "name": sheet
         }
    print('    添加工作表')
    apiReq('post',a,url,json.dumps(data))
    url=r'https://graph.microsoft.com/v1.0/me/drive/root:/AutoApi/App'+str(a)+r'/'+filesname+r':/workbook/worksheets/'+sheet+r'/tables/add'
    data={
         "address": "A1:D8",
         "hasHeaders": False
         }
    print('    添加表格')
    jsontxt=json.loads(apiReq('post',a,url,json.dumps(data)))
    print('    添加行')
    url=r'https://graph.microsoft.com/v1.0/me/drive/root:/AutoApi/App'+str(a)+r'/'+filesname+r':/workbook/tables/'+jsontxt['id']+r'/rows/add'
    rowsvalues=[[0]*4]*2
    for v1 in range(0,2):
        for v2 in range(0,4):
            rowsvalues[v1][v2]=random.randint(1,1200)
    data={
         "values": rowsvalues
         }
    apiReq('post',a,url,json.dumps(data))
    
def taskWrite(a,taskname):
    url=r'https://graph.microsoft.com/v1.0/me/todo/lists'
    data={
         "displayName": taskname
         }
    print("    创建任务列表")
    listjson=json.loads(apiReq('post',a,url,json.dumps(data)))
    url=r'https://graph.microsoft.com/v1.0/me/todo/lists/'+listjson['id']+r'/tasks'
    data={
         "title": taskname,
         }
    print("    创建任务")
    taskjson=json.loads(apiReq('post',a,url,json.dumps(data)))
    url=r'https://graph.microsoft.com/v1.0/me/todo/lists/'+listjson['id']+r'/tasks/'+taskjson['id']
    print("    删除任务")
    apiReq('delete',a,url)
    url=r'https://graph.microsoft.com/v1.0/me/todo/lists/'+listjson['id']
    print("    删除任务列表")
    apiReq('delete',a,url)    
    
def teamWrite(a,channelname):
    url=r'https://graph.microsoft.com/v1.0/me/joinedTeams'
    print("    获取team")
    jsontxt = json.loads(apiReq('get',a,url))
    objectlist=jsontxt['value']
    #创建
    print("    创建team频道")
    data={
         "displayName": channelname,
         "description": "This channel is where we debate all future architecture plans",
         "membershipType": "standard"
         }
    url=r'https://graph.microsoft.com/v1.0/teams/'+objectlist[0]['id']+r'/channels'
    jsontxt = json.loads(apiReq('post',a,url,json.dumps(data)))
    url=r'https://graph.microsoft.com/v1.0/teams/'+objectlist[0]['id']+r'/channels/'+jsontxt['id']
    print("    删除team频道")
    apiReq('delete',a,url)

def onenoteWrite(a,notename):
    url=r'https://graph.microsoft.com/v1.0/me/onenote/notebooks'
    data={
         "displayName": notename
         }
    print('    创建笔记本')
    notetxt = json.loads(apiReq('post',a,url,json.dumps(data)))
    print('    删除笔记本')
    url=r'https://graph.microsoft.com/v1.0/me/drive/root:/Notebooks/'+notename
    apiReq('delete',a,url)
    
#一次性获取access_token，降低获取率
for a in range(1, int(app_num)+1):
    client_id=os.getenv('CLIENT_ID_'+str(a))
    client_secret=os.getenv('CLIENT_SECRET_'+str(a))
    ms_token=os.getenv('MS_TOKEN_'+str(a))
    access_token_list[a-1]=getmstoken(ms_token,a)
print('')    
#获取天气
headers={'Accept-Language': 'zh-CN'}
weather=req.get(r'http://wttr.in/'+city+r'?format=4&?m',headers=headers).text

#实际运行
for a in range(1, int(app_num)+1):
    print('账号 '+str(a))
    print('发送邮件 ( 邮箱单独运行，每次运行只发送一次，防止封号 )')
    if emailaddress != '':
        SendEmail(a,'weather',weather)
        print('')
#其他api
for _ in range(1,config['rounds']+1):
    if config['rounds_delay'][0] == 1:
        time.sleep(random.randint(config['rounds_delay'][1],config['rounds_delay'][2]))     
    print('第 '+str(_)+' 轮\n')        
    for a in range(1, int(app_num)+1):
        if config['app_delay'][0] == 1:
            time.sleep(random.randint(config['app_delay'][1],config['app_delay'][2]))        
        print('账号 '+str(a))    
        #生成随机名称
        filesname='QAQ'+str(random.randint(1,600))+r'.xlsx'
        #新建随机xlsx文件
        xls = xlsxwriter.Workbook(filesname)
        xlssheet = xls.add_worksheet()
        for s1 in range(0,4):
            for s2 in range(0,4):
                xlssheet.write(s1,s2,str(random.randint(1,600)))
        xls.close()
        xlspath=sys.path[0]+r'/'+filesname
        print('上传文件 ( 可能会偶尔出现创建上传失败的情况 ) ')
        with open(xlspath,'rb') as f:
            UploadFile(a,filesname,f)
        choosenum = random.sample(range(1, 5),2)
        if config['allstart'] == 1 or 1 in choosenum:
            print('excel文件操作')
            excelWrite(a,filesname,'QVQ'+str(random.randint(1,600)))
        if config['allstart'] == 1 or 2 in choosenum:
            print('team操作')
            teamWrite(a,'QVQ'+str(random.randint(1,600)))
        if config['allstart'] == 1 or 3 in choosenum:
            print('task操作')
            taskWrite(a,'QVQ'+str(random.randint(1,600)))
        if config['allstart'] == 1 or 4 in choosenum:
            print('onenote操作')
            onenoteWrite(a,'QVQ'+str(random.randint(1,600)))
        print('-')