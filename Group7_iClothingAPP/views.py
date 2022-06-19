from django.shortcuts import render, redirect
from django.http.response import HttpResponse, JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
import cloudinary

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
import requests
#from bs4 import BeautifulSoup
import time

def Homepage(request):
	items=[]
	price=[]
	item_path=[]
	dict={}
	try:
		DATABASE_URL = os.environ.get('DATABASE_URL')
		connection = psycopg2.connect(DATABASE_URL)
		cursor = connection.cursor()
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
	#return render(request,'HomePage.html',{'total_no_products':3})

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
	fail_creation=''
	if(reg_pass == reg_pass1):
		try:
			DATABASE_URL = os.environ.get('DATABASE_URL')
			connection = psycopg2.connect(DATABASE_URL)
			cursor = connection.cursor()
			#print(reg_usr+' '+reg_pass+' '+reg_email+' '+reg_type)
			if(reg_type=='User'):
				acct_status_Active='Active'
				fail_creation='Account Created'
			else:
				acct_status_Active='Inactive'
				fail_creation='Account requested and awaiting for admin approval'
			insrt_qry="insert into user_login values('"+reg_usr+"','"+reg_pass+"','"+reg_email+"','"+reg_type+"','"+acct_status_Active+"');"
			print(insrt_qry)
			cursor.execute(insrt_qry)
			connection.commit()
		except Error as e:
			print("Error while connecting to MySQL", e)
			usr_exist='Username Already Taken'
			return render(request,'LoginPage.html',{'fail_creation':usr_exist})
		return render(request,'LoginPage.html',{'fail_creation':fail_creation})
	else:
		pass_not_matched='Both Passwords not matched'
		return render(request,'LoginPage.html',{'fail_creation':pass_not_matched})

def login_request(request):
	login_usr= request.POST.get('login_username')
	login_pass= request.POST.get('login_password')
	dict={}
	items=[]
	price=[]
	item_path=[]
	try:
		DATABASE_URL = os.environ.get('DATABASE_URL')
		connection = psycopg2.connect(DATABASE_URL)
		cursor = connection.cursor()
		login_chk_qry="select count(*),account_type,account_status from user_login where username='"+login_usr+"' and password='"+login_pass+"' group by account_type,account_status;"
		print(login_chk_qry)
		cursor.execute(login_chk_qry)
		record = cursor.fetchall()
		print(record)
		try:
			if(record[0][0]==1):
				if(record[0][2]=='Active'):
					if(record[0][1]=='User'):
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
						#dict['total_no_products']=22
						dict['user_name']=login_usr
						#print(dict)
						return render(request,'User_after_login.html',dict)
						#return render(request,'User_after_login.html',{'user_name':login_usr})
					elif(record[0][1]=='Admin'):
						dict={}
						login_chk_qry="select username,email_id from user_login where account_type='Admin' and account_status='Inactive';"
						cursor.execute(login_chk_qry)
						record=cursor.fetchall()
						print(record)
						for i in range(1,len(record)+1):
							dict['user_name_'+str(i)]=record[i-1][0]
							dict['Email_id_'+str(i)]=record[i-1][1]
						dict['total_no_users']=len(record)
						dict['total_no_products']=len(record)
						if(len(record)==0):
							dict['no_requests']='No requests Approval Pending'
						print(dict)
						return render(request,'Admin_after_login.html',dict)
						#return render(request,'Admin_after_login.html')
					else:
						return render(request,'LoginPage.html')
				else:
					login_invalid='Account is Inactive'
		except:
			login_invalid='Invalid Credentials'
	except Error as e:
		print("Error while connecting to MySQL : ", e)
	return render(request,'LoginPage.html',{'login_invalid':login_invalid})

def retrieve_cred(request):
	return render(request,'Retrieve_credentials.html')

def logout_request(request):
	return render(request,'LoginPage.html',{'login_invalid':'Logged out Successfully'})

def saved_Address(request):
	usernm=request.POST.get('user_name1')
	print(usernm)
	return render(request,'saved_Address.html',{'user_name':usernm})

def add_Address(request):
	usernm=request.POST.get('user_name1')
	street=request.POST.get('street')
	apt=request.POST.get('Apt')
	city=request.POST.get('city')
	state=request.POST.get('state')
	pincode=request.POST.get('pincode')
	mobile=request.POST.get('mobile')
	try:
		DATABASE_URL = os.environ.get('DATABASE_URL')
		connection = psycopg2.connect(DATABASE_URL)
		cursor = connection.cursor()
		login_chk_qry='select count(*) from user_login where username="'+usernm+'";'
		print(login_chk_qry)
		cursor.execute(login_chk_qry)
		record = cursor.fetchone()
		print(record)
		if(record[0]==1):
			insert_qry="insert into user_address values('"+usernm+"','"+street+"','"+apt+"','"+city+"','"+state+"','"+pincode+"','"+mobile+"');"
			print(insert_qry)
			cursor.execute(insert_qry)
			connection.commit()
			return render(request,'saved_Address.html',{'user_name':usernm,'Status_of_address':'Address saved successfully'})
		else:
			return render(request,'saved_Address.html',{'user_name':usernm,'Status_of_address':'Address not saved successfully'})
	except Error as e:
		print("Error while connecting to MySQL", e)
	return render(request,'saved_Address.html',{'user_name':usernm,'Status_of_address':'Address not saved successfully'})

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
		DATABASE_URL = os.environ.get('DATABASE_URL')
		connection = psycopg2.connect(DATABASE_URL)
		cursor = connection.cursor()
		login_chk_qry="update user_login set account_status='"+stat+"' where username='"+user_name+"';"
		print(login_chk_qry)
		cursor.execute(login_chk_qry)
		dict['done_stat']='User '+status+' Successfully'
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
		DATABASE_URL = os.environ.get('DATABASE_URL')
		connection = psycopg2.connect(DATABASE_URL)
		cursor = connection.cursor()
		login_chk_qry="select max(item_no) from items;"
		print(login_chk_qry)
		cursor.execute(login_chk_qry)
		record=cursor.fetchone()
		print(record)
		try:
			if record[0] is None:
				name_no=0
			else:
				name_no=record[0]
		except:
			name_no=0
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
			#fs = FileSystemStorage(path)
			#filename = fs.save(myfile.name, myfile)
			#filename = fs.save('C:\Group7_iClothingAPP\static\Women', myfile)
			#uploaded_file_url = fs.url(filename)
			#cloudinary.uploader.upload("my_picture.jpg")
			myfile.name=department_name+str(time.strftime("%Y%m%d-%H%M"))+str(name_no)+'.png'
			cld=cloudinary.uploader.upload(myfile,use_filename = True, unique_filename = False)
			#print(cld)
			path=cld['secure_url']
			dict['stat_new_item']='Item Successfully added to database.'
			insrt_qry="insert into items values ("+str(name_no)+",'"+item_name+"','"+tab_dep_name+"','"+path+"','"+item_brand+"','"+item_size+"','"+str(item_price)+"','"+item_description+"',"+item_tot+");"
			print(insrt_qry)
			cursor.execute(insrt_qry)
			connection.commit()
			return render(request,'Admin_Upload_New.html',dict)
	except Error as e:
		print("Error while connecting to MySQL", e)
	return render(request,'Admin_Upload_New.html',dict)

def open_cart(request):
	usernm=request.POST.get('user_name1')
	no_of_items_cart=request.POST.get('cart_val')
	item_paths=request.POST.get('cart_click')
	
	return render(request,'User_Shopping_Cart.html')







