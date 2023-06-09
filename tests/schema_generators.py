from backend.api.schemas import User
from backend.api.schemas.device import Device, DeviceCreate
from backend.api.schemas.heartbeat import (DeviceHeartbeatCreate,
                                           DeviceTemperature)


def gen_device_create(user: User) -> DeviceCreate:
    return DeviceCreate(
        name="Numero Uno",
        ssh_port=22,
        dyn_dns_address="adlerhorst@ddns.net",
        user=user.id,
    )


def gen_device_heartbeat_create() -> DeviceHeartbeatCreate:
    return DeviceHeartbeatCreate(
        temperature=DeviceTemperature(
            temp_cpu=[42, 45, 44, 49], temp_gpu=[60], temp_hard_drive=[70]
        ),
        ram_usage=0.7,
        swap_usage=0.02,
        disk_usage=0.42,
        num_ssh_connections=2,
        created_at_device="2023-04-08T19:05:41.395Z",
        uptime="2023-03-12T12:23:41.395Z",
    )
