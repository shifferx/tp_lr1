import psutil
import json
from pathlib import Path
import platform
import socket
import datetime


def neadekvatnie_bytes_v_chelovecheskie(n):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if abs(n) < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return "too much"


def system_info():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    now = datetime.datetime.now()

    info = {
        "hostname": socket.gethostname(),
        "fqdn": socket.getfqdn(),
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            },
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            },
        "boot_time": boot_time.isoformat(timespec="seconds"),
        "uptime_seconds": round((now - boot_time).total_seconds(), 1),
        "users": [
            {
                "name": u.name,
                "terminal": u.terminal,
                "host": u.host,
                "started": datetime.datetime.fromtimestamp(u.started).isoformat(timespec="seconds"),
                }
            for u in psutil.users()
            ]
        }
    return info


def chip_info():
    freq = psutil.cpu_freq()
    info = {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "frequency_mhz": {
            "current": freq.current if freq else None,
            "min": freq.min if freq else None,
            "max": freq.max if freq else None,
            },
        "usage_percent": psutil.cpu_percent(interval=1),
        "usage_per_core_percent": psutil.cpu_percent(interval=1, percpu=True),
        }
    return info

def memory_info():
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()

    info = {
        "virtual": {
            "total": vm.total,
            "total_human": neadekvatnie_bytes_v_chelovecheskie(vm.total),
            "available": vm.available,
            "available_human": neadekvatnie_bytes_v_chelovecheskie(vm.available),
            "used": vm.used,
            "used_human": neadekvatnie_bytes_v_chelovecheskie(vm.used),
            "free": vm.free,
            "free_human": neadekvatnie_bytes_v_chelovecheskie(vm.free),
            "percent": vm.percent,
        },
        "swap": {
            "total": swap.total,
            "total_human": neadekvatnie_bytes_v_chelovecheskie(swap.total),
            "used": swap.used,
            "used_human": neadekvatnie_bytes_v_chelovecheskie(swap.used),
            "free": swap.free,
            "free_human": neadekvatnie_bytes_v_chelovecheskie(swap.free),
            "percent": swap.percent,
        },
    }
    return info


def disk_info():
    partitions = {}

    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
    
        partitions[part.device] = {
            "mountpoint": part.mountpoint,
            "fstype": part.fstype,
            "opts": part.opts,
            "total": usage.total,
            "total_human": neadekvatnie_bytes_v_chelovecheskie(usage.total),
            "used": usage.used,
            "used_human": neadekvatnie_bytes_v_chelovecheskie(usage.used),
            "free": usage.free,
            "free_human": neadekvatnie_bytes_v_chelovecheskie(usage.free),
            "percent": usage.percent,
            }
    return {"partitions": partitions}

def all_info_collect():
    data = {
        "system": system_info(),
        "cpu": chip_info(),
        "memory": memory_info(),
        "disk": disk_info(),
        }
    return data

def save_to_json(data, filename="system_info.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Данные сохранены в {Path(filename).resolve()}")


if __name__ == "__main__":
    info = all_info_collect()
    save_to_json(info)