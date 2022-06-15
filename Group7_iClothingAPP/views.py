from django.shortcuts import render, redirect
from django.http.response import HttpResponse, JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages

#import mysql.connector
#from mysql.connector import Error

import json
import os

import sys
from subprocess import run,PIPE

import mimetypes
from django import forms

from django.conf import settings
from django.core.files.storage import FileSystemStorage
# Create your views here.

#import psycopg2
#import pandas as pd
import re
#import reverse_geocoder as rg

import urllib
#import requests
#from bs4 import BeautifulSoup


def Homepage(request):
	return render(request,'HomePage.html')

def login(request):
	return render(request,'LoginPage.html')

def abt_cmpy(request):
	return render(request,'abtpage.html')

def cart_lgn(request):
	return render(request,'cartloginPage.html')

def rld_hmpg(request):
	return render(request,'HomePage.html')




def register(request):
	reg_usr= request.POST.get('reg_username')
	reg_email= request.POST.get('reg_email')
	reg_pass= request.POST.get('reg_password')
	reg_pass1= request.POST.get('reg_password1')
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
				insrt_qry='insert into user_login values("'+reg_usr+'","'+reg_pass+'","'+reg_email+'");'
				print(insrt_qry)
				cursor.execute(insrt_qry)
				connection.commit()
		except Error as e:
			print("Error while connecting to MySQL", e)
			usr_exist='Username Already Taken'
			return render(request,'Home_Page.html',{'fail_creation':usr_exist})
		finally:
			if (connection.is_connected()):
				cursor.close()
				connection.close()
				print("MySQL connection is closed")
		return render(request,'Home_Page.html')
	else:
		pass_not_matched='Both Passwords not matched'
		return render(request,'Home_Page.html',{'fail_creation':pass_not_matched})

def logout_request(request):
	return render(request,'Home_Page.html')

def homepage(request):
    return render(request = request,
                  template_name='main/home.html')

def login_request(request):
	login_usr= request.POST.get('login_username')
	login_pass= request.POST.get('login_password')
	inp= request.POST.get('user_location')
	print(inp)
	#temp_atmos,daily_status,week_status,User_location=weather_today(inp)
	#return render(request,'weather_web.html',{'Temp_Atmosphere':temp_atmos,"Daily_status":daily_status,"Weekly_status":week_status,'User_location':User_location})
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='Gopisairam@1')                                         
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			login_chk_qry='select count(*) from user_login where username="'+login_usr+'" and password="'+login_pass+'";'
			print(login_chk_qry)
			cursor.execute(login_chk_qry)
			record = cursor.fetchone()
			print(record)
			if(record[0]==1):
				numbers = re.findall('[0-9]+', inp)
				coordinates=(float(numbers[0]+'.'+numbers[1]),float(numbers[2]+'.'+numbers[3]))
				result=rg.search(coordinates)
				results_df=pd.DataFrame(result)
				User_location=results_df.loc[0][2].split(',')[0] + ',' + results_df.loc[0][3].split(',')[0]
				User_location=User_location.replace(' ','')
				print(User_location)
				print("select count(*) from news where location='"+User_location+"';")
				cursor.execute("select count(*) from news where location='"+User_location+"';")
				tot=cursor.fetchone()
				print(tot)
				if(tot[0]==0):
					print('new fetch')
					query = User_location.replace(' ', '+')
					URL = f"https://news.google.com/search?q={query}"
					resp = requests.get(URL)
					soup = BeautifulSoup(resp.content, "html.parser")
					i=0
					for g in soup.find_all('h3'):
						if(i==1):
							for h in soup.find_all('h4'):            
								i=i+1
						sql_insert="insert into News values ('" + User_location + "','" + (g.get_text().replace("'",' '))  +"','" + login_usr +"','2021-05-05');"
						print(sql_insert)
						cursor.execute(sql_insert)
						connection.commit()
						i=i+1
				print("select news_headline from news where location='"+User_location+"';")
				cursor.execute("select news_headline from news where location='"+User_location+"' limit 5;")
				print('fetch done')
				headlines=cursor.fetchall()
				print(headlines)
				news_hedlns2=headlines[1][0]
				news_hedlns3=headlines[2][0]
				news_hedlns4=headlines[3][0]
				news_hedlns5=headlines[4][0]
				news_hedlns1=headlines[0][0]	
				try:
					print('fetch data from table')
					cursor.execute("select temp,daily_stat,week_stat from user_weather_location where location_name='"+User_location+"';")
					weather=cursor.fetchone()
					temp_atmos=weather[0]
					daily_status=weather[1]
					week_status=weather[2]
					return render(request,'new_header1.html',{'user_name':login_usr,'Temp_Atmosphere':temp_atmos,'Daily_status':daily_status,'Weekly_status':week_status,'User_location':User_location,'headline_1':news_hedlns1,'headline_2':news_hedlns2,'headline_3':news_hedlns3,'headline_4':news_hedlns4,'headline_5':news_hedlns5})
				except:
					print('fetch weather using beautiful soup')
					URL=f"https://darksky.net/forecast/" + (numbers[0]+'.'+numbers[1]) + ',' + (numbers[2]+'.'+numbers[3]) +'/'
					resp = requests.get(URL)
					soup = BeautifulSoup(resp.content, "html.parser")
					for g in soup.find_all('span',class_='summary swap'):
						temp_atmos=g.get_text()
					for g in soup.find_all('span',class_='currently__summary next swap'):
						daily_status=g.get_text().split('\n')[2].strip()
					for g in soup.find_all('div',class_='summary'):
						week_status=g.get_text()
						week_status=week_status.strip()
						print('insert query: '+week_status)
						insrt_qry="insert into user_weather_location values('"+User_location+"','"+temp_atmos+"','"+daily_status+"','"+week_status+"','"+login_usr+"');"
						print(insrt_qry)
						cursor.execute(insrt_qry)
						connection.commit()
					return render(request,'new_header1.html',{'user_name':login_usr,'Temp_Atmosphere':temp_atmos,'Daily_status':daily_status,'Weekly_status':week_status,'User_location':User_location,'headline_1':news_hedlns1,'headline_2':news_hedlns2,'headline_3':news_hedlns3,'headline_4':news_hedlns4,'headline_5':news_hedlns5})
	except Error as e:
		print("Error while connecting to MySQL : ", e)
	finally:
		if (connection.is_connected()):
			cursor.close()
			connection.close()
			print("MySQL connection is closed")
	return render(request,'Home_Page.html')

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
	
	