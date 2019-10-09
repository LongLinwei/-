# -*- coding: utf-8 -*-
import requests
import itchat
from  itchat.content import *
import os
from PIL import Image
import math
import os.path
import wordcloud
# from scipy.misc import imread
import sys
import json
import collections
from random import choice
from aip import AipFace
import base64
import smtplib
from email.mime.text import MIMEText

robot_reply=False

robot_chat=False

mass_set=False
mass_model=None

auto_reply=False
auto_reply_set=False
auto_reply_content=None

source_search=False

source_send=False

repeat=False
repeat_num=0

r_choice=False

face_level=False

send_email=False
email_info={}
email_sure=False
diary_open=False

@itchat.msg_register(PICTURE)
def picture_save(msg):
	
	friend=msg['FromUserName']
	if friend==myusername and msg['ToUserName']=="filehelper" and face_level:
		msg['Text']('颜值.jpg')
		try:
			score=detection('颜值.jpg')
			if score is None:
				itchat.send('检测不到人脸',toUserName='filehelper')
				return
		except Exception as e:
			itchat.send(f'格式错误：{e}',toUserName='filehelper')
			return
		else:
			itchat.send(f'颜值得分：{score}',toUserName='filehelper')
			itchat.send('您可以继续上传，或输入“t#13”退出',toUserName='filehelper')
			return
			

	if not os.path.exists('保存图片'):
		os.mkdir('保存图片')
	
	if friend==myusername and msg['ToUserName']=="filehelper":
		msg['Text']("保存图片/"+msg['FileName'])

@itchat.msg_register(ATTACHMENT)
def picture_save(msg):
	if not os.path.exists('保存文件'):
		os.mkdir('保存文件')
	friend=msg['FromUserName']
	if friend==myusername and msg['ToUserName']=="filehelper":
		msg['Text']("保存文件/"+msg['FileName'])

@itchat.msg_register(VIDEO)
def picture_save(msg):
	if not os.path.exists('保存视频'):
		os.mkdir('保存视频')
	friend=msg['FromUserName']
	if friend==myusername and msg['ToUserName']=="filehelper":
		msg['Text']("保存视频/"+msg['FileName'])


