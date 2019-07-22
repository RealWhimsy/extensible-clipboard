from requests import get

@staticmethod
def get_public_ipv4():
    ip = get('https://api.ipify.org').text
    print  ('My public IP address is:', ip)