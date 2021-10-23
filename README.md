# oSys-Alpha
This program yearns to be my first attempt at making a windows RAT with python.
It's not my any means perfect, However it mostly works without a problem.

**Important Note:**

This application was developed as an educational exercise. It doesn't and shouldn't be used for any malicious intent.
The code does not come with UAC bypass, Nor Persistence, Nor does it try to bypass any anti-virus detection.


**Features**

- Ability to Power-Off/Restart The client's machine.
- Ability to upload and auto-run EXE files to the client's machine.
- Ability to take a screenshot of the client's machine 1st monitor. (30-sec cooldown)
- Ability to silently enable RDP on the client's machine and create a reverse tunnel to connect to the RDP.
- Automatic communication compression between the client and server.
- Interactive GUI to use all of the features and manage the clients.
- Automatically shows new client connected to the server. And Automatically removes disconnected clients.
- Logs actions to a log file.


**Compilation method:**

Obfuscate and pack using PyArmor.
1. `pip install PyInstaller`
2.  `pyarmor pack --clean -e "--onefile " client.py` / `pyarmor pack --clean -e "--onefile --noconsole " server.py`

**Usage Guidelines:**

- Forward port 8000 TCP (For the server hosting)
- Forward port 22 TCP (For the SSH server)
- Connection to HRDP is through mstsc.exe. The connection IP address is: 127.0.0.1:6969 | Username=hidden | Password=hidden
- Default host IP can be changed using the startup arg "-i=0.0.0.0" or "--ip=0.0.0.0" ("0.0.0.0" being your desired ip address)
- Default host port can be changed using the startup arg "-p=1337" or "--port=1337" ("1337" being your desired port number)
- If you suspect you may have encountered an error please look at the log file for a possible explanation.
