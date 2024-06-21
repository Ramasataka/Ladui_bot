import mysql.connector

def db_check_running():
    try:
        con = mysql.connector.connect(
            host='localhost',
            user='root',
            database='discord_bot',
            password=''
        )
        con.close()
        return True
    except mysql.connector.Error as e:
        return False

    

