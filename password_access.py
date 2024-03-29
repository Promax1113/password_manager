import base64
import hashlib
import pathlib
import os
from fernet import Fernet

import password_processing

userpath = pathlib.Path(__name__).parent.resolve()


def gen_fernet_key(passcode: bytes) -> bytes:
    assert isinstance(passcode, bytes)
    hlib = hashlib.md5()
    hlib.update(passcode)
    return base64.urlsafe_b64encode(hlib.hexdigest().encode('latin-1'))


def save_password(_name, _webpage, _username, _password):
    password = password_processing.Password()
    setattr(password, "webpage", _webpage)
    setattr(password, "password_loc", f"{userpath}/passwords/{_name}.passfile")
    setattr(password, "username", _username)
    setattr(password, "password", _password)

    f = Fernet(gen_fernet_key(password_processing.user_details.encode("utf-8")))
    with open(getattr(password, "password_loc"), "+ab") as file:
        file.write(f.encrypt(bytes(_username, 'utf-8')))
        file.write(b"\n")
        file.write(f.encrypt(bytes(_password, 'utf-8')))
        file.close()
    with open(f"{userpath}/passwords/{_name}.data", "wb") as file:
        file.write(f.encrypt(bytes(_webpage, 'utf-8')))

    password_processing.passwords.append(password)


def read_password(_name):

    if not os.path.isfile(f"{userpath}/passwords/{_name}.passfile"):
        return "File not found!"

    fernet_k = Fernet(gen_fernet_key(password_processing.user_details.encode("utf-8")))

    with open(f"{userpath}/passwords/{_name}.data", "r") as f:
        website = f.readline()
        f.close()

    with open(f"{userpath}/passwords/{_name}.passfile", "r") as file:
        data = file.readlines()
        file.close()
    try:
        webpage = (fernet_k.decrypt(website.encode())).decode()
        username = (fernet_k.decrypt(data[0].strip("\n").encode())).decode()
        password = (fernet_k.decrypt(data[1].encode())).decode()
    except:
        return "Invalid Login! You did not login!"


    return {
        "name": _name,
        "website": webpage,
        "username": username,
        "password": password
    }
