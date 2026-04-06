import time
from config.config_manager import get_config
from state.state_manager import get_state


class ZyraSystemInfo:
    def __init__(self):
        self.config = get_config()
        self.state = get_state()
        self.name: str = self.config.app.name
        self.version: str = self.config.app.version
        self.start_time: float = time.time()

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
        self.state.system.refresh()

        return {
            "zyra": {
                "name": self.name,
                "version": self.version,
                "uptime": self.uptime,
            },
            "system": {
                "os_name": self.state.system.os_name,
                "arch": self.state.system.arch,
                "timezone": str(self.state.system.timezone),
                "cpu_name": self.state.system.cpu_name,
                "memory_gb": self.state.system.memory_gb,
                "storage_gb": self.state.system.storage_gb,
                "username": self.state.system.username,
                "hostname": self.state.system.hostname,
                "userlanguage": self.state.system.userlanguage,
            },
        }
