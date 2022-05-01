import eval_face_recognition
import base64
import boto3
import datetime
import os
import cv2
import numpy as np
import json


session = boto3.Session(
        aws_access_key_id='AKIA3UZRGXK2UPNV6FXP',
        aws_secret_access_key='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'
    )
s3 = session.client('s3')
dynamo_db=session.client('dynamodb')
name_id_map={'Sunaada':'1219580453','Krutarth':'1222317733','Anup':'1222119431'}
bucket_name="face-recog-videos"
tempVideoPath="/tmp/tempFile.h264"
frames_path="/tmp/frames/"
crop_path="/tmp/cropped_images/"
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
dynamo_db_table_name="studentInfo"

def get_student_id(name):
    response = dynamo_db.get_item(
    Key={
        'id': {
            'S': name_id_map[name],
        }
    },
    TableName=dynamo_db_table_name,
    )
    student_info={'Name':response['Item']['name']['S'],'Major':response['Item']['major']['S'],'Year':response['Item']['year']['S'],'Id':response['Item']['id']['S']}
    return json.dumps(student_info,indent=4)


def face_recognition_handler(event, context):	
	video_data=event["video_data"]
	video_bytes=bytes(video_data,'utf-8')
	with open(tempVideoPath,"wb") as temp_file:
		temp_file.write(base64.b64decode(video_bytes))

	response = s3.upload_file(tempVideoPath, bucket_name, "faceRecog"+str(datetime.datetime.now())+".h264")

	if os.path.exists(frames_path):
		os.system("rm "+ frames_path + "*")
	else:
		os.mkdir(frames_path)
	if os.path.exists(crop_path):
		os.system("rm "+ crop_path + "*")
	else:
		os.mkdir(crop_path)

	os.system("ffmpeg -i " + tempVideoPath + " -r 1 " + frames_path + "image-%3d.jpeg")
	frame_filenames = next(os.walk(frames_path), (None, None, []))[2]
	for frame in frame_filenames:
		full_frame_path=frames_path+frame
		img = cv2.imread(full_frame_path)

		faces_detected = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)
		if len(faces_detected) > 0:
			(x, y, w, h) = faces_detected[0]

			p = 10 #padding
			img_cropped = img[y-p+1:y+h+p, x-p+1:x+w+p]
			im_reshape = cv2.resize(img_cropped , (160, 160), interpolation=cv2.INTER_CUBIC)
			norm_img = np.zeros((im_reshape.shape[0], im_reshape.shape[1]))
			norm_img = cv2.normalize(im_reshape, norm_img, 0, 255, cv2.NORM_MINMAX)
			cv2.imwrite(crop_path + frame, norm_img)

			res=eval_face_recognition.face_recognition(crop_path + frame)
			return get_student_id(res)
		else:
			continue
	

	return "No Face Detected"
