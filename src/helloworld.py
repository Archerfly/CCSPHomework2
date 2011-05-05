# -*- coding: utf-8 -*-
import cgi
import os
import time
import re
import urllib
import urllib2
import sys
from BeautifulSoup import BeautifulSoup
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from django.utils import simplejson as json




#def fetchHtml(url):
#    r = urllib2.Request(url)
#    r.add_header('User-Agent', 'Mozilla 5.0')
#    page = urllib2.urlopen(r)
#    return page
    

class MainPage(webapp.RequestHandler):
    
    
    def get(self):
        self.response.out.write('吳明珠中醫診所API')

        
class deptPage(webapp.RequestHandler):     
    
    def get(self):
        if self.request.get('id') == '':
             
            array_dept=[]
            array_dept.append({"1":unicode('中醫科', 'utf-8')})
            jsonResult = json.dumps(array_dept,ensure_ascii=False)
            self.response.out.write(jsonResult) 
            
        elif self.request.get('id') == '1':
            #search dept
            array_dept=[]
            array_dept.append({"1":unicode('中醫科', 'utf-8')})
            #search doctor
            array_doctor=[]
            array_doctor.append({"1":unicode('吳明珠', 'utf-8')})
            
            #search time
            
            urlrequest =  urlfetch.fetch(url='http://cmed.ktop.com.tw/webreg.php?tp=reg2_1&id=3801201475&ip=10.241.61.113&bno=F127659156&bday=780925',deadline=10,allow_truncated=True)
            soup = BeautifulSoup(urlrequest.content)
            date_and_doctors = soup.findAll('a', href=re.compile(r'\/webreg\.php\?tp=reg2_2'))
            date_and_doctors_title = []
            
    
            for a in date_and_doctors:
                date_and_doctors_title.append(a['title'])
                

            
            dateStr = []
    
            for a in date_and_doctors_title:
                int_year = int(a[0:3])+1911
                months = a[4:6]
                date = a[7:9]
                str_year = ('%d' %(int_year))
                if a[12]!='六': 
                    strtempB = str_year+'-'+months+'-'+date+'-B'
                    dateStr.append(strtempB)
                    strtempC = str_year+'-'+months+'-'+date+'-C'
                    dateStr.append(strtempC)
                else:
                    strtempA = str_year+'-'+months+'-'+date+'-A'
                    dateStr.append(strtempA)
                    strtempB = str_year+'-'+months+'-'+date+'-B'
                    dateStr.append(strtempB)
                
                
            #result of search append to array 
            array=[]
            array.append({"id":'1'})
            array.append({"name":(array_dept[0])['1']})
            array.append({"doctor":array_doctor})
            array.append({"time":dateStr})
            jsonResult = json.dumps(array,ensure_ascii=False)
            self.response.out.write(jsonResult)
        else:
            self.response.out.write(unicode('沒有這個部門','utf-8'))
            


class doctorPage(webapp.RequestHandler):     
    
    def get(self):
        
        if self.request.get('id') =='':
            array=[]
            array.append({"1":unicode('吳明珠', 'utf-8')})
            jsonResult = json.dumps(array,ensure_ascii=False)
            self.response.out.write(jsonResult)
        elif self.request.get('id') == '1':
            #search dept
            array_dept=[]
            array_dept.append({"1":unicode('中醫科', 'utf-8')})
            #search doctor
            array_doctor=[]
            array_doctor.append({"1":unicode('吳明珠', 'utf-8')})
            
            #search time把那一頁的資料fetch下來 然後取出哪些時段有醫生
            urlrequest = urlfetch.fetch(url='http://cmed.ktop.com.tw/webreg.php?tp=reg2_1&id=3801201475&ip=10.241.61.113&bno=F127659156&bday=780925&x=41&y=7',deadline=10)
            soup = BeautifulSoup(urlrequest.content)
            date_and_doctors = soup.findAll('a', href=re.compile(r'\/webreg\.php\?tp=reg2_2'))
            date_and_doctors_title = []

    
            for a in date_and_doctors:
                date_and_doctors_title.append(a['title'])
               

            
            dateStr = []
            #把年月日取出來如果不為星期六其他時段都是BC
            for a in date_and_doctors_title:
                int_year = int(a[0:3])+1911
                months = a[4:6]
                date = a[7:9]
                if a[12]!='六': 
                    strtempB = str(int_year)+'-'+months+'-'+date+'-B'
                    dateStr.append(strtempB)
                    strtempC = str(int_year)+'-'+months+'-'+date+'-C'
                    dateStr.append(strtempC)
                else:
                    strtempA = str(int_year)+'-'+months+'-'+date+'-A'
                    dateStr.append(strtempA)
                    strtempB = str(int_year)+'-'+months+'-'+date+'-B'
                    dateStr.append(strtempB)
                
            #result of search append to array 
            array=[]
            array.append({"id":'1'})
            array.append({"name":(array_doctor[0])['1']})
            array.append({"dept":array_dept})
            array.append({"time":dateStr})
            jsonResult = json.dumps(array,ensure_ascii=False)
            self.response.out.write(jsonResult)
        else:
            self.response.out.write(unicode('沒有這個編號的醫生','utf-8')) 
            
            
class registerPage(webapp.RequestHandler): 
    def get(self):
        table_fill=True
        bday=''
        table_array=[]
        #判斷是否有給身分證
        if self.request.get('bno') =='':
            table_fill=False
            table_array.append({'bno':'身分證'})
        else:
            bno = self.request.get('bno')
            
        #判斷是否有給生日 
        if self.request.get('birthday') =='':
            table_fill=False
            table_array.append({'birthday':'生日'})
        else:
            birthday = self.request.get('birthday')
            #把生日轉換成醫院要的格式
            bday_year_temp = int(birthday[0:4])-1911
            bday_date_temp = birthday[5:7]+birthday[8:]
            bday = '0'+str(bday_year_temp)+bday_date_temp
           
        #判斷是否有給要選擇哪個掛號時段   
        if self.request.get('time') =='':
            table_fill=False
            table_array.append({'time':'掛號時段'})
        else:
            time = self.request.get('time') 
         
        #判斷是否有給是否為第一次看診     
        if self.request.get('first') =='':
            table_fill=False
            table_array.append({'first':'是否為第一次看診(True or False)'})
        else:
            first = self.request.get('first') 
            #先判斷是初診還是復診
            if first=='True':
            #下列五行為初診幫他註冊的程序
                if self.request.get('name') =='':
                    table_fill=False
                    table_array.append({'name':'姓名'})
                else:
                    name=self.request.get('name')    
            
                if self.request.get('tel') =='':
                    table_fill=False
                    table_array.append({'tel':'電話(eg:02-12345678)'})
                else:
                    tel=self.request.get('tel')
                
                if table_fill:
                    name_str = urllib.quote(name.encode('big5'))
                    urlstr = 'http://cmed.ktop.com.tw/webreg.php?tp=reg1_1&id=3801201475&ip=10.241.61.113&pname='+name_str+'&bno='+bno+'&bday='+bday+'&tel='+tel
                    urlfetch.fetch(url=urlstr,deadline=10)
#        birthday = '1989-09-25' 
#        time = '2011-05-06-B'             
#        first = True
#        tel='02-29047059'
#        name='徐聖哲'
        
        
            
        if table_fill:  
            #register2 
            registerUrl='http://cmed.ktop.com.tw/webreg.php?tp=reg2_1&id=3801201475&ip=10.241.61.113'+'&bno='+bno+'&bday='+ bday
            result = urlfetch.fetch(url=registerUrl,deadline=10) 
        
            #把醫生的連結都soup出來
            soup = BeautifulSoup(result.content)
            doctor_link = soup.findAll('a',href=re.compile(r'\/webreg\.php\?tp=reg2_2'))
         
            time_month=int(time[5:7])
            time_day = int(time[8:10])
            doctor_number = -1
            #因為有好多個連結 所以要看使用者選擇哪個時段 然後要取那一個時段的連結就好
            counter = 0
            for a in doctor_link:
                if time_month == int(a['title'][4:6]) and time_day == int(a['title'][7:9]):
                    doctor_number=counter
                counter +=1    
                    #確認使用者時段沒有輸入錯誤
            if doctor_number == -1:
                        self.response.out.write(unicode('您所輸入的日期沒有對應的醫生','utf-8'))
            else:    
            #日期沒有輸入錯誤的話 就會幫使用者選到醫生 接著就在把網頁fetch出來 取出診號 在弄成json格式傳出去
                registerUrl = 'http://cmed.ktop.com.tw'+doctor_link[doctor_number]['href'][0:12]+'tp=reg2_3'+doctor_link[doctor_number]['href'][21:]
                result3=urlfetch.fetch(url = registerUrl,deadline = 10)
                soup = BeautifulSoup(result3.content)
                number = soup.find('span','txt06')
                dic = {'ststus':'0','message':number.string[12:]}
                jsonResult = json.dumps(dic,ensure_ascii=False)
                self.response.out.write(jsonResult)
        else:
            dic = {'ststus':'2','message':table_array}
            jsonResult = json.dumps(dic,ensure_ascii=False)
            self.response.out.write(jsonResult)
            
