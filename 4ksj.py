#!/opt/conda/bin/python3.9
import httpx
import re
import sys
import time
from urllib.parse import urlencode

# global variables
uname = '**********'         # username，需要修改
upassword = '**********'     # password，需要修改
loginhash = ''
formhash = ''
r = httpx.Client(http2=True)
headers = {'Host':'www.4ksj.com',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
'Accept-Encoding':'gzip, deflate',
'Upgrade-Insecure-Requests':'1',
'Sec-Fetch-Dest':'document',
'Sec-Fetch-Mode':'navigate',
'Sec-Fetch-Site':'same-origin',
'Sec-Fetch-User':'?1',
'Te':'trailers'
}

#从个人空间页面获取当前K值
def getK(spaceurl):
    ret = r.get(spaceurl, headers = headers).text
    time.sleep(1)
    K_now = re.findall(r'<li><em>K币</em>(.*?) 个</li>', ret)[0]
    #print('当前K币: ' + str(K_now) + '个')
    return K_now

#登录网站，并获取个人空间入口
def login(uname, upassword):
    headers['Referer'] = 'https://www.4ksj.com/'
    ret = r.get(r'https://www.4ksj.com/member.php?mod=logging&action=login', headers=headers).text
    time.sleep(1)
    formhash = re.findall(r'<input type="hidden" name="formhash" value="(.*?)"', ret)[0]
    print('获取到登录页formhash: ' + formhash)
    loginhash = re.findall(r'loginhash=(.*?)"', ret)[0]
    print("获取到登录页loginhash:"+loginhash)
    headers['Origin'] = 'https://www.4ksj.com'
    headers['Referer'] = 'https://www.4ksj.com/member.php?mod=logging&action=login'
    headers['Sec-Fetch-Dest'] = 'iframe'
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    data = {'formhash':formhash, 'referer':'https://www.4ksj.com/', 'username':uname, 'password':upassword, 'questionid':'0', 'answer':''}
    ret = r.post('https://www.4ksj.com/member.php?mod=logging&action=login&loginsubmit=yes&loginhash='+loginhash+'&inajax=1', headers = headers, data=urlencode(data)).text
    time.sleep(1)
    if 'succeedmessage' in ret:
        print('登录成功')
    else:
        print(re.findall(r'errorhandle_\(\'(.*?)\', {', ret)[0])
        return False, False

    del headers['Origin']
    del headers['Content-Type']
    headers['Sec-Fetch-Dest'] = 'document'
    ret = r.get('https://www.4ksj.com', headers=headers).text

    spaceurl = ""
    userid = re.findall(r'discuz_uid = \'(.*?)\'', ret)[0]
    spaceurl = "https://www.4ksj.com/space-uid-"+userid+".html"
    print("个人空间入口:"+spaceurl)
    return spaceurl

#进行签到
def qiandao():
    headers['Referer'] = spaceurl
    ret = r.get('https://www.4ksj.com/qiandao/', headers = headers).text
    time.sleep(1)
    formhash = re.findall(r'action=logout&amp;formhash=(.*?)"', ret)[0]
    print('获取到签到页formhash: ' + formhash)

    headers['Referer'] = 'https://www.4ksj.com/qiandao/'
    headers['Sec-Fetch-Dest'] = 'empty'
    headers['Sec-Fetch-Mode'] = 'cors'
    headers['Accept'] = '*/*'
    headers['X-Requested-With'] = 'XMLHttpRequest'
    del headers['Upgrade-Insecure-Requests']
    ret = r.get('https://www.4ksj.com//qiandao/?mod=sign&operation=list&inajax=1&ajaxtarget=ranklist', headers = headers).text
    time.sleep(1)

    ret = r.get('https://www.4ksj.com//qiandao/?mod=sign&operation=qiandao&formhash=' + formhash + '&format=empty&inajax=1&ajaxtarget=', headers = headers).text
    time.sleep(1)
    if '今日已签' in ret:
        print('签到结果：今日已签')
    if '<root><![CDATA[]]></root>' in ret:
        print('签到结果：签到成功')

#退出登录
def logout(formhash):
    ret = r.get('https://www.4ksj.com/member.php?mod=logging&action=logout&formhash=' + formhash, headers = headers).text
    print('退出登录')


if __name__ == '__main__':
    print("4K世界签到开始：")
    for i in range(3): # 尝试3次
        if i > 0:
            #logger.warn('retrying for ' + str(i) + 'times')
            print('尝试第' + str(i) + '次')
        try:
            spaceurl = login(uname, upassword)
            #if not spaceurl:
            #    print("没有获取到昵称，签到失败，系统终止。")
            #    sys.exit(0) # exit if login failed
            headers['Referer'] = 'https://www.4ksj.com/'

            k_num1 = getK(spaceurl)

            qiandao()

            headers['Referer'] = 'https://www.4ksj.com/qiandao/'
            headers['Accept']='text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            headers['Sec-Fetch-Dest'] = 'document'
            headers['Sec-Fetch-Mode'] = 'navigate'
            headers['Upgrade-Insecure-Requests'] = '1'
            del headers['X-Requested-With']
            
            k_num2 = getK(spaceurl)

            print('***************结果统计***************')
            #print('之前K币: ' + str(k_num1) + '个')
            print('本次获得K币: ' + str(int(k_num2)-int(k_num1)) + '个')
            print('累计K币: ' + str(int(k_num2)) + '个')
            print('*************************************')

            logout(formhash)

            sys.exit(0)
        except Exception as e:
            print('line: ' + str(e.__traceback__.tb_lineno) + ' ' + repr(e))
            time.sleep(10)