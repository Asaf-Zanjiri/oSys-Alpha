import datetime

# Consts
BUFFER_SIZE = 1024
POWER_MODULE_COOLDOWN = 5

# Server Variables
all_connections = []
custom_console = 'oSys> '

# Power Module Variables - Cooldowns
latest_restart_time = datetime.datetime(2000, 12, 1, 1, 1)
latest_shutdown_time = datetime.datetime(2000, 12, 1, 1, 1)