class cancleRegisterPage(webapp.RequestHandler): 
    def get(self):
#        bno = 'F149642575'
#        bdaytemp = '1989-09-25'              
#        time = '2011-05-06-B'
        table_fill=True
        table_array=[]
        #判斷是否有給身分證
        if self.request.get('bno') =='':
            table_fill=False
            table_array.append({'bno':'身分證'})
        else:
            bno = self.request.get('bno')
            
        #判斷是否有給生日 
        if self.request.get('birthday') =='':
            table_fill=False
            table_array.append({'birthday':'生日'})
        else:
            birthday = self.request.get('birthday')
            #把生日轉換成醫院要的格式
            bday_year_temp = int(birthday[0:4])-1911
            bday_date_temp = birthday[5:7]+birthday[8:]
            bday = '0'+str(bday_year_temp)+bday_date_temp
           
        #判斷是否有給要選擇哪個掛號時段   
        if self.request.get('time') =='':
            table_fill=False
            table_array.append({'time':'掛號時段'})
        else:
            time = self.request.get('time') 
        
        if table_fill:
            #find cancle_register url 
            #feach 輸入身分證以及生日之後進入的網頁 裡面有一個包含有hisid的link把他，用soup取得他之後我們就可以進入完成取消掛號的那一頁
            cancleregisterUrl='http://cmed.ktop.com.tw/webreg.php?tp=reg4_1&id=3801201475&ip=10.241.61.113'+'&bno='+bno+'&bday='+ bday
            result = urlfetch.fetch(url = cancleregisterUrl,deadline = 10)
            soup = BeautifulSoup(result.content)
            cancle_links = soup.findAll('a',href=re.compile(r'hisid'))
            cancle_link = ''
            for a in cancle_links:
                date_str = a.parent.previousSibling.previousSibling.previousSibling.previousSibling.previousSibling.previousSibling
                datetemp = time[5:7]+'/'+time[8:10]
                if datetemp==date_str.string[4:]:
                    cancle_link=a['href']
            if cancle_link == '':
                self.response.out.write('你沒有在這個日期掛號')
            else:
                #cancle_register 進入完成取消掛號的那一頁之後取得他的取消完成資訊 確認無誤後就把json格式的狀態碼傳出去
                cancleregisterUrl = 'http://cmed.ktop.com.tw'+cancle_link[0:12]+'tp=reg4_3'+cancle_link[21:]
                urlfetch.fetch(url = cancleregisterUrl,deadline = 10)
                dic = {'ststus':'0'}
                jsonResult = json.dumps(dic,ensure_ascii=False)
                self.response.out.write(jsonResult)
#                #cancle_register 進入完成取消掛號的那一頁之後取得他的取消完成資訊 確認無誤後就把json格式的狀態碼傳出去
#                cancleregisterUrl = 'http://cmed.ktop.com.tw'+cancle_link[0:12]+'tp=reg4_3'+cancle_link[21:]
#                result2 = urlfetch.fetch(url = cancleregisterUrl,deadline = 10)
#                soup = BeautifulSoup(result2.content)
#                cancle_message_cls = soup.find('center')
#                
#                if cancle_message_cls.next.string == '取消網路掛號成功':  
#                    dic = {'ststus':'0'}
#                    jsonResult = json.dumps(dic,ensure_ascii=False)
#                    self.response.out.write(jsonResult)
        else: 
            dic = {'ststus':'2','message':table_array}
            jsonResult = json.dumps(dic,ensure_ascii=False)
            self.response.out.write(jsonResult)
            
application = webapp.WSGIApplication([('/', MainPage),
                                      ('/wmc/dept',deptPage),
                                      ('/wmc/doctor',doctorPage),
                                      ('/wmc/register',registerPage),
                                      ('/wmc/cancel_register',cancleRegisterPage)], debug=True)



def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
