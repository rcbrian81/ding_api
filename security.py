from settings import SECURITY_KEY


def validate_security_key(received_key):
    if received_key != SECURITY_KEY:
        return "0_sec_9999"  
    return "1"  