@itchat.msg_register([TEXT,SHARING])
def choice_menu(msg):
	# print(msg)
	global robot_chat,robot_reply,mass_set,auto_reply,auto_reply_set,auto_reply_content,source_search,source_send,repeat,repeat_num,r_choice,face_level,mass_model,send_email,email_sure,diary_open
	switch=[robot_chat,robot_reply,mass_set,auto_reply_set,auto_reply,source_search,source_send,repeat,r_choice,face_level,send_email,diary_open]
	text=msg['Text']
	friend=msg['FromUserName']
	if friend==myusername and msg['ToUserName']=="filehelper":
		
		if text in ['关键词','#0']:
			itchat.send(detail,toUserName='filehelper')
		elif text=='退出' and any(switch):			
			robot_reply=False
			robot_chat=False
			mass_set=False
			mass_model=None
			auto_reply=False
			auto_reply_set=False
			auto_reply_content=None
			source_search=False
			source_send=False
			repeat=False
			repeat_num=0
			r_choice=False
			face_level=False
			send_email=False
			email_info={}
			email_sure=False
			diary_open=False
			itchat.send('已退出',toUserName='filehelper')
		elif text in ['自动回复','#1'] and not any(switch):
			auto_reply_set=True
			itchat.send("请输入自动回复模板",toUserName='filehelper')
		elif auto_reply_set:		
			auto_reply_content=msg['Text']
			auto_reply=True
			auto_reply_set=False
			itchat.send("设置成功",toUserName='filehelper')
		elif text in ['退出自动回复','t#1'] and auto_reply:
			auto_reply=False
			itchat.send("自动回复已关闭",toUserName='filehelper')
			auto_reply_content=None

		elif text in ['小灵回复','#2'] and not any(switch):
			robot_reply=True
			itchat.send("开启小灵回复成功",toUserName='filehelper')
		elif text in ['退出小灵回复','t#2'] and robot_reply:
			robot_reply=False
			itchat.send("小灵回复已关闭",toUserName='filehelper')

		elif text in ['小灵聊天','#3'] and not any(switch):
			robot_chat=True
			itchat.send("开启小灵聊天成功，快来和我聊天吧",toUserName='filehelper')
		elif text in ['退出小灵聊天','t#3'] and robot_chat:
			robot_chat=False
			itchat.send("小灵聊天已关闭",toUserName='filehelper')
		elif robot_chat:
			resp=tlresp(text,msg['FromUserName'])
			itchat.send(resp,toUserName='filehelper')

		elif text in ['群发','#4'] and not any(switch):
			mass_set=True
			itchat.send("请设置群发模板，使用'@name'添加名字，如'@name,新年快乐'，@name将提取好友备注或呢称",toUserName='filehelper')
		elif mass_set and mass_model is None:
			mass_model=text
			to_doc=""	
			for friend in friend_list[:5]:
				name=friend['RemarkName'] or friend['NickName']
				doc=mass_model.replace("@name",name)
				to_doc+=doc+';'
				# itchat.send(doc,toUserName=friend['UserName'])
			itchat.send(f'前五个群发格式如下：\n{to_doc}\n请确定是否发送（是或否）',toUserName='filehelper')
		elif mass_set and mass_model:
			if text=='是':
				num=0
				for friend in friend_list:
					name=friend['RemarkName'] or friend['NickName']
					doc=mass_model.replace("@name",name)
					itchat.send(doc,toUserName=friend['UserName'])
					# itchat.send(doc,toUserName='filehelper')
					num+=1
				mass_set=False
				mass_model=None
				itchat.send(f"群发完成,共发送消息{num}条",toUserName='filehelper')
			else:
				mass_set=False
				mass_model=None
				itchat.send("已取消群发",toUserName='filehelper')

		elif text in ['关机','#5']:
			itchat.send("关机命令执行成功，电脑将在一分钟后关机",toUserName='filehelper')
			os.system('shutdown -s -t 60')
		elif text in ['取消关机','t#5']:
			itchat.send("关机命令已取消",toUserName='filehelper')
			os.system('shutdown -a')
			

		elif text in ['名字云图','#6']:
			itchat.send("好友名字获取中，请等待...",toUserName='filehelper')
			non_bmp_map=dict.fromkeys(range(0x10000,sys.maxunicode+1),0xfffd)
			lt=[]

			for friend in friend_list:
				friend_nickname=friend['NickName'].translate(non_bmp_map)
				lt.append(friend_nickname)
			itchat.send("好友名字获取成功，名字词云制作中",toUserName='filehelper')
			w=wordcloud.WordCloud(font_path='msyh.ttc',\
                          background_color="white",max_words=500,width=800,height=1200)
			text=" ".join(lt)
			w.generate(text)
			w.to_file(f'{nickname}名字词云.jpg')
			itchat.send_image(f'{nickname}名字词云.jpg',toUserName='filehelper')

		elif text in ['男女比例','#8.1']:
			tol_num=len(friend_list)
			man_num=0
			madam_num=0
			unknow_num=0
			for friend in friend_list:
				if friend['Sex']==1:
					man_num+=1
				elif friend['Sex']==2:
					madam_num+=1
				else:
					unknow_num+=1
			
			itchat.send(f'您的好友总数为：{tol_num}人(不包含您自己)，其中男生{man_num}人，女生{madam_num}人，保密{unknow_num}人',toUserName='filehelper')

		elif text in ['地区分布','#8.2']:
			province_lst=[]
			city_lst=[]
			itchat.send('城市分布计算中，请稍候...',toUserName='filehelper')
			for friend in friend_list:
				province_lst.append(friend['Province'])
				city_lst.append(friend['City'])
			w1=wordcloud.WordCloud(font_path='msyh.ttc',\
                          background_color="white",max_words=500,width=800,height=1200)
			text1=" ".join(province_lst)
			w1.generate(text1)
			w1.to_file('province.jpg')

			w2=wordcloud.WordCloud(font_path='msyh.ttc',\
                          background_color="white",max_words=500,width=800,height=1200)
			text2=" ".join(city_lst)
			w2.generate(text2)
			w2.to_file('city.jpg')

			province_count=[f'{i[0]}:{i[1]}' for i in sorted(list(collections.Counter(province_lst).items()),key=lambda x:x[1],reverse=True) if i[0]]
			city_count=[f'{i[0]}:{i[1]}' for i in sorted(list(collections.Counter(city_lst).items()),key=lambda x:x[1],reverse=True) if i[0]]

			province_text="\n".join(province_count)
			city_text='\n'.join(city_count)
			itchat.send(f'省分布：\n{province_text}',toUserName='filehelper')
			itchat.send_image('province.jpg',toUserName='filehelper')
			itchat.send(f'城市分布：\n{city_text}',toUserName='filehelper')
			itchat.send_image('city.jpg',toUserName='filehelper')
		elif text in ['个性签名','#8.3']:
			signature_list=[]
			num=0
			for friend in friend_list:
				signature=friend['Signature']
				if signature:
					signature_one=friend['NickName']+' : '+signature
					signature_list.append(signature_one)
					num+=1
					if num%30==0:
						signature_text='\n'.join(signature_list)
						itchat.send(signature_text,toUserName='filehelper')
						signature_list.clear()


		elif text in ['好友墙','#7']:			
			if not os.path.exists(nickname):
				friend_num=len(friend_list)
				itchat.send(f"获取好友头像中，您一共有{friend_num}位好友，获取时间较长，请等待...",toUserName='filehelper')
				os.mkdir(nickname)
				num=0
				for friend in friend_list:
				    img = itchat.get_head_img(userName=friend["UserName"])
				    fileImage = open(nickname + "/" + str(num) + ".jpg",'wb')
				    fileImage.write(img)
				    fileImage.close()
				    num += 1
				    if num%50==0:
				    	itchat.send(f"已获取{num}张头像",toUserName='filehelper')

			itchat.send("好友头像获取成功，准备进行头像拼接",toUserName='filehelper')
			img_joint(nickname)
			itchat.send_image(f'{nickname}好友墙.jpg',toUserName='filehelper')

		elif text in ['电脑资源','#9'] and not any(switch):
			itchat.send('请输入您要查询的电脑路径（如“E:\文档\微信”）',toUserName='filehelper')
			source_search=True
		elif text in ['退出电脑资源','t#9'] and source_search:
			source_search=False
			itchat.send('电脑资源查询已关闭',toUserName='filehelper')
		elif source_search:
			try:
				source_lst=os.listdir(text)
			except:
				itchat.send('路径格式错误或路径不存在,请重新输入',toUserName='filehelper')
			else:
				source_text='\n'.join(source_lst)
				itchat.send(source_text,toUserName='filehelper')
		elif text in ['文件传输','#10'] and not any(switch):
			itchat.send('请输入您要传输文件的电脑路径（如“E:\文档\微信\info.txt”）',toUserName='filehelper')
			source_send=True
		elif text in ['退出传输','t#10']:
			itchat.send('文件传输已关闭',toUserName='filehelper')
			source_send=False
		elif source_send:
			if os.path.exists(text):
				itchat.send_file(text,toUserName='filehelper')
				source_send=False
				itchat.send('文件传输已关闭',toUserName='filehelper')
			else:
				itchat.send('文件不存在或格式错误，请重新输入',toUserName='filehelper')
				return

		elif text in ['复读机','#11'] and not any(switch):
			itchat.send('请输入您要重复的次数',toUserName='filehelper')
			repeat=True
		elif repeat and repeat_num==0:
			try:
				repeat_num=int(text)
			except:
				itchat.send('请输入一个整数',toUserName='filehelper')
			else:
				itchat.send(f'复读机开启成功，重复次数为{repeat_num}次',toUserName='filehelper')
		elif text in ['退出复读机','t#11']:
			repeat=False
			repeat_num=0
			itchat.send('复读机已关闭',toUserName='filehelper')

		elif text in ['随机选择','#12'] and not any(switch):
			r_choice=True
			itchat.send('请输入您要选择的选项，用中文逗号分隔开，如“黄焖鸡米饭，沙县小吃，兰州拉面”',toUserName='filehelper')
		elif r_choice:
			choice_list=text.split("，")
			choice_result=choice(choice_list)
			itchat.send(f'听我的，选{choice_result}就对了',toUserName='filehelper')
			r_choice=False
		elif text in ['颜值打分','#13'] and not any(switch):
			itchat.send(f'请上传一张图片',toUserName='filehelper')
			face_level=True
		elif text in ['退出颜值','t#13']:
			itchat.send('颜值打分已关闭',toUserName='filehelper')
			face_level=False
		elif text in ['发送邮件','#14'] and not any(switch):
			with open('邮箱配置.txt','r') as f:
				try:
					email_info['sender']=f.readline().split('：')[1].strip()
					email_info['psw']=f.readline().split('：')[1].strip()
					# print(email_info['sender'],email_info['psw'])
				except:
					itchat.send('请先在邮箱配置文件中配置您的账号信息，并检查格式是否有误',toUserName='filehelper')
					return
			itchat.send('请输入接收者邮箱账号，若有多个请用英文逗号隔开',toUserName='filehelper')
			send_email=True
		elif text in ['退出邮箱','t#14']:
			itchat.send('邮箱已关闭',toUserName='filehelper')
			send_email=False
			email_info.clear()
		elif send_email and email_info.get('receviers',None) is None:
			email_info['receviers']=text.split(',')
			# if len(email_info['receviers'])==1:
			# 	email_info['receviers']=email_info['receviers'][0]
			itchat.send('请输入标题',toUserName='filehelper')
		elif send_email and email_info.get('receviers',None) and email_info.get('title',None) is None:
			email_info['title']=text
			itchat.send('请输入正文内容',toUserName='filehelper')
		elif send_email and email_info.get('receviers',None) and email_info.get('title',None) and email_info.get('content',None) is None:
			email_info['content']=text
			itchat.send('邮件标题:{}\n发送者{}\n接收者:{}\n邮件内容:{}\n请确定是否发送（是或否）'.format(email_info['title'],email_info['sender'],','.join(email_info['receviers']),email_info['content']),toUserName='filehelper')
			email_sure=True
		elif send_email and email_sure:
			if text=='是':
				email_send()
				if email_info['status']:
					itchat.send('邮件发送成功',toUserName='filehelper')
				else:
					itchat.send('邮件发送失败，请检查授权码及邮件内容',toUserName='filehelper')
				send_email=False
				email_sure=False
				email_info.clear()
			else:
				itchat.send('邮件已取消',toUserName='filehelper')
				send_email=False
				email_sure=False
				email_info.clear()
		elif text in ['日记','#15'] and not any(switch):
			itchat.send('请输入日记内容',toUserName='filehelper')
			diary_open=True
		elif text in ['退出日记','t#15']:
			itchat.send('日记已保存，关闭成功',toUserName='filehelper')
			diary_open=False
		elif diary_open:
			with open("日记.txt",'a',encoding='utf8') as f:
				f.write(text+'\n\n')

		

		elif any(switch):
			itchat.send('若您想使用其他功能，请先退出正在运行的功能',toUserName='filehelper')
			
		else:
			itchat.send('没有此功能',toUserName='filehelper')



	elif repeat and repeat_num!=0 and friend==myusername:
		for i in range(repeat_num-1):
			itchat.send(text,toUserName=msg['ToUserName'])
	elif friend==myusername and msg['ToUserName']!="filehelper":
		return
	elif auto_reply:
		itchat.send(auto_reply_content,toUserName=msg['FromUserName'])
	elif robot_reply:
		resp=tlresp(text,msg['FromUserName'])
		itchat.send(resp,toUserName=msg['FromUserName'])

	else:
		return

