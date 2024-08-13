import os
import re
import sys
from time import sleep

class DataParser:
    def __init__(self):
        self.data_points = {'cpu_temp': [], 'cpu_usage': [], 'gpu_temp': [], 'gpu_usage': []}
        self.cpu_extra_info = {}
        self.gpu_extra_info = {}
        self.gpu_name = "Loading..."
        self.cpu_name = "Loading..."

    def resourcePath(self, relativePath):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            basePath = sys._MEIPASS
        except Exception:
            basePath = os.path.abspath(".")

        return os.path.join(basePath, relativePath)
    
    def parse_data(self):
        while True:
            file_path = 'data.txt'

            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write('')

            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                self._parse_extra_info(lines)

                for line in lines:
                    if 'CPU Temperature:' in line:
                        temp = float(re.search(r'CPU Temperature: (\d+)', line).group(1))
                        self.data_points['cpu_temp'].append(temp)
                    elif 'CPU Name:' in line:
                        self.cpu_name = re.search(r'CPU Name: (.+)', line).group(1).strip()
                    elif 'GPU Name:' in line:
                        self.gpu_name = re.search(r'GPU Name: (.+)', line).group(1).strip()
                    elif 'CPU Usage:' in line:
                        usage = float(re.search(r'CPU Usage: (\d+)', line).group(1))
                        self.data_points['cpu_usage'].append(usage)
                    elif 'GPU Temperature:' in line:
                        temp = float(re.search(r'GPU Temperature: (\d+)', line).group(1))
                        self.data_points['gpu_temp'].append(temp)
                    elif 'GPU Usage:' in line:
                        usage = float(re.search(r'GPU Usage: (\d+)', line).group(1))
                        self.data_points['gpu_usage'].append(usage)
                sleep(1)
    
    def _parse_extra_info(self, lines):
        substrings = ["Name", "Usage", "Temperature"]
        for line in lines:
            if line.startswith('CPU'):
                if all(substring not in line for substring in substrings):
                    key, value = line.split(': ', 1)
                    key = key.strip()
                    value = value.strip()
                    self.cpu_extra_info[key] = value
            elif line.startswith('GPU') or line.startswith('D3D'):
                if all(substring not in line for substring in substrings):
                    key, value = line.split(': ', 1)
                    key = key.strip()
                    value = value.strip()
                    self.gpu_extra_info[key] = value
    
    def get_latest_data(self):
        return self.data_points
    
    def get_cpu_name(self):
        return self.cpu_name

    def get_gpu_name(self):
        return self.gpu_name
    
    def get_cpu_extra_info(self):
        return self.cpu_extra_info

    def get_gpu_extra_info(self):
        return self.gpu_extra_info
