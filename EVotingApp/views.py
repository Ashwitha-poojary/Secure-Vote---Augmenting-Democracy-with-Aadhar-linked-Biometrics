from django.shortcuts import render, redirect
from django.http import JsonResponse
from EVotingApp.models import *
from django.db.models import Count
from datetime import datetime
from dateutil.relativedelta import relativedelta

import cv2
import numpy as np
import os
from PIL import Image
import time
import serial
import re
import time

PORT = 'COM7'
faceDetect = cv2.CascadeClassifier(r'''ImageProcessing/haarcascade_frontalface_alt2.xml''');
recognizer=cv2.face.LBPHFaceRecognizer_create();

#Assigning the training labels to the images in dataset using Python Method
def getImagesWithID(path):
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)]
    # print(imagePaths)
    faces=[]
    IDs=[]
    #Convert the images to grayscale for processing
    for imagePath in imagePaths:
        faceImg = Image.open(imagePath).convert('L');
        faceNp = np.array(faceImg,'uint8')
    
        #Tokenization of the images splitted into pixels
        ID = int(os.path.split(imagePath)[-1].split('.')[1])
        faces.append(faceNp)
        IDs.append(ID)
        # cv2.imshow("training",faceNp)
        cv2.waitKey(10)
    return IDs, faces

def collet_thumb(id):
    try:
        ser = serial.Serial(port=PORT,baudrate=9600,timeout=5)  # open serial port
               

        if ser.isOpen():
            print("Serial port is open.")
        else:
            print("Failed to open serial port.")
            return False

        while True:
            # print("Reading port....")
           
            ser.write(b"a")
            # time.sleep(3)
            data = ser.readline().decode().rstrip()
            print(data)
            
            if data.startswith("Stored!"):
                ser.close()
                print("Serial port closed.")
                return True  
                
            ser.write(id.encode())
            # time.sleep(3)
            data = ser.readline().decode().rstrip()
            print(data)
        

    except KeyboardInterrupt:
        # Clean up the serial port when the script is interrupted
        ser.close()
        print("Serial port closed.")
        return False

    return False


def verify_thumb(id):
    try:
        ser = serial.Serial(port=PORT,baudrate=9600,timeout=5)  # open serial port
               
        if ser.isOpen():
            print("Serial port is open.")
        else:
            print("Failed to open serial port.")
            return False

        while True:
            print("Reading port....")
           
            ser.write(b"s")
            time.sleep(5)
            data = ser.readline().decode('utf-8').strip()
            print(data)
            if data.startswith("$"):
                ser.close()
                accessed_id  = data[1]
                print("user id: ",accessed_id)
                print("Serial port closed.")

                if accessed_id == str(id):
                    print("match found")
                    return True
                else:
                    print("match not found")
                    return False
          
    except KeyboardInterrupt:
        # Clean up the serial port when the script is interrupted
        ser.close()
        print("Serial port closed.")
        return False


# Create your views here.

def index(request):
    return render(request, 'index.html')

def admin(request):
    return render(request, 'admin/index.html')

def user(request):
    return render(request, 'user/index.html')

def getUsers(request):
    data = User.objects.all().select_related()
    return render(request, 'admin/users.html', {"users": data})

def userStatus(request,id):
    data = User.objects.filter(id=id).get()
    if data.status == 1:
        data.status = 0
    else:
        data.status = 1
    data.save()
    return redirect('/admin/user/')

def addCandidate(request):
    constituency_list = Constituency.objects.all()
    party_list = Party.objects.all()
    res = {"constituency_list": constituency_list,"party_list": party_list}
    if request.method == 'POST':
        name=request.POST['name']
        dob=request.POST['dob']
        constituency=request.POST['constituency']
        party=request.POST['party']
        image_file=request.FILES['image']
        status=1

        data = Candidate(name=name, dob=dob, constituency_id=constituency, party_id=party, image=image_file, status=status)
        data.save()

        return render(request, 'admin/add_candidate.html', res)
    return render(request, 'admin/add_candidate.html', res)

def getCandidates(request):
    data = Candidate.objects.all().select_related()
    return render(request, 'admin/candidates.html', {"candidates": data})

def candidateStatus(request,id):
    data = Candidate.objects.filter(id=id).get()
    if data.status == 1:
        data.status = 0
    else:
        data.status = 1
    data.save()
    return redirect('/admin/candidate/')

def adminLogin(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]

        if ((username == "admin") and (password == "admin")):
            return redirect('/admin')
    return render(request, 'admin/login.html')

def userLogin(request):
    if request.method == 'POST':
        phone=request.POST['phone']
        password=request.POST["password"]
        datas = User.objects.filter(phone=phone, password=password).order_by('id')[:1]

        for data in datas:
            if data.phone == phone:
                request.session['user'] = data.id
                return redirect('/user/')
        return render(request,'user/login.html',{'error':'Invalid Login Credentials'})
    return render(request, 'user/login.html')

