import os.path
from shutil import copy
import sqlite3
import sys

import win32crypt


def getLoginData():
    # Fetch the cookie DB and copy to local folder.
    # This helps avoid access issues due to DB locking while Chrome is open.
    userhome = os.path.expanduser('~')
    destination = os.path.dirname(os.path.realpath(__file__))

    filePath = os.path.normpath(os.path.join(
                    userhome, 'AppData\\Local\\Google\\Chrome'
                    '\\User Data\\Default\\Login Data'))

    copy(filePath, destination)


getLoginData()


# Connect to the Database
try:
    conn = sqlite3.connect('Login Data')
    cursor = conn.cursor()
except Exception as e:
    print("Unable to connect to Database.")
    print("{0}".format(e))
    sys.exit(1)

# Fetch contents of Login Data
try:
    cursor.execute('''
        SELECT action_url,
        username_value,
        password_value
        FROM logins''')
except Exception as e:
    print("{0}".format(e))
    sys.exit(1)

data = cursor.fetchall()

# Open export.txt to begin file write of output.
with open('export.txt', 'w') as f:

    # Decrypt contents of Login Data file.
    if len(data) > 0:
        for result in data:
            # Decrypt the Password
            try:
                password = win32crypt.CryptUnprotectData(
                    result[2],
                    None,
                    None,
                    None,
                    0)[1].decode("utf-8")
            except Exception as e:
                print("{0}".format(e))
                pass
            if password:
                f.write(
                    "URL: {0} :: ".format(result[0]) +
                    "Username: {0} :: ".format(result[1]) +
                    "Password: {0}\n".format(password))
    else:
        f.write("No results returned from query")
        print("No results returned from query")
        sys.exit(0)
