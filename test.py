import time
import requests
from bs4 import BeautifulSoup

# 需要修改的部分
#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################

authen = {
    # 用户名和密码
    'username': '',
    'password': '',
}

courseList=[
    {
        'BJDM':'f2a1c814d5ba4cc985f963c2282158e0',
        'lx':'2',
        'skfsdm': "01",  
    }, 

    {
        'BJDM':'940269bcd4a248d1b2891d1deeb5f8f6',
        'lx':'2',
        'skfsdm': "01",  
    }, 

    {
        'BJDM':'c008ae27a3734e1cacc99f627c197c19',
        'lx':'2',
        'skfsdm': "01",  
    }, 
]

cour_name = [
    "英语阅读2班","英语阅读3班","英语阅读4班",
]


# 以下不需要修改
#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
}

def get_stamp():
    return str(int(time.time() * 1000))

def get_web(session, url):
    try:
        page = session.get(url, headers=headers, timeout=15)
        return page
    except Exception as e:
        print(f"获取网页时出错: {str(e)}")
        return None

def get_zwid(session, file):
    try:
        t = get_stamp()
        id_url = "https://yjsxk.buaa.edu.cn/yjsxkapp/sys/xsxkappbuaa/xsxkCourse/loadFanCourseInfo.do?_=" + t + "&pageSize=100"
        zw = get_web(session, id_url)
        if zw is None:
            return
            
        zwj = zw.json()
        for i in zwj["datas"]:
            if "ISKZ" in i:
                if "DXZWID" in i:
                    file.write(i["KCLBMC"] + "—" + i["KCMC"] + '\n')
                    file.write("DXZWID:" + i["DXZWID"] + '\n')
                    file.write("KZWID:" + i["KZWID"] + '\n\n')
                else:
                    file.write(i["KCLBMC"] + "—" + i["KCMC"] + '\n')
                    file.write("KZWID:" + i["KZWID"] + '\n\n')
    except Exception as e:
        print(f"获取ID时出错: {str(e)}")

def get_csrf(session):
    try:
        indx = "https://yjsxk.buaa.edu.cn/yjsxkapp/sys/xsxkappbuaa/xsxkHome/loadPublicInfo_course.do?_="
        rc = get_web(session, indx + get_stamp())
        if rc is None:
            return None
            
        rr = rc.json()
        return rr["csrfToken"]
    except Exception as e:
        print(f"获取CSRF令牌时出错: {str(e)}")
        return None

def get_post(k, csrf):
    try:
        kc = {
            'bjdm': k['BJDM'],
            'skfsdm': k['skfsdm'], 
            'lx': k['lx'],
            'csrfToken': csrf,
        }
        if 'fromKzwid' in k and 'fromDxzwid' in k:
            kc['fromKzwid'] = k['fromKzwid']
            kc['fromDxzwid'] = k['fromDxzwid'],
        elif 'fromKzwid' in k and 'fromDxzwid' not in k:
            kc['fromKzwid'] = k['fromKzwid']
        return kc
    except Exception as e:
        print(f"构建POST数据时出错: {str(e)}")
        return None

def query(session, j, k, csrf):
    try:
        xk = "https://yjsxk.buaa.edu.cn/yjsxkapp/sys/xsxkappbuaa/xsxkCourse/choiceCourse.do?_="
        xk = xk + get_stamp()
        kc_data = get_post(k, csrf)
        if kc_data is None:
            return "error"
            
        r = session.post(xk, data=kc_data)
        rj = r.json()
        
        if rj['msg'] == "页面已过期，请刷新页面后重试":
            return "error"
        else:
            print(cour_name[j] + ":" + rj['msg'])
            if (rj['code'] == 1):
                jg_data = {
                    'xid': rj["msg"],
                    'sfhqdqxkqqs': '1',
                }
                time.sleep(0.5)
                jg_url = "https://yjsxk.buaa.edu.cn/yjsxkapp/sys/xsxkappbuaa/xsxkCourse/loadXkjgRes.do?_=" + get_stamp()
                jg = session.post(jg_url, data=jg_data)
                jgj = jg.json()
                print(jgj)
                if (jgj['msg'] == '{"code":1}'):
                    print('选课成功。')
                else:
                    print("选课失败。")
            return "OK"
    except Exception as e:
        print(f"查询课程时出错: {str(e)}")
        return "error"

def qk(session, cours, csrf):
    try:
        j = 0
        for k in cours:
            a = query(session, j, k, csrf)
            if a == "OK":
                j += 1
            if a == "error":
                print("界面刷新。")
                return "error"
        time.sleep(0.8)
        return "OK"
    except Exception as e:
        print(f"抢课过程中出错: {str(e)}")
        return "error"

def main_loop():
    while True:
        try:
            # 每次循环都创建新的会话，确保连接状态干净
            session = requests.Session()
            
            # 登录过程
            print("尝试登录...")
            login_page = get_web(session, "https://sso.buaa.edu.cn/login?service=https://yjsxk.buaa.edu.cn/yjsxkapp/sys/xsxkappbuaa/*default/index.do")
            if login_page is None:
                print("登录页面获取失败，将重试...")
                time.sleep(5)
                continue
                
            soup = BeautifulSoup(login_page.text, 'html.parser')
            execution_input = soup.find('input', {'name': 'execution'})
            if not execution_input:
                print("未找到execution参数，将重试...")
                time.sleep(5)
                continue
                
            execution_value = execution_input.get('value', '')
            
            login_data = {
                'username': authen['username'],
                'password': authen['password'],
                'type': 'username_password',
                'submit': 'LOGIN',
                '_eventId': 'submit',
                'execution': execution_value
            }
            
            r = session.post("https://sso.buaa.edu.cn/login", data=login_data)
            if r.status_code != 200:
                print(f"登录请求失败，状态码: {r.status_code}，将重试...")
                time.sleep(5)
                continue
            
            # 获取CSRF令牌
            csrf = get_csrf(session)
            if not csrf:
                print("获取CSRF令牌失败，将重试...")
                time.sleep(5)
                continue
            
            # 开始抢课循环
            i = 1
            while True:
                print(f"第{i}次抢课尝试。")
                result = qk(session, courseList, csrf)
                
                if result == "error":
                    print("抢课过程出现错误，尝试刷新CSRF令牌...")
                    csrf = get_csrf(session)
                    if not csrf:
                        print("刷新CSRF令牌失败，将重新开始整个流程...")
                        break  # 跳出内部循环，回到主循环重新开始
                
                # 每50次尝试后稍作休息
                if i % 50 == 0:
                    time.sleep(5)
                
                i += 1
                # 每次尝试后短暂休息，避免过于频繁的请求
                time.sleep(1)
                
        except Exception as e:
            print(f"主循环出错: {str(e)}，将在5秒后重新开始...")
            time.sleep(5)  # 出错后稍等再重试，避免无限快速重试

if __name__ == "__main__":
    print("开始选课程序，按Ctrl+C可终止程序...")
    main_loop()
