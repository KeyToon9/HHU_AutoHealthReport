import requests, re
import os, json
import datetime

# 脚本会自动生成cookies文件保存以便短时间内多次登录
# 请保护好自己的隐私
user_id     = ''# 学号
user_psw    = ''# 密码
user_name   = ''# 姓名
user_sfz    = ''# 身份证号码
user_ph     = ''# 手机号码
# 以下信息请严格按照健康打卡表单中的信息填写
user_col    = ''# 学院 如 计信院
user_year   = ''# 年级 如 2019级
user_spec   = ''# 专业 如 计算机
user_class  = ''# 班级 如 计算机18_1
user_dorm   = ''# 宿舍楼 如 江宁校区教学区1舍
user_dormid = ''# 宿舍号 如 110

host = 'http://form.hhu.edu.cn'
url_login = 'http://ids.hhu.edu.cn/amserver/UI/Login'
#url_index = 'http://my.hhu.edu.cn/index.portal'
url_form = 'http://form.hhu.edu.cn/pdc/form/list'
url_save_form = 'http://form.hhu.edu.cn/pdc/formDesignApi/dataFormSave?'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
}

form_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    'Referer': 'http://form.hhu.edu.cn/pdc/form/list'
}

re_get_url = r'<a href="(/pdc.*)" class'
re_get_wid = r"var _selfFormWid = '([A-Z0-9]{+})';"

# Get Cookies
#==========================
def get_cookies_dict():
    login_post_data = {
        'Login.Token1': user_id,
        'Login.Token2': user_psw,
        'goto': 'http://my.hhu.edu.cn/loginSuccess.portal',
        'gotoOnFail': 'http://my.hhu.edu.cn/loginFailure.portal'
    }

    s = requests.session()

    s.post(url=url_login, headers=headers, data=login_post_data)
    return s.cookies.get_dict()

# Write cookies file
#==========================
def write_cookies(cookies_dict):
    with open('cookies.json', 'w') as f:
        json.dump(cookies_dict, f)
        
# Read cookies to dict
#==========================
def read_cookies(is_login = True):
    c = {}
    if os.path.exists('cookies.json') and is_login:
        with open('cookies.json', 'r') as f:
            c = json.load(f)
    else:
        c = get_cookies_dict()
        write_cookies(c)
    return c

# Login 
#==========================
def login():
    cookies_dict = read_cookies()
    
    s = requests.session()
    res = s.get(url=url_form, headers=headers, cookies=cookies_dict)
    fail_page = "<script type='text/javascript'>top.location.href='http://ids.hhu.edu.cn/amserver/UI/Login?goto=http://form.hhu.edu.cn/pdc/form/list';</script>"

    if res.status_code == 200:
        if res.text == fail_page:
            print('登录信息已过期, 正在重新登录')
            cookies_dict = read_cookies(is_login=False)
            res = s.get(url=url_form, headers=headers, cookies=cookies_dict)
        res.encoding='utf-8'
        return res, cookies_dict
    else:
        raise Exception("Error: " + res.status_code)

# Get the url of sign page
#==========================
def get_report_url(html_text):
    # 似乎所有人都是一样的
    # 但是以防万一还是动态获取
    # 然后缓存下来
    return re.findall(re_get_url, html_text)[0]

# Get wid
#==========================
def get_wid(html_text):
    # 淦 这个wid到底是什么东西啊
    return re.findall(re_get_wid, html_text)[0]

# save url and wid
#==========================
def save_info(form_url, wid):
    data = {
        'form_url': form_url,
        'wid': wid
    }
    
    with open('config.json', 'w') as f:
        json.dump(data, f)

def report(page, cookies):
    wid = 'A335B048C8456F75E0538101600A6A04'
    today = datetime.date.today().strftime("%Y/%m/%d")
    
    if (os.path.exists('config.json')):
        with open('config.json', 'r') as f:
            j = json.load(f)
            report_url = j['form_url']
            wid = j['wid']
    else:
        report_url = host + get_report_url(page.text)
        # wid = ?
        save_info(report_url, wid)
    
    print(today)
    
    s = requests.session()
    # 这里是想获取在 /formDesignApi/S/gUTwwojq 这个页面获取 wid
    # 可为什么get form.hhu.edu.cn/pdc/formDesignApi/S/gUTwwojq
    # 却会返回 form.hhu.edu.cn/pdc/form/list 的内容 为什么啊
    """
    res = s.get(url=report_url, headers=form_headers, cookies=cookies)
    """
    req_url = url_save_form + 'wid=' + wid + '&userId=' + user_id
    
    data = {
        'DATETIME_CYCLE': today,
        'XGH_336526': user_id,
        'XM_1474': user_name,
        'SFZJH_859173': user_sfz,
        'SELECT_941320': user_col,
        'SELECT_459666': user_year,
        'SELECT_814855': user_spec,
        'SELECT_525884': user_class,
        'SELECT_125597': user_dorm,
        'TEXT_950231': user_dormid,
        'TEXT_937296': user_ph,
        'RADIO_853789': '否',
        'RADIO_43840': '否',
        'RADIO_579935': '健康',
        'RADIO_138407': '否',
        'RADIO_546905': '否',
        'RADIO_314799': '否',
        'RADIO_209256': '否',
        'RADIO_836972': '否',
        'RADIO_302717': '否',
        'RADIO_701131': '否',
        'RADIO_438985': '否',
        'RADIO_467360': '是',
        # 这里我都默认了
        'PICKER_956186': '江苏省,南京市,江宁区',
        # TODO: 留学生 这里我不是留学生 所以我不知道这里会有什么
        'TEXT_434598': '',
        'TEXT_515297': '',
        'TEXT_752063': '',
    }
    
    res = s.post(url=req_url, headers=headers, cookies=cookies, data=data)
    
    if json.loads(res.text)['result']:
        print('签到成功')
    else:
        print('签到失败')
    
if __name__ == '__main__':
    page, cookies = login()
    report(page, cookies)
    
    