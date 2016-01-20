#coding=utf-8
__author__ = 'AllenCHM'

from selenium import webdriver
import time
import codecs
import re
import random
import pymongo
from lxml import etree
import hashlib


accountNumber = u'xxxxxxxx' #账号
password = u'xxxxxxxx' #密码


def parsePageInfo(html):
    soup = etree.HTML(html)
    divs = soup.xpath('//div[@node-type="feed_list"]//div[contains(@class, "WB_cardwrap")]')
    lists = []
    for num, div in enumerate(divs):
        item = {}
        #微博ID, 微博正文， 链接地址， 发布时间， 微博来源， 转发量， 评论数， 评论内容， 点赞数，微博类型
        try:
            item[u'微博ID'] = div.xpath('.//div[@class="feed_content wbcon"]/a[1]/text()')[0].strip()
        except:
            continue
        item[u'IDurl'] = div.xpath('.//div[@class="feed_content wbcon"]/a[1]/@href')[0]
        item[u'微博正文'] = div.xpath('.//div[@class="feed_content wbcon"]/p[@class="comment_txt"]')[0].xpath('string(.)')
        item[u'链接地址'] = div.xpath('.//div[@class="feed_from W_textb"]/a[1]/@href')[-1]
        item[u'发布时间'] = div.xpath('.//div[@class="feed_from W_textb"]/a[1]/@title')[0].strip()
        try:
            item[u'微博来源'] = div.xpath('.//div[@node-type="like"]/div[@class="feed_from W_textb"]/a[@rel="nofollow"]/text()')[0]
        except:
            item[u'微博来源'] = u''
        item[u'转发量'] = div.xpath('.//div[@class="feed_action clearfix"]/ul/li[2]')[0].xpath('string(.)')[2:]
        item[u'评论数'] = div.xpath('.//div[@class="feed_action clearfix"]/ul/li[3]')[0].xpath('string(.)')[2:]
        # item[u'评论内容']
        item[u'点赞数'] = div.xpath('.//div[@class="feed_action clearfix"]/ul/li[4]')[0].xpath('string(.)')
        item[u'微博类型'] = div.xpath('.//div[@class="feed_content wbcon"]/div[@class="comment"]')
        if item[u'微博类型']:
            item[u'微博类型'] = u'转发'
        else:
            item[u'微博类型'] = u'原创'
        weiboDoc.update_one({u'链接地址':item[u'链接地址']}, {'$set': item}, True)
        lists.append(item[u'IDurl'])
    return lists

def parseUserInfo(html, weiboUserDoc, url):
    soup = etree.HTML(html)
    item = {}
    #用户ID, 性别， 关注人数， 粉丝数， 微博发布总数， 微博认证， 微博会员等级， 简介
    try:
        item[u'微博ID'] = soup.xpath('//h1[@class]/text()')[0].strip()
        item[u'简介'] = soup.xpath('//div[@class="pf_intro"]/text()')[0].strip()
        item[u'性别'] = soup.xpath('//div[@class="pf_username"]//i/@class')[0].strip()
        if u'female' in item[u'性别']:
            item[u'性别'] = u'女'
        elif u'male' in item[u'性别']:
            item[u'性别'] = u'男'
        else:
            pass
        item[u'关注人数'] = soup.xpath('//table[@class="tb_counter"]//td[1]//strong/text()')[0].strip()
        item[u'粉丝数'] = soup.xpath('//table[@class="tb_counter"]//td[2]//strong/text()')[0].strip()
        item[u'微博发布总数'] = soup.xpath('//table[@class="tb_counter"]//td[3]//strong/text()')[0].strip()
        item[u'微博认证'] = soup.xpath('//a[contains(@class, "W_icon icon_verify_v")]')
        if item[u'微博认证']:
            item[u'微博认证'] = soup.xpath('//p[@class="info"]/span/text()')[0].strip()
        else:
            item[u'微博认证'] = ''
        item[u'微博会员等级'] = soup.xpath('//a[contains(@class, "W_icon_level icon_level")]/span/text()')[0].strip()
        item[u'url'] = url
        weiboUserDoc.insert(item)
        print u'i got you!!!!!!!!!!!'
    except Exception, e:
        print e