def userRegister(request):
    data = Constituency.objects.all()
    if request.method == 'POST':
        name=request.POST['name']
        email=request.POST['email']
        phone=request.POST['phone']
        Aadhaar=request.POST['Aadhaar']
        password=request.POST['password']
        dob=request.POST['dob']
        constituency=request.POST['constituency']
        status=1

        if User.objects.filter(phone=phone).exists():
            return render(request, 'user/register.html', {"error":"Duplicate Contact no", "options": data})
        elif User.objects.filter(aadhar=Aadhaar).exists():
            return render(request, 'user/register.html', {"error":"Duplicate Aadhaar no", "options": data})
        else:
            data = User(name=name, email=email, phone=phone, password=password, dob=dob, constituency_id=constituency, status=status, aadhar=Aadhaar)
            data.save()

        return render(request, 'user/login.html', {"success":"Registered Successfully"})
    return render(request, 'user/register.html', {"options": data})

def userVerification(request,user_id):
    if request.method == 'POST':
        # if not request.session.has_key('user'):
        #     return redirect('/user/login/')
        # user_id=request.session['user']

        cam = cv2.VideoCapture(0)
        sampleNum=0
        while(cv2.waitKey(1)!=27):
            ret,img = cam.read()
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            faces = faceDetect.detectMultiScale(gray,1.3,5);
            for(x,y,w,h) in faces:
                sampleNum += 1
                cv2.imwrite("ImageProcessing/dataset/User."+str(user_id)+"."+str(sampleNum)+".png",gray[y:y+h,x:x+w])
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,225),2)
                cv2.waitKey(100)
            cv2.imshow("Face",img);
            cv2.waitKey(1);
            if(sampleNum>100):
                break
        cam.release()
        cv2.destroyAllWindows()

        # #Assigning the test labels to the data trained
        IDs,faces = getImagesWithID('ImageProcessing/dataset')
        recognizer.train(faces,np.array(IDs))

        recognizer.write('ImageProcessing/recognizer/trainingData.yml')
        cv2.destroyAllWindows()

        return render(request, 'admin/user_verification.html', {"success":"Face Verified Successfully",'user_id':user_id})

    return render(request, 'admin/user_verification.html',{'user_id':user_id})

def thumb_verification(request,user_id):
    if request.method == 'POST':
       success = collet_thumb(str(user_id))
       if success:
           return render(request, 'admin/user_verification.html', {"success":"Thumb Procedure completed successfully",'user_id':user_id})
       else:
           return render(request, 'admin/user_verification.html', {"error":"Thumb Procedure failed or interrupted",'user_id':user_id})

    return render(request, 'admin/user_verification.html',{'user_id':user_id})

def verifyUser(request):
    if not request.session.has_key('user'):
        return redirect('/user/login/')
    user_id=request.session['user']
    user = User.objects.filter(id=user_id).first()
    user_age = relativedelta(datetime.today(), datetime.strptime(user.dob, '%Y-%m-%d'))
    res = {"user_age": user_age.years,"is_eligible": False if (user_age.years < 18) else True, "user_verified": True}

    if request.method == 'POST':
        Aadhaar = request.POST['Aadhaar']
        user_adhar = User.objects.filter(aadhar=Aadhaar).first()

        if user_adhar is None:
            response = {"user_age": user_age.years, "is_eligible": False if (user_age.years < 18) else True, "user_verified": True, "user_found": 0}
            return render(request, 'user/user_verify.html', response)
        else:
            if user_adhar.id != user_id:
                response = {"user_age": user_age.years, "is_eligible": False if (user_age.years < 18) else True, "user_verified": True, "user_found": 0}
                return render(request, 'user/user_verify.html', response)

        thumb_verified = verify_thumb(user_id) 

        if not thumb_verified:
            response = {"user_age": user_age.years, "is_eligible": False if (user_age.years < 18) else True, "user_verified": True, "user_found": 0,"error":"Failed to verify the thumb"}
            return render(request, 'user/user_verify.html', response) 
            
        cam = cv2.VideoCapture(0);
        rec = cv2.face.LBPHFaceRecognizer_create();
        rec.read("ImageProcessing/recognizer/trainingData.yml");
        id = 0
        fontface = cv2.FONT_HERSHEY_SIMPLEX
        fontsize = 1
        fontcolor = (0,511,1)
        userCount = 0
        strangerCount = 0
        userFound = False

        while(True):
            ret,img = cam.read();
            image=img
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            faces = faceDetect.detectMultiScale(gray,1.3,5);
            for(x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,180),2)
                id,conf = rec.predict(gray[y:y+h,x:x+w])
                if(id==user_id and conf<50):
                    id=user.name
                    userCount += 1
                else:
                    id="Stranger"
                    strangerCount += 1
                 
                cv2.putText(img,str(id),(x,y+h+25),fontface,fontsize,fontcolor,2);
            cv2.imshow("Face",img);

            if(userCount > 30):
                userFound = True
                break;
            if(strangerCount > 30):
                break;

            if(cv2.waitKey(1)==ord('q')):
                break;
        cam.release()
        cv2.destroyAllWindows()

        if userFound:
            request.session['verified_user'] = 1
            return redirect('/user/vote/')
        res = {"user_age": user_age.years, "is_eligible": False if (user_age.years < 18) else True, "user_verified": True, "user_found": 0}
    return render(request, 'user/user_verify.html', res)