def img_joint(nickname):
	img_list=os.listdir(nickname)
	img_list_len=len(img_list)
	size=int(math.sqrt((640*640)/img_list_len))
	numline=int(640/size)
	new_img=Image.new('RGB',(size*numline,size*numline))
	x,y=0,0
	for i in img_list:
		try:
			img=Image.open(f"{nickname}/{i}")
		except:
			print("没有找到图片"+i)
		else:
			img=img.resize((size,size),Image.ANTIALIAS)
			new_img.paste(img,(x*size,y*size))
			x+=1
			if x==numline:
				y+=1
				x=0
			
		new_img.save(f'{nickname}好友墙.jpg')



def tlresp(text,userid):
	# print(text)
	data={
	"reqType":0,
    "perception": {
        "inputText": {
            "text": text
        },
        "inputImage": {
            "url": "imageUrl"
        },
        "selfInfo": {
            "location": {
                "city": "北京",
                "province": "北京",
                "street": "信息路"
            }
        }
    },
    "userInfo": {
        "apiKey": KEY,
        "userId": userid[1:10]
    }
}
	# data=json.dumps(data).encode('utf-8')
	# print(data)
	# 我们通过如下命令发送一个post请求
	data=json.dumps(data)
	# print(data)
	r = requests.post(apiUrl, data=data).json()
	# 让我们打印一下返回的值，看一下我们拿到了什么
	# print(r)
	return r['results'][0]['values']['text']

