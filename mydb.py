import mysql.connector

dataBase=mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='3171996',

)

cursorObject = dataBase.cursor()

#Create DB

cursorObject.execute("CREATE DATABASE budgexdb")

print("ALL DONE!")