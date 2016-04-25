# -*- coding:utf-8 -*-  
#author: pxd
from django.core.mail import EmailMessage
from . import account
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def send_register_mail(username, password, tenant_id, email):
	title = "帐号激活邮件"
	token = account.get_register_token(username, email, password, tenant_id)
	url = "http://10.108.125.20/horizon/auth/register/validate/%s/"% token

	html_content = "<p>亲爱的用户 <b>"+username+"<b>: 您好！<br>您只需要点击下面链接，便可以激活您的帐号。<br><a href='"+url+"'>"+url+"</a><br>如果以上链接无法点击，请将它复制到您的浏览器地址栏中进入访问，该链接24小时内有效。</p>"
	msg = EmailMessage(title, html_content, to=[email])
	msg.content_subtype = "html"
	res = msg.send()
	return res


def send_reset_mail(to_mail):
	username = account.get_user_name_by_email(to_mail)
	token = account.get_reset_token(to_mail)
	url = "http://10.108.125.20/horizon/auth/reset/validate/%s/"% token
	
	title = "重置密码"
	html_content = "<p>用户名: "+username + "<br>重置密码请点击这里：<a href='"+url+"'>"+url+"</a><br>如果以上链接无法点击，请将它复制到您的浏览器地址栏中进入访问<br>如果你没有要求过重设密码，请直接忽略这个邮件。</p>"
	msg = EmailMessage(title, html_content, to=[to_mail])
	msg.content_subtype = "html"
	res = msg.send()
	return res
