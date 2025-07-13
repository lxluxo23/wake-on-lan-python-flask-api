import platform
import subprocess

def obtenerPorMac(mac_address):
    mac_address = formatearMac(mac_address)
    try:
        result = subprocess.check_output(['arp', '-a'], shell=True, text=True)
        for line in result.split('\n'):
            if mac_address in line:
                parts = line.split()
                ip_address = parts[0]
                return ip_address
    except subprocess.CalledProcessError:
        return None
    
def formatearMac(mac):
    mac_formateada = mac.replace(':', '-')
    return mac_formateada.lower()

def ping(host):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', host]
    return subprocess.call(command) == 0