def userVote(request):
    response = {}
    candidates_list = []
    if not request.session.has_key('verified_user'):
        return redirect('/user/verify/')
    if not request.session.has_key('user'):
        return redirect('/user/login/')
    user_id=request.session['user']
    user = User.objects.filter(id=user_id).select_related().first()

    today_date=datetime.today().strftime('%Y-%m-%d')

    # submit vote
    if request.method == 'POST':
        voted_to = request.POST['vote']
        user_vote = Vote.objects.filter(user_id=user_id, candidate_id=voted_to, vote_date=today_date).first()
        if user_vote == None:
            data = Vote(vote_date=today_date, user_id=user_id, candidate_id=voted_to)
            data.save()

    # vote details
    vote_info = VoteInfo.objects.first()
    vote_date = '' if vote_info == None else vote_info.vote_date
    is_vote_today = True if vote_date == today_date else False
    user_vote = Vote.objects.filter(user_id=user_id, vote_date=vote_date).first()

    candidates = Candidate.objects.filter(constituency_id=user.constituency.id).select_related()
    for candidate in candidates:
        vote = Vote.objects.filter(user_id=user_id, candidate_id=candidate.id, vote_date=vote_date).first()
        candidates_list.append({
            "vote_status": 0 if vote == None else 1,
            "details": candidate,
        })

    response = {
        "vote_date": vote_date,
        "is_vote_today": is_vote_today, 
        "is_voted": False if user_vote == None else True,
        "constituency": user.constituency.title,
        "candidates_list": candidates_list
    }
    return render(request, 'user/cast_vote.html', response)

def userResult(request):
    response = {}
    candidates_list = []
    
    if not request.session.has_key('user'):
        return redirect('/user/login/')
    user_id=request.session['user']
    user = User.objects.filter(id=user_id).select_related().first()

    today_date=datetime.today().strftime('%Y-%m-%d')

    # vote details
    vote_info = VoteInfo.objects.first()
    vote_date = '' if vote_info == None else vote_info.vote_date
    show_result = 0 if vote_info == None else vote_info.result_status
    user_vote = Vote.objects.filter(user_id=user_id, vote_date=vote_date).first()

    candidates = Candidate.objects.filter(constituency_id=user.constituency.id).select_related()
    for candidate in candidates:
        vote_count = Vote.objects.filter(candidate_id=candidate.id, vote_date=vote_date).count()
        candidates_list.append({
            "vote_count": vote_count,
            "details": candidate,
        })

    candidates_list_sorted = sorted(candidates_list, key=lambda x: x['vote_count'], reverse=True)

    response = {
        "show_result": show_result,
        "vote_date": vote_date,
        "constituency": user.constituency.title,
        "candidates_list": candidates_list_sorted
    }
    return render(request, 'user/vote_result.html', response)

def voteInfo(request):
    if request.method == 'POST':
        data = VoteInfo.objects.first()
        vote_date = request.POST['date']
        if data == None:
            data = VoteInfo(vote_date=vote_date, result_status=0)
            data.save()
        else:
            data.vote_date = vote_date
            data.save()

    info = VoteInfo.objects.first()
    res = {
        "info_id": 0 if info == None else info.id,
        "vote_date": '' if info == None else info.vote_date,
        "result_status": 0 if info == None else info.result_status
    }

    return render(request, 'admin/vote_info.html', res)

def resultStatus(request,id):
    data = VoteInfo.objects.first()
    if data.result_status == 1:
        data.result_status = 0
    else:
        data.result_status = 1
    data.save()
    return redirect('/admin/info/')

def logout(request):
    if request.session.has_key('user'):
        del request.session['user']
    if request.session.has_key('admin'):
        del request.session['admin']
    if request.session.has_key('verified_user'):
        del request.session['verified_user']
    return redirect('/')

def getUser(request):
    if request.method == 'GET':
        adhar=request.GET['aadhar']
        user_id=request.session['user']

        user = User.objects.filter(aadhar = adhar).first()
        if user:
            if user.id == user_id:
                response ={
                    'status':True,
                    'data': {
                        'name' : user.name,
                        'email' : user.email,
                        'phone' : user.phone,
                        'dob' : user.dob,
                        'constituency' : user.constituency.title
                    }
                }
                return JsonResponse(response)

        else:
            return JsonResponse({'status':False})
        return JsonResponse({'status':False})
            