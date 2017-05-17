#coding=utf-8
#Memorycheck Ver1.1

import subprocess
import os
import time
import shutil
import threading

#定义设备连接状态
def DeviceStatus():
    global deviceArray
    deviceStatus=subprocess.Popen('adb devices',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    deviceIndexed=deviceStatus.stdout.read()
    deviceArray=deviceIndexed.split()
    return len(deviceArray)

#运行monkey
while(DeviceStatus()==4):
    print('设备未连接，请打开usb调试重新插入usb数据线连接设备')
    devices=False
    time.sleep(10)
if(DeviceStatus()==6):
    #设备连接成功，重启设备
    print(time.ctime()+'设备重启，请稍后')
    subprocess.Popen('adb reboot',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    time.sleep(90)
    #等待设备重启成功
    while(DeviceStatus()==4):
        print('等待adb连接')
        devices=False
        time.sleep(10)
    if(DeviceStatus()==6):
        #获取设备名称和版本号
        productName=os.popen('adb shell getprop ro.product.board').readline().strip('\n')
        swVersion=os.popen('adb shell getprop ro.gn.gnznvernumber').readline().strip('\n')        
        #建result文件夹
        def createResultDir():
            resultpath=(".\Result")
            resultpathisExists=os.path.exists(resultpath)
            if not resultpathisExists:
                os.makedirs(resultpath)
            resultFolder=resultpath+os.path.sep+productName+os.path.sep+swVersion+os.path.sep+time.strftime("%Y-%m-%d",time.localtime())
            resultFolderIsExists=os.path.exists(resultFolder)
            if not resultFolderIsExists:
                os.makedirs(resultFolder)
            return resultFolder+os.path.sep

        #创建log文件夹
        def createadbLogDir():
            logpath=(".\Logs")
            logpathisExists=os.path.exists(logpath)
            if not logpathisExists:
                os.makedirs(logpath)
            logFolder=logpath+os.path.sep+productName+os.path.sep+swVersion+os.path.sep+time.strftime("%Y-%m-%d",time.localtime())
            logFolderIsExists=os.path.exists(logFolder)
            if not logFolderIsExists:
                os.makedirs(logFolder)
            return logFolder+os.path.sep
        #创建packageinfo存放文件夹
        def packagelistsDir():
            packagelistsPath=(".\Packagelists")
            packagelistsPathisExists=os.path.exists(packagelistsPath)
            if not packagelistsPathisExists:
                os.makedirs(packagelistsPath)
            packagelistsFolder=packagelistsPath+os.path.sep+productName+os.path.sep+swVersion
            packagelistsFolderIsExists=os.path.exists(packagelistsFolder)
            if not packagelistsFolderIsExists:
                os.makedirs(packagelistsFolder)
            return packagelistsFolder+os.path.sep
        #定义Monkey运行状态
        def MonkeyStatus():
            global monkeyArray
            monkeyStatus=subprocess.Popen('adb shell "ps | grep monkey"',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
            monkeyIndexed=monkeyStatus.stdout.read()
            monkeyArray=monkeyIndexed.split()
            return len(monkeyArray)
        
        #定义文件名称规则
        resultdir=createResultDir()
        adblogsdir=createadbLogDir()
        packagelistsdir=packagelistsDir()
        packagelistsfilename=packagelistsdir+productName+"_package_name_info.txt"

        #获取开机内存
        print(time.ctime()+'adb连接成功，正在获取测试前内存信息')
        subprocess.Popen('adb shell dumpsys meminfo > '+resultdir+'meminfo_before_test_'+time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())+'.txt',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)

        #连接设备，获取包名
        print(time.ctime()+'开始获取应用信息')
        os.system('adb install -r packageview.apk')
        os.system('adb shell am start -n com.gionee.packages/com.gionee.packages.MainActivity')
        os.system('adb pull /sdcard/packages_visual.txt '+packagelistsfilename)
        os.system('adb uninstall com.gionee.packages')
        print(time.ctime()+'应用信息获取成功，开始分析生成应用列表')

        #将包名导入到列表中
        openapplists=open(packagelistsfilename,'r')
        applists=openapplists.readlines()
        openapplists.close()
        applist=dict(zip(applists,applists))
        print(time.ctime()+'应用列表生成完毕，共'+str(len(applists))+'个应用')

        #开始执行不拆分测试
        testpackages=('')
        for line in applists:
            line=line.strip('\n')
            testpackages +=('-p '+line+' ')

        print(time.ctime()+'等待5分钟开始执行测试')
        time.sleep(300)
        print(time.ctime()+'开始执行monkey测试')
        subprocess.Popen('adb shell monkey -s 1 '+testpackages+'--throttle 500 --ignore-crashes --ignore-security-exceptions --ignore-timeouts --monitor-native-crashes -v -v 172800 > '+adblogsdir+'monkey_logs_'+time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())+'.txt',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)

        def monkeytest():
            while(DeviceStatus()==6):
                if(MonkeyStatus()==0):
                    print(time.ctime()+'monkey测试中断，重启monkey测试')
                    subprocess.Popen('adb shell monkey -s 1 '+testpackages+'--throttle 500 --ignore-crashes --ignore-security-exceptions --ignore-timeouts --monitor-native-crashes -v -v 172800 > '+adblogsdir+'monkey_logs_'+time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())+'.txt',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
                    time.sleep(30)
                else:
                    print(time.ctime()+'monkey进程正常')
                    time.sleep(30)
                
        def memorycheckresult():
            while(DeviceStatus()==6):
                time.sleep(300)
                print(time.ctime()+'正在获取内存信息')
                subprocess.Popen('adb shell dumpsys meminfo > '+resultdir+'meminfo_'+time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())+'.txt',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)

                
        threads = []
        t1 = threading.Thread(target=monkeytest)
        threads.append(t1)
        t2 = threading.Thread(target=memorycheckresult)
        threads.append(t2)

        if __name__ == '__main__':
            for t in threads:
                t.setDaemon(True)
                t.start()
                
            t.join()
            
            print(time.ctime()+'测试结束')
            os.system('pause')

'''
    print(time.ctime()+'开始执行monkey测试')
        subprocess.Popen('adb shell monkey -s 1 '+testpackages+'--throttle 500 --ignore-crashes --ignore-security-exceptions --ignore-timeouts --monitor-native-crashes -v -v -v 172800 > '+adblogsdir+'monkey_logs_'+time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())+'.txt',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        while(DeviceStatus()==6):
            time.sleep(300)
            print(time.ctime()+'正在获取内存信息')
            subprocess.Popen('adb shell dumpsys meminfo > '+resultdir+'meminfo_'+time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())+'.txt',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
            if(MonkeyStatus()==0):
                print(time.ctime()+'Monkey进程终止，测试停止')
                os.system('pause')
                break
'''

'''
    #开始执行单app拆分测试
    print('等待5分钟开始执行测试')
    time.sleep(300)
    print('开始执行monkey测试')
    for key in applist.keys():
        app = applist[key].split("\n")[0]
        print(time.ctime()+'正在测试应用的包名：'+app)
        os.system('adb shell monkey -s 1 -p '+app+' --throttle 500 --ignore-crashes --ignore-security-exceptions --ignore-timeouts -v -v 10000 > '+adblogsdir+app+'_monkey_logs_'+time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())+'.txt')
        while(DeviceStatus()==6):
            time.sleep(300)
            print(time.ctime()+'正在抓取内存信息')
            os.system('adb shell dumpsys meminfo > '+resultdir+'meminfo_'+time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())+'.txt')
            if(MonkeyStatus()==0):
                break
'''
