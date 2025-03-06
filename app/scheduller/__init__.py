
import sys
from scheduller.scheduller import  send_message, shutdown, startup, check_payment_after_reg

from arq.connections import RedisSettings

class WorkerSettings:
    functions = [send_message, check_payment_after_reg]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings()