import handler
import cv2

with open("data.txt","r") as f:
    bytes=f.read()
#print(bytes)

event={"video_data":bytes}

# a=cv2.imread("/Users/anupkashyap/Desktop/Test/frames/image-001.jpeg")
# print(a)
print(handler.face_recognition_handler(event,None))