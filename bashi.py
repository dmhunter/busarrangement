#-*- coding:utf-8 -*-
import time
import datetime
import random
def onbustime(distance,worktime):
#计算每个用户最迟上车时间
	onbustime=[]
	for i in range(len(distance)):
#转换时间格式
		wtime=datetime.datetime.strptime(worktime[i],"%H:%M")
#计算行驶时间
		waytime=float(distance[i])/60*3600
#最迟上车时间
		onbustime.append((wtime-datetime.timedelta(0,waytime)).ctime()[11:16])
	return onbustime

def randomdistance():
#产生200个随机距离，5-30公里之间。不同的距离数为40个。
#先随机产生40个不同的距离，再随机选择成为各个用户的距离
	dd=[]
	distance=[]
	for i in range(40):
		t="%.1f"%(5+random.random()*25)
		dd.append(t)
	for i in range(200):
		distance.append(dd[int(round(39*random.random()))])
#	print "类型：",type(distance[1])是str类型，注意运算时要转换成数值型
	return distance

def randomonworktime():
#随机产生一些上班时间，分为8:00，8:30，9:00，9:40这几种
	worktime=[]
	t=['8:00','8:30','9:00','9:30']
	for i in range(200):
		worktime.append(t[int(round(3*random.random()))])
	return worktime

def distimesort(distance,worktime):
#将产生的distance按距离从远到近进行排列，与此同时worktime也按照对应的distance的顺序排列
	dwdict=list()
	for i in range(len(distance)):
		dwdict.append({float(distance[i]):onbustime(distance,worktime)[i]})
	dwdictsort=sorted(dwdict,key=lambda x:x.keys()[0],reverse=True)
	return dwdictsort
#返回的数据格式为［{距离：最迟上车时间},{},{}..］

def ticketprice(distance):
#根据距离不同计算票价
	if distance<10:
		price=5
	else:
		if distance<20:
			price=8
		else:
			price=10
	return price

def commonsort(alist,blist,reverse=False):
#将alist与blist按相同顺序排序，其中alist默认按从小到大排序
	adict=list()
	for i in range(len(alist)):
		adict.append({alist[i]:i})
	adictsort=sorted(adict,key=lambda x:x.keys()[0],reverse=False)
	newalist,newblist=[],[]
	for i in adict:
		newalist.append(i.keys()[0])
		newblist.append(blist[i.values()[0]])
	return newalist,newblist


def perbus(data,startlocation,starttime):
#根据给定的巴士发车起始位置(距终点的距离)和发车时间，计算这趟巴士的收益与客户满意度的值
#data表示该线路上剩余未乘车的用户数据,数据格式为distimesort函数返回值
#先剔除比发车位置更远的用户
	userdata=data #尽量不更改函数参数原值
	busclientnum=0
	busrevenue=-60-float(startlocation)*1
	waitime=0
	busclientdata=[]#保存乘坐了这趟车的乘客信息
	for i in range(len(userdata)):
		if busclientnum>=20:
			break
		arrivetime=starttime+datetime.timedelta(0,float(60*userdata[i].keys()[0]/60))
		formattime=datetime.datetime.strptime(arrivetime.ctime()[11:16],'%H:%M')
		#print testtime
		if formattime<datetime.datetime.strptime(userdata[i].values()[0],"%H:%M"):
			busclientnum+=1
			busclientdata.append(i)
			waitime+=(datetime.datetime.strptime(userdata[i].values()[0],"%H:%M")-testtime).seconds/60
#datetime.datetime类型变量相减之后就变成datetime.timedelta类型了
			busrevenue+=ticketprice(userdata[i].keys()[0])
		else:
			continue		
	return busrevenue,waitime,busclientdata	

def goalfunc(data,n,startlocations,starttimes):
#计算目标函数，n趟巴士的总收益与客户满意度倒数的乘积
#先将startlocations数组与starttimes数组都按照发车时间先后顺序排序
	begintimes,beginlocations=commonsort(starttimes,startlocations,reverse=False)
	busrevenue,waitime,clientnum=0,1,0
	userdata=data
	for i in range(n):
		if not userdata:
			break
		revenue,time,clientdata=perbus(userdata,beginlocations[i],begintimes[i])
		if clientdata:
			busrevenue+=revenue
			waitime+=time
			clientnum+=len(clientdata)
			clientlist=[]
			for j in range(len(userdata)):
				if j not in clientdata:
					clientlist.append(userdata[j])
			userdata=clientlist
		else:
			break
	return busrevenue,waitime,(float(clientnum)/(n*20))*busrevenue*busrevenue/waitime,clientnum

def randparams(distance):
#产生随机参数作为goalfunc函数中除data之外的参数
	randomparams=[]
	n=random.randint(1,20)#产生随机巴士数量
	randomparams.append(n)
	startlocations,starttimes=[],[]
	for i in range(n):
#起始位置肯定要设置在用户候车处		
		startlocations.append(list(set(distance))[random.randint(0,len(set(distance))-1)])
		starttimes.append(datetime.datetime(1900,1,1,7,30)+datetime.timedelta(0,random.randint(0,120)*60))
	randomparams.append(startlocations)
	randomparams.append(starttimes)
	return randomparams

def randomoptimize(data,distance,randomparams=randparams,goalfunc=goalfunc):
#randomparams是goalfunc函数的随机参数列表
	bestresult=0
	bestparams=[]
	for i in range(10000):
		params=randomparams(distance)
		revenue,waitime,goal,clientnum=goalfunc(data,params[0],params[1],params[2])
		if goal>bestresult and revenue>0:
			bestresult=goal
			bestparams=params
		print "Revenue:",revenue,"Waitime:",waitime,"Goal:",goal
	totalrevenue,totalwaitime,finalgoal,totalclientnum=goalfunc(data,bestparams[0],bestparams[1],bestparams[2])
	return bestparams,bestresult,totalrevenue,totalwaitime,totalclientnum


def main():
	worktime=randomonworktime()
	distance=randomdistance()
	userbustime=onbustime(distance,worktime)
	data=distimesort(distance,worktime)
	print data 
	bestparams,bestresult,revenue,waitime,totalclientnum=randomoptimize(data,distance)
	print "最佳参数：",bestparams,'\n',"指标最佳值：",bestresult,"净收入：",revenue,"乘客总等待时间：",waitime,"乘客总人数：",totalclientnum,'\n'

if __name__=="__main__":
	main()
