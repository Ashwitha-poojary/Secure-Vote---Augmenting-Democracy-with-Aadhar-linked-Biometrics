import cv2
from imageMail import sendMail
from imageServer import uploadImage
import numpy as np
# import requests
# import RPi.GPIO as GPIO
import time

# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)




headers = {
    'cache-control': "no-cache"
}

# Add location of haarcascade_frontface_default
faceDetect = cv2.CascadeClassifier(r'''haarcascade_frontalface_alt2.xml''');
cam = cv2.VideoCapture(0);
rec = cv2.face.LBPHFaceRecognizer_create();
rec.read("recognizer/trainingData.yml");
id = 0
fontface = cv2.FONT_HERSHEY_SIMPLEX
fontsize = 1
fontcolor = (0,511,1)
count=0
c=0
while(True):
    ret,img = cam.read();
    image=img
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray,1.3,5);
    for(x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,180),2)
        id,conf = rec.predict(gray[y:y+h,x:x+w])
        print(conf);
        if(id==1 and conf<50):
            id="Person 1"
        elif(id==2 and conf<50):
            id="person 2"
        else:
            id="Stranger"
            count=count+1
            print(count)

        if(count>30):
            if(c!=1):
                
                # response = requests.request("GET", url, headers=headers, params=querystring)
                print("Unknown Person")
                cv2.imwrite("unknownperson.jpg", image)
                print('image saved')
                count=0
                uploadImage()
                # sendMail()
                
        cv2.putText(img,str(id),(x,y+h+25),fontface,fontsize,fontcolor,2);
        print(id)
    cv2.imshow("Face",img);

    if(cv2.waitKey(1)==ord('q')):
        break;
cam.release()
cv2.destroyAllWindows()
