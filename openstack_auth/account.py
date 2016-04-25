#author:pxd
from keystoneclient.v2_0 import client
import urllib2
import json
import MySQLdb
from random import choice
import string
from datetime import *

def get_db_connector():
	return MySQLdb.connect(host='localhost', user='root', passwd='secret', db='keystone')

def set_db_close(conn, cur):
	conn.commit()#submit to database
	cur.close()
	conn.close()

#execute without return record
def query_exec(query_str):
	try:
		conn = get_db_connector()

		cur = conn.cursor()
		cur.execute(query_str)

		set_db_close(conn, cur)
	except MySQLdb.Error, e:
		conn.rollback()
		print "Error %d: %s" % (e.args[0], e.args[1])

#return one record
def query_one(query_str):
	try:
		conn = get_db_connector()

		cur = conn.cursor()
		cur.execute(query_str)
		record = cur.fetchone()

		set_db_close(conn, cur)

		return record
	except MySQLdb.Error, e:
		conn.rollback()
		print "Error %d: %s" % (e.args[0], e.args[1])

#return all records
def query_all(query_str):
	try:
		conn = get_db_connector()

		cur = conn.cursor()
		cur.execute(query_str)
		records = cur.fetchall()

		set_db_close(conn, cur)

		return records
	except MySQLdb.Error, e:
		conn.rollback()
		print "Error %d: %s" % (e.args[0], e.args[1])

def get_user_name_by_email(email):
	query_str = "select extra, name from user"
	records = query_all(query_str)

	for record in records:
		if record[0] == '{"email": "%s"}' % email:
			return record[1]
	return 0

def get_user_id_by_name(username):
	query_str = "select id from user where name='%s'" % username
	record = query_one(query_str)

	if record == None:
		return 0
	else:
		return record[0]

def exist_username(username):
	query_str = "select id from user where name= '%s'" % username #name= %s is wrong!!!! it should be name= '%s'
	record = query_one(query_str)

	if record == None:
		return 0
	else :
		return 1

#check the keystone user table to see if already exists the username
def exist_email(email):
	query_str = "select extra from user"
	records = query_all(query_str)

	for record in records:
		if record[0] == '{"email": "%s"}' % email:
			return 1
	return 0

def exist_tenant(tenant_id):
	query_str = "select id from project where id='%s'" % tenant_id
	record = query_one(query_str)

	if record == None:
		return 0
	else :
		return 1

#check the validate_code table to see if username already exists
def exist_validate_username(username):
	query_str = "select id from validate_code where name= '%s'" % username
	record = query_one(query_str)

	if record == None:
		return 0
	else :
		return 1

def exist_validate_email(email):
	query_str = "select id from validate_code where email= '%s'" % email
	record = query_one(query_str)

	if record == None:
		return 0
	else :
		return 1

def exist_username_all(username):
	res = exist_username(username)+exist_validate_username(username)
	return res

def exist_email_all(email):
	res = exist_email(email)+exist_validate_email(email)
	return res

def get_keystone_client():
	url = 'http://10.108.125.20:5000/v2.0/tokens'
	values = {
	    "auth": {
	        "tenantName": "admin",
	        "passwordCredentials":
	            {
	                "username": "admin",
	                "password": "secret"}}}
	data1 = json.dumps(values)
	req1 = urllib2.Request(url, data1)
	req1.add_header('Content-Type', 'application/json')
	response = urllib2.urlopen(req1)
	res = response.read()
	content = json.loads(res)
	token_id = content['access']['token']['id']
	endpoint = 'http://10.108.125.20:35357/v2.0'
	keystone = client.Client(token=token_id, endpoint=endpoint)
	return keystone

def create_user(username, password, email):
	info = exist_username(username) + exist_email(email);
	if info == 0:
		keystone = get_keystone_client()
		my_user = keystone.users.create(name=username,password=password,email=email, enabled=True)
		return my_user.id
	else :
		return 0

def create_tenant(tenant_name):
	keystone = get_keystone_client()
	my_tenant = keystone.tenants.create(tenant_name=tenant_name, description="created via dashboard registration", enabled=True)
	return my_tenant.id

def join_tenant(user_id, tenant_id):
	keystone = get_keystone_client()
	my_tenant = keystone.tenants.get(tenant_id)
	my_user = keystone.users.get(user_id)
	my_role = keystone.roles.get('9fe2ff9ee4384b1894a90878d3e92bab')#role:'_member'
	keystone.roles.add_user_role(my_user, my_role, my_tenant)
	return 1

def activate_user(user_id):
	keystone = get_keystone_client()
	my_user = keystone.users.get(user_id)
	keystone.users.update_enabled(user=my_user, enabled=True)
	return 1

#example: gen_password(8), param:'8' stands for the length of the password
def gen_password(length=8,chars=string.ascii_letters+string.digits):
	return ''.join([choice(chars) for i in range(length)])

def update_password(user_id, new_password):
	keystone = get_keystone_client()
	my_user = keystone.users.get(user_id)
	keystone.users.update_password(my_user, new_password)
	return 1

######create a table in your database use the following sql.
# CREATE TABLE `register_token` (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `username` varchar(40) NOT NULL,
#   `token` varchar(40) NOT NULL,
#   `expire_time` varchar(30) NOT NULL,
#   `email` varchar(30) NOT NULL,
#   `tenant_id` varchar(64),
#   `password` varchar(30) NOT NULL,
#   PRIMARY KEY (`id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
format = "%Y-%m-%d %H:%M:%S"
def get_register_token(username, email, password, tenant_id):
	token = gen_password(30)
	now = datetime.now()
	day = now.day
	expire_time = now.replace(day=day+1)
	et_str = expire_time.strftime(format)
	query_str = "insert into register_token (username, token, expire_time, email, tenant_id, password) values('%s','%s','%s','%s','%s','%s')"% (username, token, et_str, email, tenant_id, password)
	query_exec(query_str)
	return token

def validate_register_url(token):
	query_str = "select * from register_token where token='%s'" % token
	record = query_one(query_str)
	if record == None:
		return False
	username=record[1]
	email=record[4]
	tenant_id=record[5]
	password=record[6]
	expire_time = datetime.strptime(record[3], format)
	now = datetime.now()
	query_str = "delete from register_token where token='%s'" % token
	query_exec(query_str)
	if now<expire_time:#after email activate, then truely create user and tenant
		create_user(username, password, email)
		if tenant_id=="":
			tenant_id=create_tenant("tenant-"+username)
		user_id = get_user_id_by_name(username)
		join_tenant(user_id, tenant_id)
		return True
	else:
		return False

######create a table in your database use the following sql.
# CREATE TABLE `reset_token` (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `email` varchar(30) NOT NULL,
#   `token` varchar(40) NOT NULL,
#   PRIMARY KEY (`id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
def get_reset_token(email):
	token = gen_password(30)
	query_str = "insert into reset_token (email, token) values('%s','%s')"% (email, token)
	query_exec(query_str)
	return token

def validate_reset_url(token):
	query_str = "select * from reset_token where token='%s'" % token
	record = query_one(query_str)
	if record == None:
		return False
	email=record[1]
	username = get_user_name_by_email(email)
	user_id = get_user_id_by_name(username)
	query_str = "delete from reset_token where token='%s'" % token
	query_exec(query_str)
	return user_id