def detection(path):
	""" 你的 APPID AK SK """
	APP_ID = '16918274'
	API_KEY = '8LPSpFQpG1WTSTP77arZKTFG'
	SECRET_KEY = 'Me1HVHyWjm6sPSluFBGeNHGTYZQNbcyf'
		
	client = AipFace(APP_ID, API_KEY, SECRET_KEY)
	with open(path,'rb') as f:
		# print(f.read())
		data=base64.b64encode(f.read())
	# exit()
	image = data.decode()
	imageType = "BASE64"

	""" 调用人脸检测 """
	# client.detect(image, imageType);

	""" 如果有可选参数 """
	options = {}
	options["face_field"] = "beauty"
	# options["max_face_num"] = 2
	# options["face_type"] = "LIVE"
	# options["liveness_control"] = "LOW"

	""" 带参数调用人脸检测 """
	response=client.detect(image, imageType, options)
	# print(response)
	if response['error_code']!=0:
		print('失败',response['error_code'])
	else:
		return response['result']['face_list'][0]['beauty']
def email_send():
	msg_from=email_info['sender']                                 #发送方邮箱
	passwd=email_info['psw']                                  #填入发送方邮箱的授权码
	msg_to=','.join(email_info['receviers'])                                      #收件人邮箱

	subject=email_info['title']                                     #主题     
	content=email_info['content']
	msg = MIMEText(content)
	msg['Subject'] = subject
	msg['From'] = msg_from
	msg['To'] = msg_to
	try:
	    s = smtplib.SMTP_SSL("smtp.qq.com",465)				#邮件服务器及端口号
	    s.login(msg_from, passwd)                               #登录SMTP服务器
	    s.sendmail(msg_from, msg_to, msg.as_string())#发邮件 as_string()把MIMEText对象变成str
	    # print ("发送成功")
	    email_info['status']=True
	except Exception as e:
	    print (e)
	    email_info['status']=False
	finally:
	    s.quit()



