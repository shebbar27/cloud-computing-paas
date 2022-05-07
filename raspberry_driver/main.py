import base64
import boto3
import datetime
import json
import os
import pi_camera_wrapper
import time
import threading
from concurrent.futures import ThreadPoolExecutor

RECORDINGS_FOLDER = "recordings/"
RESOLUTION = (640, 480)
CONTRAST = 10
CAPTURE_DURATION = 0.5
MAX_VIDEO_FILES_RETAINED = 10
PREVIEW_POSITION = (890, 20)

files_to_delete = []
session = boto3.Session(
        aws_access_key_id='AKIA3UZRGXK2UPNV6FXP',
        aws_secret_access_key='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')
client = session.client('lambda',region_name='us-east-1')

def main():
    start_time=time.time()
    pi_camera = pi_camera_wrapper.Camera(RESOLUTION, CONTRAST)
    exe = ThreadPoolExecutor(max_workers = 5)   
    for i in range(600):
        video_file_name = capture_video(pi_camera, CAPTURE_DURATION, RECORDINGS_FOLDER)
        exe.submit(call_face_recognition_lambda_service, video_file_name)
    print(str(time.time()-start_time)+" seconds taken.")

def launch_camera_preview(pi_camera):
    pi_camera.camera.preview_fullscreen=False
    pi_camera.camera.preview_window=(PREVIEW_POSITION[0], PREVIEW_POSITION[1], RESOLUTION[0], RESOLUTION[1])
    pi_camera.camera.start_preview()

def capture_video(pi_camera, capture_duration, recordings_folder):
    return pi_camera.capture_video(capture_duration, recordings_folder)

def call_face_recognition_lambda_service(video_file_name):
    start_time = time.time()
    with open(RECORDINGS_FOLDER + video_file_name, 'rb') as video_file:
        video_data_as_bytes = base64.b64encode(video_file.read())
        payload_dict = {
            'video_data': str(video_data_as_bytes, encoding='utf-8') 
        }
                
    response = client.invoke(
            FunctionName='face_recognition',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload_dict),
        )
    face_recognition_result = response['Payload'].read()
   
    face_recognition_result = face_recognition_result.decode('UTF-8')

    latency = time.time() - start_time
    if 'error' in face_recognition_result:
        pass
    elif 'No Face Detected' in face_recognition_result:
        print(f"{datetime.datetime.now().isoformat()} - {video_file_name} \t Latency: {latency: .3f} seconds\n{face_recognition_result}")
    elif 'Name' in face_recognition_result:
        face_recognition_result=face_recognition_result[1:-1]
        try:
            result_dict= json.loads(face_recognition_result.replace('\\\"','"').replace(" ","").replace("\\n",""))
        except Exception as e:
            print(e)
        formatted_result = f"{datetime.datetime.now().isoformat()} - {video_file_name} \t Latency: {latency: .3f} seconds\nName: {result_dict['Name']}\nID: {result_dict['Id']}\nMajor: {result_dict['Major']}\nYear: {result_dict['Year']}\n================================================\n\n"
        print(formatted_result)
    os.remove(RECORDINGS_FOLDER + video_file_name)

if __name__ == '__main__':
    main()