def loginWeibo():
    browser = webdriver.Firefox()
    cookies = {
               u'_s_tentry': u'www.reader8.cn',
                u'Apache':u'7199318949133.158.1451545382799',
                u'SINAGLOBAL':u'7199318949133.158.1451545382799',
                u'ULV':u'1451545382808:1:1:1:7199318949133.158.1451545382799',
                u'SWB':u'usrmdinst_22',
                u'__gads':u'ID=defe4b80a24dbd18:T=1452417495:S=ALNI_MagE-uWsuOVNNW91-mjlyg1raLvwQ',
                u'login_sid_t':u'9867586d2eae3f79b099f86fe0e0e472',
                u'wvr':u'6',
                u'WBStore':u'5955be0e3d5411da|undefined',
                u'SSOLoginState':u'1453014708',
                u'WBtopGlobal_register_version':u'13cabfd94e1f5a1a',
                u'SUS':u'SID-3889451528-1453014770-GZ-571sq-fd18c51292b929d892a9891b146e6fcc',
                u'SUE':u'es%3D154092fcbc8f6edf73ad0250c90231f5%26ev%3Dv1%26es2%3D2b6424ab044b66166cb654863e0bb5a2%26rs0%3DSFcpCOum3cIODCT3x%252B3zOCG128%252F1y2k2SFzlgrAKdh4Uv6eWyaZ6dgQ9RkwCgkAl4gkUSCbhVd0gNVho255Pj75xvN6hD%252BSgGe6TI%252FmutTbDrUbBQ9sZ3DHYKIE299wyJZBJckwxL5YNOZKkwJUm0GIHZGPWo6PbjkY8hi9Tm7U%253D%26rv%3D0',
                u'SUP':u'cv%3D1%26bt%3D1453014770%26et%3D1453101170%26d%3Dc909%26i%3D6fcc%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D2%26st%3D0%26uid%3D3889451528%26name%3D274197603%2540qq.com%26nick%3DAllen_CHM%26fmp%3D%26lcp%3D2013-11-19%252018%253A00%253A52',
                u'SUB':u'_2A257n06iDeRxGeVG41sV9S_JyTSIHXVY7SdqrDV8PUNbuNBeLVjkkW9LHeufwVcIzdsLtK9R1aGxAShkxHMqjQ..',
                u'SUBP':u'0033WrSXqPxfM725Ws9jqgMF55529P9D9WW3QNsgxKgdBLxe4P35iY_L5JpX5K2t',
    }
    browser.add_cookie(cookies)
    browser.get(u'http://s.weibo.com/weibo/%25E8%25BD%25AC%25E5%259F%25BA%25E5%259B%25A0%25E9%25A3%259F%25E5%2593%2581&nodup=1')
    time.sleep(10)
    browser.find_element_by_xpath(u'//p[@class="tips_co"]//a[@action-type="login"]').click()
    time.sleep(10)
    browser.find_element_by_xpath(u'//div[@class="tab_bar"]//a[@node-type="login_tab"]').click()
    time.sleep(5)
    browser.find_element_by_xpath(u'//div[@node-type="username_box"]//input[@class="W_input"]').send_keys(accountNumber)
    browser.find_element_by_xpath(u'//div[@node-type="password_box"]//input[@class="W_input"]').send_keys(password)
    raw_input('ok')
    # browser.find_element_by_xpath(u'//div[@class="item_btn"]//a[@action-type="btn_submit"]').click()
    time.sleep(10)
    return browser

def getPage(browser, url):
    print url
    browser.get(url)
    time.sleep(random.uniform(8, 15))
    return browser

def savePage(url, resource):
    fileName = u'./searchPage/' + hashlib.md5(url).hexdigest() + u'.html'
    with codecs.open(fileName, u'w', u'utf-8') as f:
        f.write(resource)

def saveUserPage(url, resource):
    fileName = u'./userInfo/' + hashlib.md5(url).hexdigest() + u'.html'
    with codecs.open(fileName, u'w', u'utf-8') as f:
        f.write(resource)


conn = pymongo.MongoClient(u'192.168.0.181')
db = conn[u'test']
weiboDoc = db[u'weibo']
weiboUserDoc = db[u'weiboUser']
browser = loginWeibo()
browser = getPage(browser, u'http://s.weibo.com/weibo/%25E8%25BD%25AC%25E5%259F%25BA%25E5%259B%25A0%2520%25E9%25A3%259F%25E5%2593%2581&b=1&nodup=1&page=1')
while True:
    current_url = browser.current_url
    try:
        tmpHtml = browser.page_source
        savePage(browser.current_url, tmpHtml)
        lists = parsePageInfo(tmpHtml)  #处理搜索页面，返回用户url
        for url in lists:
            url = url.split(u'?')[0]
            if not weiboUserDoc.find({u'url':url}).count():
                browser = getPage(browser, url)
                time.sleep(2)
                tmpHtml = browser.page_source
                saveUserPage(browser.current_url, tmpHtml)
                parseUserInfo(tmpHtml, weiboUserDoc, url)
                browser = getPage(browser, current_url)
        if u'page=50' in browser.current_url:
            break
        browser.find_element_by_xpath('//div[@class="W_pages"]//a[contains(@class, "next")]').click()
    except Exception, e:
        print e
browser.quit()



