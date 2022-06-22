from django.shortcuts import render, redirect
from django.http.response import HttpResponse, JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
import smtplib,ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


import mysql.connector
from mysql.connector import Error

import json
import os

import sys
from subprocess import run,PIPE

import mimetypes
from django import forms

from django.conf import settings
from django.core.files.storage import FileSystemStorage
# Create your views here.

import psycopg2
import pandas as pd
import re
#import reverse_geocoder as rg

import urllib
from urllib import request
import requests
#from bs4 import BeautifulSoup
import time

def Homepage(request):
	items=[]
	price=[]
	item_path=[]
	dict={}
	
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')                                         
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			fetch_query="select item_name,price,item_path from items;"
			print(fetch_query)
			cursor.execute(fetch_query)
			records = cursor.fetchall()
			print(records)
			for i in range(0,len(records)):
				dict['product_no_'+str(i+1)]=records[i][0]
				dict['price_'+str(i+1)]=records[i][1]
				dict['item_path_'+str(i+1)]=records[i][2]
				items.append(records[i][0])
				price.append(records[i][1])
				item_path.append(records[i][2])
			connection.commit()
	except Error as e:
		print("Error while connecting to MySQL", e)
	finally:
		if (connection.is_connected()):
			cursor.close()
			connection.close()
			print("MySQL connection is closed")
	
	count_imgs=len(items)
	item_paths=''
	for i in range(1,(len(dict)//3)+1):
		item_paths=item_paths+(dict['item_path_'+str(i)])+','
	
	item_paths=item_paths[:len(item_paths)-1]
	dict['item_paths']=item_paths
	#print(item_paths)
	#print(dict)
	#count_imgs=40
	if(count_imgs>1000):
		count_imgs=1000
	dict['total_no_products']=count_imgs
	return render(request,'HomePage.html',dict)

def login(request):
	return render(request,'LoginPage.html')

def abt_cmpy(request):
	return render(request,'abtpage.html')

def rld_hmpg(request):
	return render(request,'HomePage.html',{'total_no_products':3})

def register(request):
	reg_usr= request.POST.get('reg_username')
	reg_email= request.POST.get('reg_email')
	reg_pass= request.POST.get('reg_password')
	reg_pass1= request.POST.get('reg_password1')
	reg_type= request.POST.get('UserAcct')
	if(reg_pass == reg_pass1):
		try:
			connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')                                         
			if connection.is_connected():
				db_Info = connection.get_server_info()
				print("Connected to MySQL Server version ", db_Info)
				cursor = connection.cursor()
				cursor.execute("select database();")
				record = cursor.fetchone()
				print(reg_usr+' '+reg_pass+' '+reg_email)
				if(reg_type=='User'):
					acct_status_Active='Active'
					fail_creation='Account Created'
				else:
					acct_status_Active='Inactive'
					fail_creation='Account requested and awaiting for admin approval'
				insrt_qry='insert into user_login values("'+reg_usr+'","'+reg_pass+'","'+reg_email+'","'+reg_type+'","'+acct_status_Active+'");'
				print(insrt_qry)
				cursor.execute(insrt_qry)
				connection.commit()
		except Error as e:
			print("Error while connecting to MySQL", e)
			usr_exist='Username Already Taken'
			return render(request,'LoginPage.html',{'fail_creation':usr_exist})
		finally:
			if (connection.is_connected()):
				cursor.close()
				connection.close()
				print("MySQL connection is closed")
		return render(request,'LoginPage.html',{'fail_creation':fail_creation})
	else:
		pass_not_matched='Both Passwords not matched'
		return render(request,'LoginPage.html',{'fail_creation':pass_not_matched})

def login_request(request):
	login_usr= request.POST.get('login_username')
	login_pass= request.POST.get('login_password')
	items=[]
	price=[]
	item_path=[]
	dict={}
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			login_chk_qry='select count(*),account_type,account_status from user_login where username="'+login_usr+'" and password="'+login_pass+'";'
			print(login_chk_qry)
			cursor.execute(login_chk_qry)
			record = cursor.fetchone()
			print(record)
			if(record[0]==1):
				if(record[2]=='Active'):
					if(record[1]=='User'):
						fetch_query="select item_name,price,item_path from items;"
						print(fetch_query)
						cursor.execute(fetch_query)
						records = cursor.fetchall()
						print(records)
						for i in range(0,len(records)):
							dict['product_no_'+str(i+1)]=records[i][0]
							dict['price_'+str(i+1)]=records[i][1]
							dict['item_path_'+str(i+1)]=records[i][2]
							items.append(records[i][0])
							price.append(records[i][1])
							item_path.append(records[i][2])
						count_imgs=len(items)
						item_paths=''
						for i in range(1,(len(dict)//3)+1):
							item_paths=item_paths+(dict['item_path_'+str(i)])+','
						item_paths=item_paths[:len(item_paths)-1]
						dict['item_paths']=item_paths
						if(count_imgs>1000):
							count_imgs=1000
						dict['total_no_products']=count_imgs
						dict['total_no_products']=22
						dict['user_name']=login_usr
						#print(dict)
						return render(request,'User_after_login.html',dict)
					elif(record[1]=='Admin'):
						dict={}
						login_chk_qry="select username,email_id from user_login where account_type='Admin' and account_status='Inactive';"
						cursor.execute(login_chk_qry)
						record=cursor.fetchall()
						print(record)
						for i in range(1,len(record)+1):
							dict['user_name_'+str(i)]=record[i-1][0]
							dict['Email_id_'+str(i)]=record[i-1][1]
						dict['total_no_users']=len(record)
						if(len(record)==0):
							dict['no_requests']='No requests Approval Pending'
						print(dict)
						return render(request,'Admin_after_login.html',dict)
					else:
						return render(request,'LoginPage.html')
				else:
					login_invalid='Account is inactive'
			else:
				login_invalid='Invalid Credentials'
	except Error as e:
		print("Error while connecting to MySQL : ", e)
	finally:
		if (connection.is_connected()):
			cursor.close()
			connection.close()
			print("MySQL connection is closed")
	return render(request,'LoginPage.html',{'login_invalid':login_invalid})

def retrieve_cred(request):
	return render(request,'Retrieve_credentials.html')

def logout_request(request):
	return render(request,'LoginPage.html',{'login_invalid':'Logged out Successfully'})

def saved_Address(request):
	usernm=request.POST.get('user_name1')
	print(usernm)
	dict={}
	dict['user_name']=usernm
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			login_chk_qry='select address_street,address_apt,address_city,address_state,address_pincode,mobile_number,id from user_address where username="'+usernm+'";'
			print(login_chk_qry)
			cursor.execute(login_chk_qry)
			record = cursor.fetchall()
			print(record)
			if(record is not None):
				for i in range(len(record)):
					dict['Apt_Street_'+str(i+1)]='Apt '+record[i][1]+', '+record[i][0]+','
					dict['city_state_zip_'+str(i+1)]=record[i][2]+', '+record[i][3]+', '+record[i][4]+'.'
					dict['mobile'+str(i+1)]=record[i][5]
					dict['id'+str(i+1)]=record[i][6]
				return render(request,'saved_Address.html',dict)
	except Error as e:
		print("Error while connecting to MySQL", e)
	return render(request,'saved_Address.html',{'user_name':usernm})

def add_Address(request):
	print('Add Address')
	usernm=request.POST.get('user_name1')
	street=request.POST.get('street')
	apt=request.POST.get('Apt')
	city=request.POST.get('city')
	state=request.POST.get('state')
	pincode=request.POST.get('pincode')
	mobile=request.POST.get('mobile')
	dict={}
	dict['user_name']=usernm
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			login_chk_qry='select count(*) from user_login where username="'+usernm+'";'
			print(login_chk_qry)
			cursor.execute(login_chk_qry)
			record = cursor.fetchone()
			print(record)
			if(record[0]==1):
				login_chk_qry='select count(*) from user_address where username="'+usernm+'";'
				print(login_chk_qry)
				cursor.execute(login_chk_qry)
				record = cursor.fetchone()
				print(record)
				id=record[0]+1
				if(len(record)<6):
					insert_qry="insert into user_address values("+str(id)+",'"+usernm+"','"+street+"','"+apt+"','"+city+"','"+state+"','"+pincode+"','"+mobile+"');"
					print(insert_qry)
					cursor.execute(insert_qry)
					login_chk_qry='select address_street,address_apt,address_city,address_state,address_pincode,mobile_number,id from user_address where username="'+usernm+'";'
					print(login_chk_qry)
					cursor.execute(login_chk_qry)
					record = cursor.fetchall()
					connection.commit()
					print(record)
					if(record is not None):
						for i in range(len(record)):
							dict['Apt_Street_'+str(i+1)]='Apt '+record[i][1]+', '+record[i][0]+','
							dict['city_state_zip_'+str(i+1)]=record[i][2]+', '+record[i][3]+', '+record[i][4]+'.'
							dict['mobile'+str(i+1)]=record[i][5]
							dict['id'+str(i+1)]=record[i][6]
							dict['Status_of_address']='Address saved successfully'
						return render(request,'saved_Address.html',dict)
					else:
						dict['Status_of_address']='Addresses are Full, Please delete any 1 address and add new Address'
						return render(request,'saved_Address.html',{'user_name':usernm,'Status_of_address':'Addresses are Full, Please delete any 1 address and add new Address'})
	except Error as e:
		print("Error while connecting to MySQL", e)
	return render(request,'saved_Address.html',{'user_name':usernm,'Status_of_address':'Address not saved successfully, Please try again'})

def rld_hmpg_after_login(request):
	usernm=request.POST.get('user_name1')
	print(usernm)
	return render(request,'User_after_login.html',{'user_name':usernm})

def approve_reject(request):
	data=request.POST.get('user_apr_rej')
	print(data)
	user_name=data[:data.find(' ')]
	stat=data[data.find(' ')+1:]
	dict={}
	status=''
	if(stat=='approve'):
		stat='Active'
		status='Approved'
	else:
		stat='Rejected'
		status='Rejected'
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			login_chk_qry="update user_login set account_status='"+stat+"' where username='"+user_name+"';"
			print(login_chk_qry)
			cursor.execute(login_chk_qry)
			login_chk_qry="select username,email_id from user_login where account_type='Admin' and account_status='Inactive';"
			cursor.execute(login_chk_qry)
			record=cursor.fetchall()
			print(len(record))
			connection.commit()
			if record is not None:
				dict['total_no_users']=len(record)
				for i in range(1,len(record)+1):
					dict['user_name_'+str(i)]=record[i-1][0]
					dict['Email_id_'+str(i)]=record[i-1][1]
					dict['done_stat']='User '+status+' Successfully'
					print(dict)
			if(len(record)==0):
				dict['no_requests']='No requests Approval Pending'
				#dict['total_no_users']=0
			return render(request,'Admin_after_login.html',dict)
	except Error as e:
		print("Error while connecting to MySQL", e)
	dict['done_stat']='User Approval Not Completed, Please try again'
	return render(request,'Admin_after_login.html',dict)

def upld_new(request):
	return render(request,'Admin_Upload_New.html')

def upload_file(request):
	print('request.FILES')
	dict={}
	dict['stat_new_item']='Item not Successfully added to database, Please try again'
	item_name=request.POST.get('item_name')
	department_name1=request.POST.get('category1')
	department_name2=request.POST.get('category2')
	department_name3=request.POST.get('category3')
	path='static/Women/Top Wear'
	item_brand=request.POST.get('item_brand')
	item_size=request.POST.get('item_size')
	item_price=request.POST.get('item_price')
	item_description=request.POST.get('item_des')
	item_tot=request.POST.get('item_tot')
	item_del=request.POST.get('item_del')
	
	dict2={}
	dict2['Men_top_wear']=['T Shirt','Casual Shirt','Men Sweaters','Suits','Jackets','Formal Shirt']
	dict2['Men_Indian_Festive_Wear']=['Men Kurtas','Sherwanis','Dhothis']
	dict2['Men_Bottom_Wear']=['Men Jeans','Track Pants','Boxers','Shorts']
	dict2['Men_Foot_Wear']=['Shoes','Flip Flops','Sandals','Men Socks']

	dict2['Women_Fusion_Wear']=['Sarees','Women Kurtas','Leggings & Churidars','Skirts','Lehenga','Dupattas']
	dict2['Women_Western_Wear']=['Women Dresses','Women Tops','Women Sweaters']
	dict2['Women_Beauty_Care']=['Makeup','Skin Care','Lipsticks','Fragrences']
	dict2['Women_Foot_Wear']=['Casual Shoes','Flats','Heels','Women Sports Shoes']

	dict2['Kids_Infants']=['Body Suites','Kids Dresses','Winter Wear','Inner Wear','Tshirts','Rompers']
	dict2['Kids_Boys_Clothing']=['Shirts','Ethnic Wear','Jeans','Kids Sweaters']
	dict2['Kids_girls_Clothing']=['Tops','TShirt','Dresses','Party wear']
	dict2['Kids_Foot_Wear']=['School Shoes','Sports Shoes','Socks']
	department_name=''
	name_no=0
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			login_chk_qry="select max(item_no) from items;"
			print(login_chk_qry)
			cursor.execute(login_chk_qry)
			record=cursor.fetchone()
			if record is not None:
				name_no=record[0]
			name_no=int(name_no)+1
			tab_dep_name=''
			if(department_name1 != 'select'):
				department_name=department_name1
			elif(department_name2 != 'select'):
				department_name=department_name2
			else:
				department_name=department_name3
			for i in dict2:
				if(department_name in dict2[i]):
					tab_dep_name=i
					break
			tab_dep_name=tab_dep_name[:tab_dep_name.find('_')]+'/'+tab_dep_name[tab_dep_name.find('_')+1:]
			path='/static/'+tab_dep_name+'/'+department_name+'/'+department_name+str(time.strftime("%Y%m%d-%H%M"))+str(name_no)+'.png'
			print(item_name+' '+item_brand+' '+item_size+' '+item_price+' '+item_description)
			print('Departments:')
			print(department_name1)
			print(department_name2)
			print(department_name3)
			print(path)
			if request.method == 'POST' and request.FILES['myfile']:
				print('if loop')
				myfile = request.FILES['myfile']
				fs = FileSystemStorage(path)
				filename = fs.save(myfile.name, myfile)
				#filename = fs.save('C:\Group7_iClothingAPP\static\Women', myfile)
				uploaded_file_url = fs.url(filename)
				dict['stat_new_item']='Item Successfully added to database.'
				insrt_qry="insert into items values ("+str(name_no)+",'"+item_name+"','"+tab_dep_name+"','"+path+"','"+item_brand+"','"+item_size+"','"+str(item_price)+"','"+item_description+"',"+item_tot+","+item_del+");"
				print(insrt_qry)
				cursor.execute(insrt_qry)
				connection.commit()
				return render(request,'Admin_Upload_New.html',dict)
	except Error as e:
		print("Error while connecting to MySQL", e)
	return render(request,'Admin_Upload_New.html',dict)

def open_cart(request):
	usernm=request.POST.get('user_name1')
	#no_of_items_cart=request.POST.get('cart_val')
	item_paths=request.POST.get('cart_click')
	print(usernm)
	#print(no_of_items_cart)
	item_name=''
	item_price=''
	dict={}
	dict['user_name']=usernm
	item_paths=item_paths.split(',')
	no_of_items_cart=len(item_paths)-1
	query=[]
	for i in range(0,len(item_paths)):
		item_paths[i]=item_paths[i][item_paths[i].find('static')-1:]
	print(item_paths)
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			login_chk_qry="select item_name,price,item_path,no_of_items_available,no_of_days_item_deliver,size from items;"
			print(login_chk_qry)
			cursor.execute(login_chk_qry)
			record=cursor.fetchall()
			#print(record)
			k=0
			if record[0] is not None:
				for i in range(0,no_of_items_cart):
					for j in range(0,len(record)):
						if(k<no_of_items_cart):
							if(item_paths[i]==record[j][2]):
								k=k+1
								print(record[j][2])
								qry="insert into shopping_cart values('"+usernm+"','"+record[j][0]+"','"+record[j][2]+"','"+record[j][1]+"',1,"+str(record[j][4])+",'L');"
								query.append(qry)
				
				print(query)
				print('no_of_tems_in_cart:'+str(no_of_items_cart))
				for i in range(0,len(query)):
					cursor.execute(query[i])
				query1="select item_name,item_path,item_price,quantity,no_of_days_item_deliver from shopping_cart where username='"+usernm+"';"
				print(query1)
				cursor.execute(query1)
				record=cursor.fetchall()
				print(record)
				shp_crt_len=len(record)
				dict['tot_cart_ord']=len(record)
				for i in range(1,len(record)+1):
					dict['item_name'+str(i)]=record[i-1][0]
					dict['price'+str(i)]=record[i-1][2]
					dict['q'+str(i)]=record[i-1][3]
					dict['img_cart_path'+str(i)]=record[i-1][1]
					dict['deliver'+str(i)]=str(record[i-1][4])+' Days to deliver'
					qnt_chk=record[i-1][2]
					if('$' in qnt_chk):
						a=''
						for m in qnt_chk:
							if('$'==m):
								pass
							else:
								a=a+str(m)
						qnt_chk=float(a)
					#print(qnt_chk)
					dict['q_price'+str(i)]=float(qnt_chk*record[i-1][3])
					#print(dict['q'+str(i)])
					#print(dict['price'+str(i)])
					#print(dict['q_price'+str(i)])
				query1="select address_apt,address_street,address_city,address_state,address_pincode,mobile_number from user_address where id = (select max(id) from user_address where username='"+usernm+"');"
				print(query1)
				cursor.execute(query1)
				record=cursor.fetchall()
				print(record)
				dict['user_def_address']=''
				if len(record)==0:
					dict['user_def_address']='Please add the delivery address from profile dropdown'
				else:
					for i in range(0,len(record)):
						dict['add_'+str(i+1)]=''
						for j in record[i]:
							dict['add_'+str(i+1)]=dict['add_'+str(i+1)]+j+','
						dict['add_'+str(i+1)]=dict['add_'+str(i+1)][:len(dict['add_'+str(i+1)])-1]
				connection.commit()
				img_cart_paths=''
				price_str=''
				item_name_str=''
				qnt_str=''
				del_str=''
				q_pr_str=''
				
				for i in range(0,shp_crt_len):
					img_cart_paths=img_cart_paths+dict['img_cart_path'+str(i+1)]+','
					price_str=price_str+str(dict['price'+str(i+1)])+','
					item_name_str=item_name_str+dict['item_name'+str(i+1)]+','
					qnt_str=qnt_str+str(dict['q'+str(i+1)])+','
					del_str=del_str+dict['deliver'+str(i+1)]+','
					q_pr_str=q_pr_str+str(dict['q_price'+str(i+1)])+','
				
				img_cart_paths=img_cart_paths[:len(img_cart_paths)-1]
				price_str=price_str[:len(price_str)-1]
				item_name_str=item_name_str[:len(item_name_str)-1]
				qnt_str=qnt_str[:len(qnt_str)-1]
				del_str=del_str[:len(del_str)-1]
				q_pr_str=q_pr_str[:len(q_pr_str)-1]
				
				dict['img_cart_paths']=img_cart_paths
				dict['price_str']=price_str
				dict['item_name_str']=item_name_str
				dict['qnt_str']=qnt_str
				dict['del_str']=del_str
				dict['q_pr_str']=q_pr_str
				tot_p=0.0
				for i in range(0,shp_crt_len):
					tot_p=tot_p+float(dict['q_price'+str(i+1)])
				
				tax=round(float(0.2*tot_p),2)
				dict['tax_tot']=tax
				dict['tot_p']=tot_p+tax
				print(dict)
				return render(request,'User_Shopping_Cart.html',dict)
	except Error as e:
		print("Error while connecting to MySQL", e)
	return render(request,'User_Shopping_Cart.html')

def update_addrs(request):
	usernm=request.POST.get('user_name1')
	add_inp=request.POST.get('Address_Any')
	print(add_inp)
	print(usernm)
	add_inp=add_inp.split(',')
	exec_qry=''
	dict={}
	for i in range(len(add_inp)):
		add_inp[i]=add_inp[i].strip()
	if(add_inp[0]=='Delete'):
		exec_qry='Delete from user_address where id = '+add_inp[1]+';'
	else:
		exec_qry="Update user_address set address_street = '"+add_inp[3]+"',address_apt='"+add_inp[2]+"',address_city='"+add_inp[4]+"',address_state='"+add_inp[5]+"',address_pincode='"
		exec_qry=exec_qry+add_inp[6][:add_inp[6].find('.')]+"',mobile_number='"+add_inp[6][add_inp[6].find('.')+1:]+"' where id = "+add_inp[1]+";"
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			print(exec_qry)
			cursor.execute(exec_qry)
			login_chk_qry='select address_street,address_apt,address_city,address_state,address_pincode,mobile_number,id from user_address where username="'+usernm+'";'
			print(login_chk_qry)
			cursor.execute(login_chk_qry)
			record = cursor.fetchall()
			print(record)
			if(record is not None):
				for i in range(len(record)):
					dict['Apt_Street_'+str(i+1)]=record[i][1]+', '+record[i][0]+','
					dict['city_state_zip_'+str(i+1)]=record[i][2]+', '+record[i][3]+', '+record[i][4]+'.'
					dict['mobile'+str(i+1)]=record[i][5]
					dict['id'+str(i+1)]=record[i][6]
			connection.commit()
			dict['Status_of_address']='Address Update or Delete Done'
			return render(request,'saved_Address.html',dict)
	except Error as e:
		print("Error while connecting to MySQL", e)
	return render(request,'saved_Address.html',{'user_name':usernm,'Status_of_address':'Address Update or Delete Not Complete Successfully'})
	
def save_cart_checkout(request):
	usernm=request.POST.get('user_name1')
	print(usernm)
	data=request.POST.get('all_data')
	print(data)
	dict={}
	dict['user_name']=usernm
	it_nm=''
	it_pth=''
	it_prce=''
	qnt=0
	it_del_days=0
	sze=''
	tot_no_valid_items=0
	a=data
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			delete_qry="delete from shopping_cart where username='"+usernm+"';"
			cursor.execute(delete_qry)
			for i in range(0,len(data.split('(')[1:])):
				it_nm=((a.split('(')[1:])[i].split(','))[0]
				it_pth=((a.split('(')[1:])[i].split(','))[2]
				it_pth=it_pth[it_pth.find('static')-1:]
				it_prce=((a.split('(')[1:])[i].split(','))[5]
				qnt=int(((a.split('(')[1:])[i].split(','))[3])
				temp=((a.split('(')[1:])[i].split(','))[4]
				it_del_days=int(temp[:temp.find(' ')])
				sze=((a.split('(')[1:])[i].split(','))[1]
				insrt_qry="insert into shopping_cart values('"+usernm+"','"+it_nm+"','"+it_pth+"','"+it_prce+"',"+str(qnt)+","+str(it_del_days)+",'"+sze+"');"
				print(insrt_qry)
				if(qnt==0):
					pass
				else:
					cursor.execute(insrt_qry)
					tot_no_valid_items=tot_no_valid_items+1
			query1="select item_name,item_path,item_price,quantity,no_of_days_item_deliver,size from shopping_cart where username='"+usernm+"';"
			print(query1)
			cursor.execute(query1)
			record=cursor.fetchall()
			print(record)
			shp_crt_len=len(record)
			dict['tot_cart_ord']=len(record)
			for i in range(1,len(record)+1):
				dict['item_name'+str(i)]=record[i-1][0]
				dict['price'+str(i)]=record[i-1][2]
				dict['q'+str(i)]=record[i-1][3]
				dict['img_cart_path'+str(i)]=record[i-1][1]
				dict['size_'+str(i)]=record[i-1][5]
				dict['deliver'+str(i)]=str(record[i-1][4])+' Days to deliver'
				qnt_chk=record[i-1][2]
				if('$' in qnt_chk):
					a=''
					for m in qnt_chk:
						if('$'==m):
							pass
						else:
							a=a+str(m)
					qnt_chk=float(a)
				#print(qnt_chk)
				dict['q_price'+str(i)]=float(qnt_chk*record[i-1][3])
				#print(dict['q'+str(i)])
				#print(dict['price'+str(i)])
				#print(dict['q_price'+str(i)])size_select
			query1="select address_apt,address_street,address_city,address_state,address_pincode,mobile_number from user_address where id = (select max(id) from user_address where username='"+usernm+"');"
			print(query1)
			cursor.execute(query1)
			record=cursor.fetchall()
			print(record)
			dict['user_def_address']=''
			if len(record)==0:
				dict['user_def_address']='Please add the delivery address from profile dropdown'
			else:
				for i in range(0,len(record)):
					dict['add_'+str(i+1)]=''
					for j in record[i]:
						dict['add_'+str(i+1)]=dict['add_'+str(i+1)]+j+','
					dict['add_'+str(i+1)]=dict['add_'+str(i+1)][:len(dict['add_'+str(i+1)])-1]
			connection.commit()
			img_cart_paths=''
			price_str=''
			item_name_str=''
			qnt_str=''
			del_str=''
			q_pr_str=''
			size_select=''
			
			for i in range(0,shp_crt_len):
				img_cart_paths=img_cart_paths+dict['img_cart_path'+str(i+1)]+','
				price_str=price_str+str(dict['price'+str(i+1)])+','
				item_name_str=item_name_str+dict['item_name'+str(i+1)]+','
				qnt_str=qnt_str+str(dict['q'+str(i+1)])+','
				del_str=del_str+dict['deliver'+str(i+1)]+','
				q_pr_str=q_pr_str+str(dict['q_price'+str(i+1)])+','
				size_select=size_select+dict['size_'+str(i+1)]+','
			
			img_cart_paths=img_cart_paths[:len(img_cart_paths)-1]
			price_str=price_str[:len(price_str)-1]
			item_name_str=item_name_str[:len(item_name_str)-1]
			qnt_str=qnt_str[:len(qnt_str)-1]
			del_str=del_str[:len(del_str)-1]
			q_pr_str=q_pr_str[:len(q_pr_str)-1]
			size_select=size_select[:len(size_select)-1]
			
			dict['img_cart_paths']=img_cart_paths
			dict['price_str']=price_str
			dict['item_name_str']=item_name_str
			dict['qnt_str']=qnt_str
			dict['del_str']=del_str
			dict['q_pr_str']=q_pr_str
			dict['size_select']=size_select
			
			tot_p=0.0
			for i in range(0,shp_crt_len):
				tot_p=tot_p+float(dict['q_price'+str(i+1)])
			
			tax=round(float(0.2*tot_p),2)
			dict['tax_tot']=tax
			dict['tot_p']=tot_p+tax
			print(dict)
			return render(request,'User_Shopping_Cart_Save.html',dict)
	except Error as e:
		print("Error while connecting to MySQL", e)
	return render(request,'User_Shopping_Cart_Save.html',{'user_name':usernm})

def pay_page(request):
	usernm=request.POST.get('user_name1')
	return render(request,'payment_form.html',{'user_name':usernm})

def del_ord_email(request):
	usernm=request.POST.get('user_name1')
	text='gopisairam999@gmail.com'
	MY_ADDRESS=str(text)
	#print(MY_ADDRESS)    
	text='pqhylspdtjskergd'
	PASSWORD=str(text)
	#print(PASSWORD)
	item_nm=''
	item_qnt=''
	itm_price=''
	complete_str=''
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			fetch_qry="select item_name,item_path,item_price,quantity,no_of_days_item_deliver,size from shopping_cart where username='"+usernm+"';"
			cursor.execute(fetch_qry)
			record=cursor.fetchall()
			print(record)
			for i in range(0,len(record)):
				item_nm=record[i][0]
				item_qnt=record[i][3]
				itm_price=record[i][2]
				complete_str=complete_str+item_nm+' '+str(item_qnt)+' '+itm_price+'\n'
			print(complete_str)
	except Error as e:
		print("Error while connecting to MySQL", e)
		#print('before email')
	
	try:
		context=ssl.create_default_context()
		# set up the SMTP server
		s = smtplib.SMTP(host='smtp.gmail.com', port=587)
		s.ehlo()
		s.starttls(context=context)
		s.ehlo()
		s.login(MY_ADDRESS, PASSWORD)

		#Gmail SMTP server address: smtp.gmail.com
		#Gmail SMTP port (TLS): 587.
		#Gmail SMTP port (SSL): 465.

		msg = MIMEMultipart()       # create a message

		# setup the parameters of the message
		msg['From']=MY_ADDRESS
		msg['To']=MY_ADDRESS
		print("To Address:",msg['To'])
		text="Invoice of your Order"
		msg['Subject']=str(text)
		print(msg['Subject'])

		msge=complete_str
		msge=msge+"\n\nThanks,\niClothing Team"
		message=str(msge)
		# add in the message body
		msg.attach(MIMEText(message, 'plain'))
		print('sending mail')        
		# send the message via the server set up earlier.
		s.send_message(msg)
		del msg

		# Terminate the SMTP session and close the connection
		s.quit()
	except Error as e:
		print("Error while connecting to MySQL", e)
		print("Some error occured and could not send mail. Sorry!")
	
	return render(request,'order_confirm.html',{'user_name':usernm})

def prod_catalog(request):
	usernm=request.POST.get('user_name1')
	dict={}
	dict['user_name']=usernm
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			fetch_qry="select item_name,department_name,brand,size,price,description,no_of_items_available,no_of_days_item_deliver,item_no,item_path from items;"
			cursor.execute(fetch_qry)
			record=cursor.fetchall()
			#print(record)
			dict['total_no_items']=len(record)
			for i in range(0,dict['total_no_items']):
				dict['itnm'+str(i+1)]=record[i][0]
				dict['dpt'+str(i+1)]=record[i][1]
				dict['brnd'+str(i+1)]=record[i][2]
				dict['size'+str(i+1)]=record[i][3]
				dict['price'+str(i+1)]=record[i][4]
				dict['des'+str(i+1)]=record[i][5]
				dict['itmsavl'+str(i+1)]=record[i][6]
				dict['itmsdel'+str(i+1)]=record[i][7]
				dict['itno'+str(i+1)]=record[i][8]
			
			item_no_str=''
			item_name_str=''
			dept_str=''
			brnd_str=''
			size_str=''
			price_str=''
			desc_str=''
			avail_str=''
			no_days_deliver_str=''
			for i in range(0,len(record)):
				item_no_str=item_no_str+str(dict['itno'+str(i+1)])+','
				item_name_str=item_name_str+dict['itnm'+str(i+1)]+','
				#print(dict['itnm'+str(i+1)])
				dept_str=dept_str+dict['dpt'+str(i+1)]+','
				brnd_str=brnd_str+dict['brnd'+str(i+1)]+','
				size_str=size_str+dict['size'+str(i+1)]+','
				price_str=price_str+dict['price'+str(i+1)]+','
				desc_str=desc_str+dict['des'+str(i+1)]+','
				avail_str=avail_str+str(dict['itmsavl'+str(i+1)])+','
				no_days_deliver_str=no_days_deliver_str+str(dict['itmsdel'+str(i+1)])+','
			
			
			item_no_str=item_no_str[:len(item_no_str)-1]
			item_name_str=item_name_str[:len(item_name_str)-1]
			dept_str=dept_str[:len(dept_str)-1]
			brnd_str=brnd_str[:len(brnd_str)-1]
			size_str=size_str[:len(size_str)-1]
			price_str=price_str[:len(price_str)-1]
			desc_str=desc_str[:len(desc_str)-1]
			avail_str=avail_str[:len(avail_str)-1]
			no_days_deliver_str=no_days_deliver_str[:len(no_days_deliver_str)-1]

			dict['item_no_str']=item_no_str
			dict['item_name_str']=item_name_str
			dict['dept_str']=dept_str
			dict['brnd_str']=brnd_str
			dict['size_str']=size_str
			dict['price_str']=price_str
			dict['desc_str']=desc_str
			dict['avail_str']=avail_str
			dict['no_days_deliver_str']=no_days_deliver_str
			#print(dict)
			return render(request,'Admin_product_catalog.html',dict)
	except Error as e:
		print("Error while connecting to MySQL", e)
	return render(request,'Admin_product_catalog.html',dict)

def prod_cat(request):
	data=request.POST.get('all_data_ed_del')
	print(data)
	temp_data=data.split('(')[1:]
	list_tuples=[]
	status='Product Catalog Successfully Updated'
	for i in temp_data:
		list_tuples.append(i.split(',')[:-1])
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			if('Delete' in data.split(',')[0]):
				for i in list_tuples:
					del_qry='Delete from items where item_no='+str(int(i[0]))+';'
					cursor.execute(del_qry)
			else:
				for i in list_tuples:
					upd_qry="Update items set item_name='"+i[1]+"', department_name='"+i[2]+"', brand='"+i[3]+"',  size='"+i[4]+"', price='"+i[5]+"', description='"+i[6]+"', no_of_items_available='"+str(i[7])+"', no_of_days_item_deliver='"+str(i[8])+"' where item_no="+str(int(i[0]))+";"
					cursor.execute(upd_qry)
		connection.commit()
	except Error as e:
		status='Product Catalog Update is not Successful, Please try again.'
		print("Error while connecting to MySQL", e)
	return render(request,'Admin_product_catalog_status.html',{'status':status})













	

















def homepage(request):
    return render(request = request,
                  template_name='main/home.html')

def news(request):
	print('All news headlines')
	userloc=request.POST.get('userlocation1')
	print(userloc)
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			print("You're connected to database: ", record)
			query="select count(*) from news where location='"+userloc+"';"
			cursor.execute(query)
			Tot = cursor.fetchone()
			query="select news_headline from news where location='"+userloc+"';"
			cursor.execute(query)
			records = cursor.fetchall()
	except Error as e:
		print("Error while connecting to MySQL", e)
	finally:
		if (connection.is_connected()):
			cursor.close()
			connection.close()
			print("MySQL connection is closed")
	print(Tot)
	Total=Tot[0]
	News_Headline={'max_headlines':Total}
	for i in range(0,Total):
		st='headline_'+str(i+1)
		News_Headline[st]=records[i][0]
	return render(request,'news.html',News_Headline)

def external(request):
	inp= request.POST.get('param')
	if(str(inp)=='' or str(inp).lower()=='inactive mode'):
		return render(request,'new_header_inactive.html')
	if('weather' in str(inp)):
		temp_atmos,daily_status,week_status,User_location=weather_today(inp)
		print(result1)
		return render(request,'weather_web.html',{'Temp_Atmosphere':temp_atmos,"Daily_status":daily_status,"Weekly_status":week_status,'User_location':User_location})
	elif('youtube' in str(inp).lower() or 'search' in str(inp).lower() or 'for' in str(inp).lower()):
		if('for' in str(inp).lower()):
			text=str(inp)[str(inp).lower().index('for')+4:]
		elif('youtube' in str(inp).lower() or 'search' in str(inp).lower() or 'per' in str(inp).lower()):
			text=str(inp)[str(inp).lower().index('per')+4:]
		else:
			text=str(inp)
		videos_link=[]
		text=text.replace(' ', '+')
		html = urllib.request.urlopen("https://www.youtube.com/results?search_query="+text)
		video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
		if(len(video_ids)>5):
			for i in range(0,5):
				videos_link.append(video_ids[i])
		else:
			videos_link=video_ids
		News_dict_val={'max_news_videos':len(videos_link)}
		for i in range(0,len(videos_link)):
			st='Yt_'+str(i+1)
			if(i==0):
				News_dict_val[st]='https://www.youtube.com/embed/'+videos_link[i]+'?autoplay=1'
			else:
				News_dict_val[st]='https://www.youtube.com/embed/'+videos_link[i]
		return render(request,"Jarvis_Youtube.html",News_dict_val)
	elif('send' in str(inp) and 'email' in str(inp) and ('message' not in str(inp) or ('to' not in str(inp) and 'message' in str(inp)))):
		to_address=''
		Message=''
		Any_Attachments=''
		Attachment_Names=''
		print(str(inp))
		if('to' in str(inp) and '.com' in str(inp)):
			to_address=str(inp)[str(inp).find('to')+3:str(inp).find('.com')+4]
			if('at the rate of' in str(inp).lower()):
				to_address=to_address.replace('at the rate of','@')
			elif('at the rate' in str(inp).lower()):
				to_address=to_address.replace('at the rate','@')
			to_address=to_address.replace(' ','')
			print(to_address)
		if('message' in str(inp).lower()):
			Message=str(inp)[str(inp).find('essage')+7:]
			print(Message)
		return render(request,"Jarvis_email.html",{'to_address':to_address,'Message':Message,'Any_Attachments':Any_Attachments,'Attachment_Names':Attachment_Names})
	elif(('add' in str(inp) or 'update' in str(inp)) and ('schedule' in str(inp) or 'occasion' in str(inp)) and 'flaga' not in str(inp) and 
	('on' not in str(inp) or 'occasion' in str(inp))):
		return render(request,"Jarvis_sch_occ.html")
	elif('send' in str(inp) and 'whatsapp' in str(inp).lower() and 'time:' not in str(inp)):
		return render(request,"Jarvis_Whatsapp.html")
	elif('sendwhatsapp' in str(inp).lower() and 'message:' in str(inp) and 'time:' in str(inp)):
		print(str(inp))
		number=str(inp)[str(inp).find(' ')+1:str(inp).find(' message:')]
		message=str(inp)[str(inp).find(':')+2:str(inp).find(' time: ')]
		time=str(inp).split('time: ')[1]
		hours=time[:time.find(',')]
		mins=time[time.find(',')+1:]
		print('number: "'+number+'"')
		print('time: '+hours+':'+mins)
		whatsapp.sendwhatmsg(number,message,int(hours),int(mins))
		return render(request,'Jarvis_Whatsapp.html',{'Status':'Message sent Successfully'})

	out= run([sys.executable,'C:\\Users\\gopis\\Project1\\jarvis_test.py',inp],shell=False,stdout=PIPE)
	print(out)
	new_var = out.stdout.decode('latin1')
	index=0
	print(inp)
	'''inp1='tell me a joke'
	out1= run([sys.executable,'C:\\Users\\gopis\\Project1\\jarvis_test.py',inp1],shell=False,stdout=PIPE)
	#print(type(out1.stdout))
	print(out1)
	joke_var=out1.stdout.decode('latin1')
	joke='\n' + joke_var[0:]
	print("joke = " + joke)'''	
	joke='No Jokes'
	if('send' in str(inp) and 'message' in str(inp) and ('mail' not in str(inp).lower() or 'whatsapp' not in str(inp))):
		f=open('display_message.txt','r')
		for each_line in f.readlines():
			msg1=each_line			
		f.close()
		return render(request,'Jarvis_message.html',{'msg1':msg1})
	elif('shutdown' in str(inp).lower()):
		os.system("TASKKILL /F /IM python.exe")
	elif(('connect' in str(inp) or 'open' in str(inp)) and 'database' in str(inp)):
		return render(request,'Jarvis Database.html')
	elif('add' in str(inp) and ('schedule' in str(inp) or 'occasion' in str(inp))):
		if('Modified occasion or schedule table' in new_var):
			Status='Updated occasion or schedule table'
		else:
			Status='Updating the occasion or schedule Table Failed'
		return render(request,"Jarvis_sch_occ.html",{'Status':Status})
	elif (('play' in str(inp) or 'next' in str(inp)) and 'video' in str(inp)):
		#print("1")
		for i in range(3,len(new_var)):
			if((i)=='4' and (i-1)=='p' and (i-2)=='m' and (i-3)=='.'):
				break
			else:
				index=index+1
		print("Index: {}".format(index))
		print("\n The video song is : " + new_var[23:(index+1)] +"Hi gopi")
		return render(request,'play_video.html',{'outp1':new_var[23:(index+1)],"joke1":joke})
	elif('home' in (str(inp)).lower()):
		inp2="my schedule for today"
		out2= run([sys.executable,'C:\\Users\\gopis\\Project1\\jarvis_test.py',inp2],shell=False,stdout=PIPE)
		#print(out2)
		sch_var=out2.stdout.decode('latin1')
		schedule='\n'+sch_var[22:]
		print("schedule = " + schedule)
		return render(request,'new_header1.html',{"sched1":schedule})
	elif('record' in str(inp) and 'audio' in str(inp)):
		return render(request,'user_media_audio.html')
	elif(('record' in str(inp) or 'take' in str(inp)) and 'video' in str(inp)):
		return render(request,'user_media_video.html')
	elif('photo' in str(inp) or 'picture' in str(inp) or 'selfie' in str(inp)):
		return render(request,'user_media_photo.html')
	elif (('play' in str(inp) or 'next' in str(inp)) and 'song' in str(inp)):
		for i in range(3,len(new_var)):
			if((i)=='3' and (i-1)=='p' and (i-2)=='m' and (i-3)=='.'):
				break
			else:
				index=index+1
		print("Index: {}".format(index))
		print("\n The song is : " + new_var[22:(index+1)] +"Hi gopi")
		print("The command is : " + inp)
		#print("2")
		return render(request,'play_song.html',{'outp1':new_var[22:(index+1)],"joke1":joke})
	elif ('play' in str(inp)):
		for i in range(3,len(new_var)):
			if((i)=='d' and (i-1)=='e' and (i-2)=='b' and (i-3)=='m'):
				break
			else:
				index=index+1
		print("\n The youtube video is : " + new_var[116:(index+1)] +"Hi gopi")
		return render(request,'play_youtube_video.html',{'outp1':new_var[116:(index+1)],"joke1":joke})
	elif('news' in str(inp) or 'headlines' in str(inp) or 'head lines' in str(inp)):
		print('news view')
		#f=open('C:\\Users\\gopis\\Desktop\\jarvis\\news.txt','r')
		#content=f.read()
		#f.close()
		try:
			connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')                                         
			if connection.is_connected():
				db_Info = connection.get_server_info()
				print("Connected to MySQL Server version ", db_Info)
				cursor = connection.cursor()
				cursor.execute("select database();")
				record = cursor.fetchone()
				print("You're connected to database: ", record)
				query='select max(id) from news;'
				cursor.execute(query)
				Tot = cursor.fetchall()
				query='select * from news order by news_time desc;'
				cursor.execute(query)
				records = cursor.fetchall()			
		except Error as e:
			print("Error while connecting to MySQL", e)
		finally:
			if (connection.is_connected()):
				cursor.close()
				connection.close()
				print("MySQL connection is closed")
		Total=Tot[0][0]+1
		Time_dict={}
		News_from_dict={}
		News_Headline={'max_headlines':Total}
		for i in range(0,Total):
			st='headline_'+str(i+1)
			Time_dict[i]=str(records[i][2])
			News_from_dict[i]=records[i][1]
			News_Headline[st]=records[i][3]
		
		return render(request,'news.html',News_Headline)
		#return render(request,'news_headlines.html',{'file_content':content})
	elif('meaning' in str(inp)):
		print('meaming of word')
		return render(request,'news_headlines.html',{'file_content':new_var[:]})
	elif("who are you" in str(inp) or "what is your name" in str(inp) or "your name" in str(inp) or "may I know your name" in str(inp) or 
	'rename' in str(inp) or 'change your name' in str(inp) or 'time' in str(inp) or 'date' in str(inp) or 'day' in str(inp)):
		return render(request,'Response_page_jarvis.html',{"joke1":joke})
	elif('download' in str(inp) and 'file' in str(inp)):
		return render(request,'download proj files.html')
	elif('upload' in str(inp) and 'file' in str(inp)):
		student = StudentForm(request.POST, request.FILES)
		return render(request,"Upload_files.html",{'form':student})
	elif('translate' in str(inp).lower() and 'image' in str(inp).lower()):
		trans_img=new_var[43:]
		return render(request,"Translate_Image.html",{'Img_Dtls':trans_img})	
	elif('calculator' in str(inp).lower() or 'calculations' in str(inp).lower()):
		return render(request,'Calculator.html')
	elif('send' in str(inp) and 'mail' in str(inp)):
		if('Email sent successfully' in new_var):
			Status='Email sent successfully'
		else:
			Status='Email send failed, Please try again'
		return render(request,"Jarvis_email.html",{'Status':Status})
	return render(request,'new_header1.html')
    
def upload1(request):
	if request.method == 'POST':
		print('post method')
		print(request.FILES['file'])
		student = StudentForm(request.POST, request.FILES)
		if student.is_valid():
			handle_uploaded_file(request.FILES['file'])  
			return render(request,"Upload_files.html",{'form':student})
			#return HttpResponse("File uploaded successfuly")  
	else:  
		print('else method')
		student = StudentForm()
	return render(request,"Upload_files.html",{'form':student})
		
	'''
	myfile = request.FILES['myfile']
		fs = FileSystemStorage()
		filename = fs.save(myfile.name, myfile)
	'''

def download(request):
	if request.method == 'POST':
		print('POST')
		inp= request.POST.get('sel_file')
		#fl_path = r'C:\\Users\\gopis\\Desktop\\jarvis/my_name_file.txt'
		fl_path = inp
		#print(fl_path)
		if('not found' in fl_path):
			pass
		else:
			print(fl_path)
			fl = open(fl_path, 'r')
			mime_type, _ = mimetypes.guess_type(fl_path)
			response = HttpResponse(fl, content_type=mime_type)
			response['Content-Disposition'] = "attachment; filename=%s" % fl_path
			return response
	else:
		inp= request.POST.get('sel_file')
		print(inp)
		print('Else in downloading file')
	return render(request,"download proj files.html")
	
#https://docs.djangoproject.com/en/3.0/topics/http/file-uploads/
#https://www.javatpoint.com/django-file-upload	

def database(request):
	if request.method == 'POST':
		inp= request.POST.get('param')
		if('home' in str(inp)):
			return render(request,'new_header1.html')
		elif('fetch' in str(inp)):
			tb_name=inp.split()[1]
			try:
				query="select * from " + tb_name + ";"
				connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')                                         
				if connection.is_connected():
					db_Info = connection.get_server_info()
					print("Connected to MySQL Server version ", db_Info)
					cursor = connection.cursor()
					cursor.execute("select database();")
					record = cursor.fetchone()
					print("You're connected to database: ", record)
					cursor.execute(query)
					record = cursor.fetchall()
					columns = cursor.description
			except Error as e:
				print("Error while connecting to MySQL", e)
			finally:
				if (connection.is_connected()):
					cursor.close()
					connection.close()
					print("MySQL connection is closed")
			
			result="Table Name: '" + tb_name + "'" +'\n'+'Column Names:'
			
			headers=[]
			#print(tabulate([['Alice', 24], ['Bob', 19]], headers=['Name', 'Age'], tablefmt='orgtbl'))
			for i in range(0,len(columns)):
				result=result+'  '+str(columns[i][0])
				headers.append(columns[i][0])
			
			list1=[]
			for i in range(0,len(record)):
				for j in range(0,len(record[i])):
					list1.append(str(record[i][j]))
				list1.append(',,,')	
			
			list2=[]
			list3=[]
			for i in range(0,len(list1)):
				if(list1[i]==',,,'):
					list2.append(list3)
					list3=[]
				else:
					list3.append(list1[i])
			
			result1=tabulate(list2, headers, tablefmt='orgtbl')
			return render(request,"Jarvis Database.html",{'output1':result1})
		elif('run query' in str(inp)):
			try:
				query=str(inp[10:])
				connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')                                         
				if connection.is_connected():
					db_Info = connection.get_server_info()
					print("Connected to MySQL Server version ", db_Info)
					cursor = connection.cursor()
					cursor.execute("select database();")
					record = cursor.fetchone()
					print("You're connected to database: ", record)
					cursor.execute(query)
					print(query)
					try:
						record = cursor.fetchall()
					except:
						record=[('success',)]
					try:
						connection.commit()
						print('commited')
					except:
						print('select query')
			except Error as e:
				print("Error while connecting to MySQL", e)
			finally:
				if (connection.is_connected()):
					cursor.close()
					connection.close()
					print("MySQL connection is closed")
			
			result=""
			for i in range(0,len(record)):
				for j in range(0,len(record[i])):
					result=result+' '+str(record[i][j])
				result=result+'\n'
			return render(request,"Jarvis Database.html",{'output1':result})	
	return render(request,"Jarvis Database.html")
			
def handle_uploaded_file(f):
	file_name='C:/Users/gopis/Desktop/Jarvis/Uploaded files/' + str(f)
	print('handle upload',file_name)
	with open(file_name, 'wb+') as destination:  
		for chunk in f.chunks():  
			destination.write(chunk)

def weather_today(text):
	#pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
	if('lat and long weather' in text):
		numbers = re.findall('[0-9]+', text)
		result=rg.search(coordinates)
		results_df=pd.DataFrame(result)
		User_location=results_df.loc[0][2].split(',')[0] + ',' + results_df.loc[0][3].split(',')[0]
	else:
		place=text.split('weather in ')[1]
		query='latitude and longitude of ' + place
		query=query.replace(' ','+')
		URL=f'https://www.google.com/search?q={query}'
		resp = requests.get(URL)
		soup = BeautifulSoup(resp.content, "html.parser")
		print(URL)	 
		h=''
		for g in soup.find_all('div',class_='BNeawe iBp4i AP7Wnd'):
			h=g.get_text()
			print("h=" +h)
			break
		numbers=[]
		if(h==''):
			numbers.append('15')
			numbers.append('9129')
			numbers.append('79')
			numbers.append('7400')
		else:
			numbers = re.findall('[0-9]+', h)
		result=rg.search(coordinates)
		results_df=pd.DataFrame(result)
		User_location=results_df.loc[0][2].split(',')[0] + ',' + results_df.loc[0][3].split(',')[0]
	print(numbers)
	text='lat and long weather in Latitude:'+(numbers[0]+'.'+numbers[1])+ 'Longitude:'+(numbers[2]+'.'+numbers[3])
	coordinates=(float(numbers[0]+'.'+numbers[1]),float(numbers[2]+'.'+numbers[3]))
	URL=f"https://darksky.net/forecast/" + (numbers[0]+'.'+numbers[1]) + ',' + (numbers[2]+'.'+numbers[3]) +'/'
	resp = requests.get(URL)
	soup = BeautifulSoup(resp.content, "html.parser")
	for g in soup.find_all('span',class_='summary swap'):
		temp_atmos=g.get_text()
	for g in soup.find_all('span',class_='currently__summary next swap'):
		daily_status=g.get_text().split('\n')[2].strip()
	for g in soup.find_all('div',class_='summary'):
		week_status=g.get_text()
	print('Temperature and Atmosphere :' + temp_atmos + 'daily status :' + daily_status + 'week status :'+week_status)
	'''
	query = 'Hourly weather forecast in ' + results_df.loc[0][2].split(',')[0] + ' ' + results_df.loc[0][3].split(',')[0] + ' weather.com'
	query=query.replace(' ','+')
	URL = f"https://google.com/search?q={query}"
	print(URL)
	resp = requests.get(URL)
	soup = BeautifulSoup(resp.content, "html.parser")
	list=''
	for g in soup.find_all('a'):
		if('q=https://weather.com/' in str(g) and 'hourbyhour' in str(g)):
			list=str(g).split('q=')[1].split('&')[0]
			list=list.replace('%3F','?')
			list=list.replace('%3D','=')
			print(list)
			break
	URL=list
	print(URL)
	resp = requests.get(URL)
	soup = BeautifulSoup(resp.content, "html.parser")
	time=[]
	for g in soup.find_all('h2',class_='_-_-components-src-molecule-DaypartDetails-DetailsSummary-DetailsSummary--daypartName--kbngc'):
		time.append(g.get_text())
	temp=[]
	for g in soup.find_all('span',class_='_-_-components-src-molecule-DaypartDetails-DetailsSummary-DetailsSummary--tempValue--jEiXE'):
		temp.append(g.get_text())
	status=[]
	for g in soup.find_all('span',class_='_-_-components-src-molecule-DaypartDetails-DetailsSummary-DetailsSummary--extendedData--307Ax'):
		status.append(g.get_text())
	wind=[]
	for g in soup.find_all('span',class_='_-_-components-src-atom-WeatherData-Wind-Wind--windWrapper--3Ly7c undefined'):
		wind.append(g.get_text())
	humidity=[]
	for g in soup.find_all('span',class_='_-_-components-src-molecule-DaypartDetails-DetailsTable-DetailsTable--value--2YD0-'):
		if('PercentageValue' in str(g)):
			humidity.append(g.get_text())
	uvindex=[]
	for g in soup.find_all('span',class_='_-_-components-src-molecule-DaypartDetails-DetailsTable-DetailsTable--value--2YD0-'):
		if('UVIndexValue' in str(g)):
			uvindex.append(g.get_text())
	rain=[]
	for g in soup.find_all('div',class_='_-_-components-src-molecule-DaypartDetails-DetailsSummary-DetailsSummary--precip--1a98O'):
		rain.append(g.get_text())
	Hourly_stat=[]
	for i in range(0,len(time)-1):
		list=[]
		list.append(time[i])
		list.append(temp[i])
		list.append(status[i])
		list.append(wind[i])
		list.append(humidity[i])
		list.append(uvindex[i])
		list.append(rain[i])
		#Hourly_stat=Hourly_stat+time[i]+' '+temp[i]+' '+status[i]+' '+wind[i]+' '+humidity[i]+' '+uvindex[i]+' '+rain[i]+'\n'
		Hourly_stat.append(list)
	#print(Hourly_stat)
	headers=['Time','Temperature','Status','Wind Speed','Humidity','UVIndex','Rain Chance']
	result1=tabulate(Hourly_stat, headers, tablefmt='orgtbl')
	#result1=result1.replace('\n',' ')
	result1=result1+'\n\n\n\n\n\n\n\n\n\nDone'
	#print(result1)
	mypath = "C:/Users\gopis\Desktop\Jarvis\Weather"
	for root, dirs, files in os.walk(mypath):
		for file in files:
			os.remove(os.path.join(root, file))
	URL='https://mausam.imd.gov.in/imd_latest/contents/all_india_forcast_bulletin.php'
	resp = requests.get(URL)
	soup = BeautifulSoup(resp.content, "html.parser")
	prediction=''
	for g in soup.find_all('img'):
		if('pdf_to_img' in str(g)):
			past_weather=str(g)
			break
	count=0
	for g in soup.find_all('img'):
		if('pdf_to_img_aiwfb' in str(g)):
			prediction=str(g)
			count=count+1
		if(count==3):
			break
	state=results_df.admin1[0]
	print('prediction url:',prediction)
	prediction='https://mausam.imd.gov.in/'+prediction[prediction.index('backend'):prediction.index('" ')]
	prediction=prediction.replace(' ','%20')
	urllib.request.urlretrieve(prediction, 'C://Users\gopis\Desktop\Jarvis\Weather/prediction.jpg')
	text = pytesseract.image_to_string(Image.open('C://Users\gopis\Desktop\Jarvis\Weather/prediction.jpg'))
	list1=text.split('Weather Warning during next 5 days')
	list2=list1[1].split('\n\n')
	#print(list2)
	Pred_state=''
	pred5day=''
	for i in range(2,len(list2)):
		if('Red color warning does' in list2[i]):
			break
		else:
			pred5day=pred5day+list2[i]+'\n'
	pred5day=pred5day+'\n\n\n\n\n\nDone'
	for i in range(2,len(list2)):
		if('Red color warning does' in list2[i]):
			break
		elif(state.lower() in list2[i].lower()):
			status=list2[i].split('likely')[0].strip().rstrip('very').strip().lstrip('¢').lstrip('@ ').split('at isolated places')[0]
			if('Day' in list2[i]):
				#print('modify:',list2[i])
				date1=list2[i].split(':')[0].split(' (')[0]
			elif('Day' in list2[i-1]):
				date1=list2[i-1].split(':')[0].split(' (')[0]
			elif('Day' in list2[i-2]):
				date1=list2[i-2].split(':')[0].split(' (')[0]
			print(status + ' on ' + date1)
			Pred_state=Pred_state+status + ' on ' + date1+'\n'
	if(Pred_state==''):
		Pred_state='No Bad Weather'
	print(Pred_state)
	'''
	return temp_atmos,daily_status,week_status,User_location
	#return render(request,'weather_web.html',{'Temp_Atmosphere':temp_atmos,"Daily_status":daily_status,"Weekly_status":week_status,'Hourly_weather':result1,'5DayPred':pred5day,'state_pred':Pred_state})

def News(request):
	if request.method == 'POST':
		inp= request.POST.get('param')
		print(str(inp))
		if('home' in str(inp).lower() and 'news' not in str(inp)):
			return render(request,'new_header1.html')
		elif('youtube' in str(inp).lower() or 'search' in str(inp).lower() or 'for' in str(inp).lower()):
			if('for' in str(inp).lower()):
				text=str(inp)[str(inp).lower().index('for')+4:]
			else:
				text=str(inp)
			videos_link=[]
			text=text.replace(' ', '+')
			html = urllib.request.urlopen("https://www.youtube.com/results?search_query="+text)
			video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
			if(len(video_ids)>5):
				for i in range(0,5):
					videos_link.append(video_ids[i])
			else:
				videos_link=video_ids
			News_dict_val={'max_news_videos':len(videos_link)}
			for i in range(0,len(videos_link)):
				st='Yt_'+str(i+1)
				if(i==0):
					News_dict_val[st]='https://www.youtube.com/embed/'+videos_link[i]+'?autoplay=1'
				else:
					News_dict_val[st]='https://www.youtube.com/embed/'+videos_link[i]
			return render(request,"Jarvis_Youtube.html",News_dict_val)
		elif('news' in str(inp).lower() and 'home' in str(inp).lower()):
			try:
				connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')                                         
				if connection.is_connected():
					db_Info = connection.get_server_info()
					print("Connected to MySQL Server version ", db_Info)
					cursor = connection.cursor()
					cursor.execute("select database();")
					record = cursor.fetchone()
					print("You're connected to database: ", record)
					query='select max(id) from news;'
					cursor.execute(query)
					Tot = cursor.fetchall()
					query='select * from news order by news_time desc;'
					cursor.execute(query)
					records = cursor.fetchall()			
			except Error as e:
				print("Error while connecting to MySQL", e)
			finally:
				if (connection.is_connected()):
					cursor.close()
					connection.close()
					print("MySQL connection is closed")
			Total=Tot[0][0]+1
			Time_dict={}
			News_from_dict={}
			News_Headline={'max_headlines':Total}
			for i in range(0,Total):
				st='headline_'+str(i+1)
				Time_dict[i]=str(records[i][2])
				News_from_dict[i]=records[i][1]
				News_Headline[st]=records[i][3]
			return render(request,'news.html',News_Headline)
		elif('open' in str(inp).lower() or 'expand' in str(inp).lower() and 'news' in str(inp).lower()):
			text=str(inp)
			print(text)
			if('one' in text):
				text='open news 1'
			news_no=int(text.strip('open ').strip('Open ').strip('news ').strip('News '))-1
			try:
				connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')                                         
				if connection.is_connected():
					db_Info = connection.get_server_info()
					print("Connected to MySQL Server version ", db_Info)
					cursor = connection.cursor()
					cursor.execute("select database();")
					record = cursor.fetchone()
					print("You're connected to database: ", record)
					query='select * from news order by news_time desc;'
					cursor.execute(query)
					records = cursor.fetchall()			
			except Error as e:
				print("Error while connecting to MySQL", e)
			finally:
				if (connection.is_connected()):
					cursor.close()
					connection.close()
					print("MySQL connection is closed")
			query=records[news_no][3]
			query = query.replace(' ', '+')
			URL = f"https://google.com/search?q={query}"
			resp = requests.get(URL)
			soup = BeautifulSoup(resp.content, "html.parser")
			news_desc=''
			for g in soup.find_all('div',class_='BNeawe s3v9rd AP7Wnd'):
				news_desc=(g.get_text())
				break
			list1=[]
			first_link_of_news=''
			for g in soup.find_all():
				if('https://' in str(g)):
					try:
						list1.append(str(g)[str(g).index('https://'):str(g).index('&amp')])
					except:
						pass
			for i in list1:
				if('https://maps' not in i and len(i)>0):
					first_link_of_news=(i)
					break
			try:
				URL=i
				resp = requests.get(URL)
				soup = BeautifulSoup(resp.content, "html.parser")
				for g in soup.find_all('img'):
					if('title' in str(g) and 'https://' in str(g)):
						temp=(str(g)[str(g).index('https://'):])
						temp=temp[0:temp.index(' ')-1]
						break
				url=temp
				response = requests.get(url, stream=True)
				file_size = int(response.headers.get("Content-Length", 0))
				file_name = 'C://Users/gopis/Desktop/Jarvis/static/news.jpg'
				progress = tqdm(response.iter_content(1024), f"Downloading {file_name}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
				with open(file_name, "wb") as f:
					for data in progress:
						f.write(data)
						progress.update(len(data))
			except:
				print('no image')
			videos_link=[]
			for g in soup.find_all('div',class_='ZINbbc xpd O9g5cc uUPGi'):
				if('https://' in str(g)):
					if('youtube.com' in str(g)):
						videos_link.append(str(g)[str(g).index('https://'):str(g).index('&amp;')])
			if(len(videos_link)==0):
				if("’" in query):
					query=query[:query.index("’")]+query[query.index("’")+1:]
				html = urllib.request.urlopen("https://www.youtube.com/results?search_query="+query)
				video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
				if(len(video_ids)>5):
					for i in range(0,5):
						videos_link.append(video_ids[i])
				else:
					videos_link=video_ids
			News_dict_val={'max_news_videos':len(videos_link),'News_Title':records[news_no][3],'News_Edition':records[news_no][1],'News_Time':str(records[news_no][2]),'News_Ggle_desc':news_desc,'News_first_link':first_link_of_news}
			for i in range(0,len(videos_link)):
				st='Yt_'+str(i+1)
				News_dict_val[st]='https://www.youtube.com/embed/'+videos_link[i]
			return render(request,"Jarvis_Expand_News.html",News_dict_val)
			
'''
with hellow as source:
...     audio = r.record(source)
... try:
  File "<stdin>", line 3
    try:
      ^
SyntaxError: invalid syntax
>>> with hellow as source:
...     audio = r.record(source)
...     s = r.recognize_google(audio)
...     print("Text: "+s)


	
	
	
	
def aud_tag(request):
	inp= request.POST.get('param1')
	#return render(request,'speech_to_text.html',{'data':data})
	out= run([sys.executable,'C:\\Users\\gopis\\Project1\\jarvis_test.py',inp],shell=False,stdout=PIPE)
	print(out)
	new_var = out.stdout.decode('latin1')
	index=0
	inp1="tell me a joke"
	out1= run([sys.executable,'C:\\Users\\gopis\\Project1\\jarvis_test.py',inp1],shell=False,stdout=PIPE)
	joke_var=out1.stdout.decode('latin1')
	joke='\n' + joke_var[78:]
	print("joke = " + joke)
	
	#print(type(inp))
	
	f=open('for_displaying_message.txt','r')
	for each_line in f.readlines():
		fl=int(each_line)
	f.close()
	if(fl>0):
		f=open('display_message.txt','r')
		for each_line in f.readlines():
			msg1=each_line			
		f.close()
		return render(request,'Jarvis_message.html',{'msg1':msg1})
	elif (('play' in str(inp) or 'next' in str(inp)) and 'video' in str(inp)):
		#print("1")
		for i in range(3,len(new_var)):
			if((i)=='4' and (i-1)=='p' and (i-2)=='m' and (i-3)=='.'):
				break
			else:
				index=index+1
		print("Index: {}".format(index))
		print("\n The video song is : " + new_var[102:(index+1)] +"Hi gopi")
		return render(request,'play_video.html',{'outp1':new_var[102:(index+1)],"joke1":joke})
	elif ('play' in str(inp) or 'next' in str(inp) or 'sing' in str(inp) and 'song' in str(inp)):
		for i in range(3,len(new_var)):
			if((i)=='3' and (i-1)=='p' and (i-2)=='m' and (i-3)=='.'):
				break
			else:
				index=index+1
		print("Index: {}".format(index))		
		print("\n The song is : " + new_var[96:(index+1)] +"Hi gopi")
		print("The command is : " + inp)
		#print("2")
		return render(request,'play_song.html',{'outp1':new_var[96:(index+1)],"joke1":joke})
	elif ('play' in str(inp)):
		for i in range(3,len(new_var)):
			if((i)=='d' and (i-1)=='e' and (i-2)=='b' and (i-3)=='m'):
				break
			else:
				index=index+1
		print("\n The youtube video is : " + new_var[116:(index+1)] +"Hi gopi")
		return render(request,'play_youtube_video.html',{'outp1':new_var[116:(index+1)],"joke1":joke})
	elif("who are you" in str(inp) or "what is your name" in str(inp) or "your name" in str(inp) or "may I know your name" in str(inp) or
	   'weather' in str(inp) or 'rename' in str(inp) or 'change your name' in str(inp)):
		return render(request,'Response_page_jarvis.html',{"joke1":joke})
	elif('schedule' in str(inp)):
		schedule='\n'+new_var[100:]
		print("schedule = " + schedule)
		return render(request,'new_header1.html',{"sched1":schedule,"joke1":joke})	
	#return render(request,'Response_page_jarvis.html',{"joke1":joke})
	return render(request,'new_header1.html',{"joke1":joke})
'''	
	
	