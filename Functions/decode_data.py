import base64

def decode_data(data):
    decoded_data = []
    for item in data:
        decoded_item = {}
        for key, value in item.items():
            if isinstance(value, str):
                try:
                    decoded_value = base64.b64decode(value).decode('utf-8')
                except (base64.binascii.Error, UnicodeDecodeError):
                    decoded_value = value
                decoded_item[key] = decoded_value
            else:
                decoded_item[key] = value
        decoded_data.append(decoded_item)
    return decoded_data
