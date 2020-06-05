import cv2 as cv;
import numpy;

cascade_path = "face_recognition\\data\\haar.xml";
cascade = cv.CascadeClassifier(cascade_path);

def face_recog(img):
	gray = cv.equalizeHist(cv.cvtColor(img, cv.COLOR_BGR2GRAY));
	face = cascade.detectMultiScale(gray);
	return face;

# image = cv.imread("face_recognition\\faces\\freeface.jpg");
# rect = face_recog(image);
# for (x, y, w, h) in rect:
#	print(x, y, w, h);