apiUrl = 'http://openapi.tuling123.com/openapi/api/v2'
KEY='0f6de175d48a44c4bc007d228982d2b0'
# userid='12'

itchat.auto_login()
# itchat.auto_login()
myusername=itchat.get_friends()[0]['UserName']
nickname=itchat.get_friends()[0]['NickName']
# print(myusername)
friend_list=itchat.get_friends()[1:]
# for friend in friend_list[:1]:
# 	print('\n'.join([f'{i[0]} : {i[1]}' for i in list(friend.items())]))


opening='''欢迎使用微信脚本，现在脚本具备以下功能：

以下关键词都有对应代码，在文件传输助手中，输入“关键词”或“#0”，即可查看对应关键词的代码，输入代码即能调用功能
1.自动回复：
在文件传输助手中，输入“自动回复”，设置自动回复内容，即可开启自动回复，如需退出请输入“退出自动回复”
2.创建一个机器人自动回复：
在文件传输助手中，输入“小灵回复”，脚本将生成一只聊天机器人“小灵”，你的好友发消息给你时，小灵将与其聊天，如需退出请输入“退出小灵回复”
3.创建一个机器人聊天：
在文件传输助手中，输入“小灵聊天”，脚本将生成一只聊天机器人“小灵”，她只会在文件传输助手中和你聊天，不会回复其他好友的消息,如需退出请输入“退出小灵聊天”
4.群发助手：
微信本身的群发助手无法添加姓名，一眼就能看出群发，这个群发助手能帮助你在内容中添加接收人的姓名，诚意满满，在文件传输助手中，输入“群发”开启
5.关闭电脑：
在文件传输助手中，输入“关机”，脚本会帮你将电脑关机，注意：关机后脚本也无法使用，取消关机请输入“取消关机”
6.生成一张好友名字云图
在文件传输助手中，输入“名字云图”，脚本将根据你的好友的昵称，形成一张好看的云图
7.生成一张好友墙图片
在文件传输助手中，输入“好友墙”，脚本将根据你的好友的头像，拼接形成一张大图
8.好友基本情况
在文件传输助手中，输入“男女比例”，将统计你的好友总数及男女比例；输入“地区分布”，将统计好友省分布及市分布，以词云返回；输入“个性签名”，将返回设置个性签名的好友名称及个性签名内容
9.查看电脑资源
在文件传输助手中，输入“电脑资源”，脚本将根据你输入文件路径查看电脑资源，退出请输入“退出电脑资源”
10.电脑文件传输
结合上面查看电脑资源的命令，您可以远程将电脑上的文件资源发送到手机上，在文件传输助手中，输入“文件传输”，脚本将根据你输入文件路径将电脑资源传输到您手机上，传输成功后将直接退出文件传输状态，如需在过程中退出请输入“退出传输“
11.重要事情说N次
在文件传输助手中，输入“复读机”，输入次数，之后你与朋友聊天时，每发出一句话都会被重复N次，退出请输入“退出复读机”
12.随机选择
你是否遇到午餐晚餐不知道吃什么好，周末不知道去哪玩好。在文件传输助手中，输入“随机选择”，用逗号将你的选择隔开，脚本将为您随机选择一个
13.上传图片、文件、视频
你在文件传输助手中上传的图片、文件及视频，脚本会帮你直接将其保存至电脑
14.颜值打分
在文件传输助手中，输入“颜值打分”，脚本会根据你上传的图片为你的颜值打分，退出请输入“退出颜值”
15.发送邮件
请先在邮箱配置文件中配置您的邮箱信息（目前仅支持qq邮箱）,然后在文件传输助手中，输入“发送邮件”，根据提示录入邮件信息以发送邮件
16.日记
在文件传输助手中，输入“日记”，将你想记录的文字输入，当“退出日记”后，会同步保存到电脑“日记.txt”文件中
'''

detail='''欢迎使用微信脚本,关键词对应代码如下：
关键词：	#0  
自动回复：#1  ；退出自动回复：t#1
小灵回复：#2  ；退出小灵回复：t#2
小灵聊天：#3  ；退出小灵聊天：t#3
群发：	#4  
关机：	#5  ；取消关机：	t#5
名字云图：#6
好友墙：  #7  
男女比例  #8.1：地区分布：	#8.2   ：个性签名：#8.3 
电脑资源  #9  ：退出电脑资源：t#9
文件传输 #10 ；退出传输：	t#10
复读机   #11 ；退出复读机：	t#11
随机选择 #12 
颜值打分 #13 ；退出颜值：	t#13
发送邮件 #14 ：退出邮件：	t#14
日记	 #15 ：退出日记：	t#15
'''

itchat.send(opening,toUserName='filehelper')
itchat.run(True)

