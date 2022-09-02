import requests

UPLOAD_URL = ""  # put your url here
PATH_TO_BLOB = ""  # put your path to blob here

with open(PATH_TO_BLOB, "rb") as f:
    object_text = f.read()
    r = requests.put(
        url=UPLOAD_URL,
        data=object_text)

print(r.status_code)
