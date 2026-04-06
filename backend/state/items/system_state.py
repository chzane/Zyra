from __future__ import annotations

import datetime
import getpass
import platform
import socket
import locale

import psutil
from pydantic import Field

from config.base_config import ZyraBaseState


def safe_call(func, default=None):
    try:
        return func()
    except Exception:
        return default


class SystemState(ZyraBaseState):
    timezone: str | None = Field(
        default_factory=lambda: safe_call(
            lambda: str(datetime.datetime.now().astimezone().tzinfo)
        )
    )

    hostname: str | None = Field(
        default_factory=lambda: safe_call(socket.gethostname)
    )

    username: str | None = Field(
        default_factory=lambda: safe_call(getpass.getuser)
    )

    userlanguage: str | None = Field(
        default_factory=lambda: safe_call(
            lambda: locale.getlocale()[0]
        )
    )

    os_name: str | None = Field(
        default_factory=lambda: safe_call(platform.system)
    )

    os_version: str | None = Field(
        default_factory=lambda: safe_call(platform.version)
    )

    platform_name: str | None = Field(
        default_factory=lambda: safe_call(platform.platform)
    )

    arch: str | None = Field(
        default_factory=lambda: safe_call(platform.machine)
    )

    cpu_name: str | None = Field(
        default_factory=lambda: safe_call(
            lambda: platform.processor() or platform.machine()
        )
    )

    cpu_count_logical: int | None = Field(
        default_factory=lambda: safe_call(psutil.cpu_count)
    )

    cpu_count_physical: int | None = Field(
        default_factory=lambda: safe_call(
            lambda: psutil.cpu_count(logical=False)
        )
    )

    memory_gb: float | None = Field(
        default_factory=lambda: safe_call(
            lambda: round(psutil.virtual_memory().total / (1024 ** 3), 2)
        )
    )

    available_memory_gb: float | None = Field(
        default_factory=lambda: safe_call(
            lambda: round(psutil.virtual_memory().available / (1024 ** 3), 2)
        )
    )

    storage_gb: float | None = Field(
        default_factory=lambda: safe_call(
            lambda: round(psutil.disk_usage("/").total / (1024 ** 3), 2)
        ),
        exclude=True
    )

    free_storage_gb: float | None = Field(
        default_factory=lambda: safe_call(
            lambda: round(psutil.disk_usage("/").free / (1024 ** 3), 2)
        ),
        exclude=True
    )

    boot_time: datetime.datetime | None = Field(
        default_factory=lambda: safe_call(
            lambda: datetime.datetime.fromtimestamp(psutil.boot_time())
        ),
        exclude=True
    )

    def refresh(self):
        self.timezone = safe_call(
            lambda: str(datetime.datetime.now().astimezone().tzinfo)
        )
        self.hostname = safe_call(socket.gethostname)
        self.username = safe_call(getpass.getuser)
        self.userlanguage = safe_call(
            lambda: locale.getlocale()[0]
        )
        self.os_name = safe_call(platform.system)
        self.os_version = safe_call(platform.version)
        self.platform_name = safe_call(platform.platform)
        self.arch = safe_call(platform.machine)
        self.cpu_name = safe_call(
            lambda: platform.processor() or platform.machine()
        )
        self.cpu_count_logical = safe_call(psutil.cpu_count)
        self.cpu_count_physical = safe_call(
            lambda: psutil.cpu_count(logical=False)
        )
        self.memory_gb = safe_call(
            lambda: round(psutil.virtual_memory().total / (1024 ** 3), 2)
        )
        self.available_memory_gb = safe_call(
            lambda: round(psutil.virtual_memory().available / (1024 ** 3), 2)
        )
        self.storage_gb = safe_call(
            lambda: round(psutil.disk_usage("/").total / (1024 ** 3), 2)
        )
        self.free_storage_gb = safe_call(
            lambda: round(psutil.disk_usage("/").free / (1024 ** 3), 2)
        )
        self.boot_time = safe_call(
            lambda: datetime.datetime.fromtimestamp(psutil.boot_time())
        )
