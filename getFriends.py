# coding:utf-8

import re,urllib2,urllib,cookielib,json,csv,time
from BeautifulSoup import BeautifulSoup
from HTMLParser import HTMLParser
import htmlentitydefs
import sys

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

#反转义函数
def unescape(text):
	def fixup(m):
		text = m.group(0)
		if text[:2] == "&#":
			# character reference
			try:
				if text[:3] == "&#x":
					return unichr(int(text[3:-1], 16))
				else:
					return unichr(int(text[2:-1]))
			except ValueError:
				print "erreur de valeur"
				pass
		else:
			# named entity
			try:
				if text[1:-1] == "amp":
					text = "&amp;amp;"
				elif text[1:-1] == "gt":
					text = "&amp;gt;"
				elif text[1:-1] == "lt":
					text = "&amp;lt;"
				else:
					print text[1:-1]
					text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
			except KeyError:
				print "keyerror"
				pass
		return text # leave as is
	return re.sub("&#?\w+;", fixup, text)


def strip_tags(html):
    html = html.strip()
    html = html.strip("\n")
    result = []
    parse = HTMLParser()
    parse.handle_data = result.append
    parse.feed(html)
    parse.close()
    return "".join(result)

cookie = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

#登陆设定
email = ''
pwd   = ''

#
logurl = "http://www.renren.com/PLogin.do"
postdata = "email="+email+"&password="+pwd+"&origURL=http%3A%2F%2Fwww.renren.com%2FSysHome.do&domain=renren.com"
request = urllib2.Request(logurl,postdata)
response = opener.open(request).read()

#首页本地保存 验证登陆
# mpg = file('homedo1.html','a+')
# mpg.write(response)
# mpg.close()

#搜索设定
url = "http://browse.renren.com/searchEx.do"
university = "哈工程"
univ_id = "3002"
depart = "核科学与技术学院"
year = "2009"

#新建csv
writer = csv.writer(file('1.csv', 'wb'))
writer.writerow(['name','id','sch','img_default','img_star','img_url'])

#循环搜索
for i in range(1):
	post_data = {
		 'ajax':1,
		 's':0,
		 'act':'search',
		 'p':'[{"t":"univ","name":'+university+',"id":'+univ_id+',"depart":'+depart+',"year":'+year+'}]',
		 # 'p':'[{"t":"univ","name":'+university+',"id":'+univ_id+',"depart":'+depart+'}]',
		 'offset':10*i,
	}
	req = urllib2.Request(url, urllib.urlencode(post_data))
	res = opener.open(req).read()

	#本地保存网页 用于检查
	# mpg = file('hpeop'+str(i)+'.html','a+')
	# mpg.write(res)
	# mpg.close()

	#页面查找并写入
	soup = BeautifulSoup(res)
	ul = soup.findAll('ul')
	for a in range(len(ul)):
		ul[a].li.extract()
	li = soup.findAll('li')
	for e in range(len(li)):
		#头像
		img = li[e].find('img')
		img_default = 'no'
		if img != None:
			# img_url = img['src']
			img_url = str(img).split('"')[1]	#另一种找img
			if img_url == 'http://head.xiaonei.com/photos/0/0/men_head.gif':
				img_default = 'yes'

		#姓名
		dd = li[e].findAll('dd')
		name = dd[0].find('a').text
		# name = li[e].div.dl.dd.a.text		#另一种找name
		name = unescape(name)	#名字是被html转义过的 用unescape()函数进行反转义

		#ID
		uid = li[e].find('a')['href']
		uid = str(uid).split('=')[2].split('&')[0]

		#头像认证
		img_star = dd[0].findAll('a')
		try:
			if img_star[1] != None:
				img_star = 'yes'
		except:
			img_star = 'no'

		#学校
		sch_none = ''
		try:
			sch = str(dd[1])
			sch = strip_tags(sch).replace(' ','').replace('\n\n\n',',').replace('\n\n','')	#对多个学校名间的html进行处理
			writer.writerow([name,uid,sch,img_default,img_star,img_url])	#写入csv
		except:		#有些人没有学校信息
			writer.writerow([name,uid,sch_none,img_default,img_star,img_url])
	
	time.sleep(0.5)