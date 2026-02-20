import socket

def getIp():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        localIp = s.getsockname()[0]
        s.close()
        return localIp
    except socket.error as e:
        print(f"Error getting IP address : {e}")
        return None