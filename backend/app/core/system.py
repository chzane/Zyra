import os
import time
from config import ZyraConfig
import platform
import getpass
import socket
import psutil
import datetime


class ZyraSystemInfo:
    def __init__(self):
        self.name: str = ZyraConfig.APP_NAME
        self.version: str = ZyraConfig.VERSION
        self.env: str = os.getenv("APP_ENV", "development")
        self.start_time: float = time.time()

        self.timezone: datetime.timezonezinfo = datetime.datetime.now().astimezone().tzinfo
        try:
            self.hostname: str | None = socket.gethostname()
        except:
            self.hostname = None
            
        try:
            self.cpu_model: str | None = platform.processor()
        except:
            self.cpu_model = None
            
        try:
            mem = psutil.virtual_memory()
            self.memory_gb: float | None = round(mem.total / (1024**3), 2)
        except:
            self.memory_gb = None
            
        try:
            disk = psutil.disk_usage('/')
            self.storage_gb: float | None = round(disk.total / (1024**3), 2)
        except:
            self.storage_gb = None
            
        try:
            self.username: str | None = getpass.getuser()
        except:
            self.username = None
            
        try:
            self.cpu_name: str | None = platform.processor() or platform.machine()
        except:
            self.cpu_name = None
            
        try:
            self.os: str | None = platform.system()
        except:
            self.os = None
            
        try:
            self.arch: str | None = platform.machine()
        except:
            self.arch = None

    @property
    def uptime(self):
        """
        Get system uptime

        :return: Uptime in seconds
        """
        return time.time() - self.start_time

    def to_dict(self):
        """
        Convert system info to dictionary

        :return: System info dictionary
        """
        return {
            "zyra": {
                "name": self.name,
                "version": self.version,
                "env": self.env,
                "uptime": self.uptime,
            },
            "system": {
                "os": self.os,
                "arch": self.arch,
                "timezone": str(self.timezone),
                "cpu_model": self.cpu_model,
                "cpu_name": self.cpu_name,
                "memory_gb": self.memory_gb,
                "storage_gb": self.storage_gb,
                "username": self.username,
                "hostname": self.hostname,
            },
        }


zyra_system_info = ZyraSystemInfo()
