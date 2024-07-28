
# Create your tests here.
import requests
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import os
from dotenv import load_dotenv


class APIClient(object):

    def __init__(self):

        load_dotenv() 
        self.BASE_URL = 'http://localhost:8000/api/v1'
        self.endpoints = {
            'login':f'{self.BASE_URL}/token',
            'register':f'{self.BASE_URL}/register',
            'get-current-user':f'{self.BASE_URL}/users/me',
            'get-workspaces':f'{self.BASE_URL}/workspace',
            'delete-workspace':f'{self.BASE_URL}/workspace',
            'create-workspace':f'{self.BASE_URL}/workspace',
            'create-zeros-poles':f'{self.BASE_URL}/workspace',
            
        }

        self.headers = None
        self.access_token = None
        
        if 'ACCESS_TOKEN' in os.environ:
            self.access_token = os.getenv('ACCESS_TOKEN')
            self.headers = {
                'Authorization': 'Bearer '+ self.access_token
            }
        
    def login(self, username,password):

        res = requests.post(self.reverse('login'), data={
            'username': username,
            'password': password,
        })
        access_token = None
        if res.status_code == 200:
           access_token = res.json().get('access_token')
        else:
            return False

        self.headers = {
            'Authorization': 'Bearer '+ access_token
        }
        self.access_token = access_token
        os.environ['ACCESS_TOKEN'] = self.access_token
        self.save_to_env('ACCESS_TOKEN', self.access_token)

        return True

    def reverse(self,endpoint):
        return self.endpoints.get(endpoint)

    def save_to_env(self, variable_name, value):
        with open('.env', 'w') as file:
            file.write(f'{variable_name}={value}\n')

    def is_authenticated(self):
        if self.access_token:
            return True
        return False
    
    def fetch_workspaces(self):
        res = requests.get(self.reverse('get-workspaces'), headers=self.headers)
        return res.json()

    def delete_workspace(self, id):
        res = requests.delete(self.reverse('delete-workspace')+f'/{id}', headers=self.headers)
        return res.status_code == 200

    def delete_workspace_by_name(self, name):
        workspaces = self.fetch_workspaces()
        workspace = next((workspace for workspace in workspaces if workspace['workspace_name'] == name), None)
        if workspace is not None:
            workspace_id = workspace['id']
            self.delete_workspace(workspace_id)

    def create_workspace(self, name):
        res = requests.post(self.reverse('create-workspace'), json={
            "workspace_name": name,
        }, headers=self.headers)
        if res.status_code == 200:
            return res.json()
        
    def create_zeros_poles(self,workspace_id, x, y, has_conj, is_zero):
        res = requests.post(self.reverse('create-zeros-poles')+f'/{workspace_id}/zeros_poles', json={
            'x': x,
            'y': y,
            'has_conj': has_conj,
            'is_zero': is_zero,
        }, headers=self.headers)
        return res.status_code == 200
    


    # def upload_image(self,filename):
    #     self.files = {
    #         'image': open(filename,'rb')
    #     }

    #     res = requests.post(self.reverse('upload-image'), files=self.files, headers=self.headers)


    # def get_grayscale(self):
    #     res = requests.get(self.reverse('get-grayscale'), headers=self.headers)

    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]

    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap
        

    # def add_gaussian_noise(self,mean=1, std=50):
    #     payload = {
    #         'mean': mean,
    #         'std': std,
    #     }
    #     res = requests.get(self.reverse('add-gaussian-noise'),params=payload, headers=self.headers)

    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def add_uniform_noise(self, low = 0, high = 50):
    #     payload = {
    #         'low': low,
    #         'high': high
    #     }
    #     res = requests.get(self.reverse('add-uniform-noise'),params=payload, headers=self.headers)

    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def add_salt_and_pepper_noise(self, saltiness = 0.5, pepperiness = 0.5):
    #     payload = {
    #         'saltiness': saltiness,
    #         'pepperiness': pepperiness
    #     }
    #     res = requests.get(self.reverse('add-salt-and-pepper-noise'),params=payload, headers=self.headers)

    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def blur(self, kernel_size = 3):
    #     payload = {
    #         'kernel': kernel_size,

    #     }
    #     res = requests.get(self.reverse('blur'),params=payload, headers=self.headers)

    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def gaussian_blur(self, kernel_size = 3, std = 1):
    #     payload = {
    #         'kernel': kernel_size,
    #         'std':std,
    #     }
    #     res = requests.get(self.reverse('gaussian-blur'),params=payload, headers=self.headers)

    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def median_blur(self, kernel_size = 3):
    #     payload = {
    #         'kernel': kernel_size,
    #     }
    #     res = requests.get(self.reverse('median-blur'),params=payload, headers=self.headers)

    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def sobel_edge_detection(self):
    #     res = requests.get(self.reverse('sobel-edge-detection'), headers=self.headers)
    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def roberts_edge_detection(self):
    #     res = requests.get(self.reverse('roberts-edge-detection'), headers=self.headers)
    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def prewitt_edge_detection(self):
    #     res = requests.get(self.reverse('prewitt-edge-detection'), headers=self.headers)
    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def canny_edge_detection(self, low_threshold = 50 , high_threshold = 150):
    #     payload = {
    #         'low_threshold': low_threshold,
    #         'high_threshold': high_threshold,
    #     }
    #     res = requests.get(self.reverse('canny-edge-detection'),params=payload, headers=self.headers)
    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def get_histogram(self, channel = 0, image_type = 'gray'):
    #     payload = {
    #         'channel': channel,
    #         'image_type': image_type,
    #     }
    #     res = requests.get(self.reverse('get-histogram'),params=payload, headers=self.headers)
        
    #     histogram = np.frombuffer(res.content, dtype=np.uint8)
        
    #     plt.hist(histogram, bins=256, color='blue')
    #     plt.xlabel('levels')
    #     plt.ylabel('Frequency')
    #     plt.title('Basic Histogram')
    #     buffer = BytesIO()
    #     plt.savefig(buffer, format='png')
    #     buffer.seek(0) 
    #     image_bytes = buffer.getvalue()
    #     qimage = QImage.fromData(image_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     plt.close()
    #     return pixmap
        
        

    # def get_equalized_histogram(self):
        
    #     res = requests.get(self.reverse('get-equalized-histogram'), headers=self.headers)
        
    #     equalized_histogram = np.frombuffer(res.content, dtype=np.uint8)
    #     plt.hist(equalized_histogram, bins=256, color='blue')
    #     plt.xlabel('levels')
    #     plt.ylabel('Frequency')
    #     plt.title('Equalized Histogram')
    #     buffer = BytesIO()
    #     plt.savefig(buffer, format='png')
    #     buffer.seek(0) 
    #     image_bytes = buffer.getvalue()
    #     qimage = QImage.fromData(image_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     plt.close()
    #     return pixmap
    
    # def normalize(self):
    #     res = requests.get(self.reverse('normalize'), headers=self.headers)
    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     image =cv.imdecode(img_bytes, cv.IMREAD_COLOR)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap
    
    # def global_threshold(self, threshold = 50):
    #     payload = {
    #         'threshold': threshold,
    #     }
    #     res = requests.get(self.reverse('global-threshold'),params=payload, headers=self.headers)
    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     image =cv.imdecode(img_bytes, cv.IMREAD_COLOR)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def local_threshold(self, kernel_size = 11):
    #     payload = {
    #         'kernel': kernel_size,
    #     }
    #     res = requests.get(self.reverse('local-threshold'),params=payload, headers=self.headers)
    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def get_equalized_image(self):
        
    #     res = requests.get(self.reverse('get-equalized-image'), headers=self.headers)
    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap

    # def get_hybrid_image(self,filename_1,filename_2,low_pass_cuttoff_freq, high_pass_cuttoff_freq ):
    #     data = {
    #         'low_pass_cuttoff_freq':low_pass_cuttoff_freq,
    #         'high_pass_cuttoff_freq':high_pass_cuttoff_freq
    #     }
    #     files = {
    #         'first_image': open(filename_1,'rb'),
    #         'second_image': open(filename_2,'rb'),
    #     }
    #     res = requests.post(self.reverse('get-hybrid-image'),data=data,files = files, headers=self.headers)
    #     index = res.headers.get('Content-Type').find('/')+1
    #     out_file = 'output.'+res.headers.get('Content-Type')[index:]
    #     img_bytes = np.frombuffer(res.content, dtype=np.uint8)
    #     qimage = QImage.fromData(img_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     return pixmap
    # def get_cdf_distribution(self):
        
    #     res = requests.get(self.reverse('get-cdf-distribution'), headers=self.headers)
        
    #     cdf_distribution = np.frombuffer(res.content, dtype=np.float32)
        
    #     plt.plot(cdf_distribution)
    #     plt.xlabel('levels')
    #     plt.ylabel('cdf')
    #     plt.title('Distribution')
    #     buffer = BytesIO()
    #     plt.savefig(buffer, format='png')
    #     buffer.seek(0) 
    #     image_bytes = buffer.getvalue()
    #     qimage = QImage.fromData(image_bytes)
    #     pixmap = QPixmap.fromImage(qimage)
    #     plt.close()
    #     return pixmap

 