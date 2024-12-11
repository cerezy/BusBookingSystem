from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Request
from pydantic import BaseModel
import time
import datetime
import json
import uvicorn
import pymysql
db = pymysql.connect(host='localhost', user='root', password='123456', database='busbookingsystem')
cursor = db.cursor()

Now_Username = "Now_Username"
Now_Password = "Now_Password"
Now_Email = "Now_Email"
Now_Type = "Now_Type"
Now_ID = 0



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)


@app.get("/", include_in_schema=False)
async def redirect_to_login():
    return RedirectResponse(url="/static/login.html")


# 创建数据模型
class Login(BaseModel):
    username: str
    password: str

# 创建一个 POST 路由
@app.post("/login")
async def login(login: Login):
    global Now_Username
    global Now_Password
    global Now_Email
    global Now_Type
    global Now_ID
    # 这里可以添加处理 item 的逻辑
    # 例如，保存到数据库等
    username = login.username
    password = login.password
    print("username: " + username + " password: " + password)
    cursor.execute("SELECT * FROM users")
    # 获取查询结果
    results = cursor.fetchall()
    can_login = 0
    first_not = False
    for row in results:
        print(row[2]+" "+row[4])
        if username == row[2] and password == row[4]:

            Now_Username = row[2]
            Now_Password = row[4]
            Now_Email = row[3]
            Now_Type = row[1]
            Now_ID = row[0]
            first_not = row[5]
            can_login = 1
            break
    if can_login == 1:
        sql = f"UPDATE users SET is_first_login = FALSE WHERE userId = '{Now_ID}'"
        cursor.execute(sql)
        db.commit()
        return {'status': 'success', 'userType': 'f"{Now_Type}"', 'init': 'f"{first_not}"'}
    if username == 'admin':
        return {'status': 'success'}
    return {'status': 'fail'}

class Query(BaseModel):
    date: str
    userType: str

Bus_id = []
Bus_time = []
Bus_origin = []
Bus_destination = []
Bus_busType = []
Bus_seats = []
Bus_plate = []


def makeUpdate():
    #找到订单是已预约的
    sql_update_1 = f"SELECT buses.busId,buses.date,buses.time,bookings.bookingId,bookings.created_at " \
                   f"from bookings JOIN buses ON " \
                   f"bookings.busId = buses.busId AND bookings.status = '已预约' AND userId = '{Now_ID}'"
    cursor.execute(sql_update_1)
    results = cursor.fetchall()
    for row in results:
        date_as_datetime = datetime.datetime.combine(row[1], datetime.time.min)
        new_datetime_obj = date_as_datetime + row[2]
        # print(new_datetime_obj)
        #如果应该已完成则更新
        if new_datetime_obj < row[4]:
            sql_update_2 = f"UPDATE bookings SET status = '已完成' WHERE bookingId = {row[3]}"
            cursor.execute(sql_update_2)
            db.commit()


@app.post("/queryAll")
async def queryAll(query: Query):
    d = query.date
    global Bus_id,Bus_time,Bus_origin,Bus_destination,Bus_busType,Bus_seats,Bus_plate
    Bus_id.clear()
    Bus_time.clear()
    Bus_origin.clear()
    Bus_destination.clear()
    Bus_busType.clear()
    Bus_seats.clear()
    Bus_plate.clear()
    sql = f"SELECT * FROM buses WHERE busId NOT IN" \
          f"(SELECT busId FROM bookings WHERE userId = '{Now_ID}' AND (status = '已预约' OR status = '已完成'))"
    cursor.execute(sql)
    # 获取查询结果
    counter = 0
    results = cursor.fetchall()
    #寻找满足日期和未预约的条件的车次
    for row in results:
        date_format = "%Y-%m-%d"
        date_string = row[4].strftime(date_format)
        if date_string == d:
            counter = counter + 1
            Bus_id.append(row[0])
            Bus_time.append(row[5])
            Bus_origin.append(row[1])
            Bus_destination.append(row[2])
            Bus_busType.append(row[3])
            Bus_seats.append(row[8])
            Bus_plate.append(row[6])
    all_info = []
    # userType = query.userType
    userType = Now_Type
    # print(userType)
    for i in range(counter):
        hours, remainder = divmod(Bus_time[i].total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        new_one = {"busId": Bus_id[i],
                 "origin": Bus_origin[i],
                "destination": Bus_destination[i],
                "time": time_str,
                "busType": Bus_busType[i],
                "seats": Bus_seats[i],
                 "plate": Bus_plate[i]
                }
        if userType == "学生" and Bus_busType[i] != "师生车":
            continue
        all_info.append(new_one)

    return all_info

class User(BaseModel):
    userId: str

@app.post("/queryBooked")
async def queryBooked(user: User):
    id = user.userId
    print(id)
    makeUpdate()
    cursor.execute("SELECT buses.busId,buses.origin,buses.destination,buses.time,"
                   "buses.busType,buses.plate,bookings.userId "
                   " FROM buses JOIN bookings ON buses.busId = bookings.busId  "
                   "WHERE status = '已预约' AND userId = " + str(Now_ID))
    # 获取查询结果
    all_booked = []
    counter = 0
    results = cursor.fetchall()
    for row in results:
        hours, remainder = divmod(row[3].total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        # 使用格式化字符串将结果组合成所需格式
        time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        new_one = {"busId": row[0],
                   "origin": row[1],
                   "destination": row[2],
                   "time": time_str,
                   "busType": row[4],
                   "plate": row[5]
                   }
        all_booked.append(new_one)
    return all_booked

@app.post("/queryFinished")
async def queryFinished(user: User):
    id = user.userId
    # print(id)
    makeUpdate()
    cursor.execute("SELECT buses.busId,buses.origin,buses.destination,buses.date,buses.time,"
                   "buses.busType,buses.plate,bookings.userId,bookings.status"
                   " FROM buses JOIN bookings ON buses.busId = bookings.busId  "
                   "WHERE (status = '已取消' OR status = '已完成') AND userId = " + str(Now_ID) +
                   " ORDER BY buses.date DESC,buses.time DESC")
    # 获取查询结果
    all_finished = []
    results = cursor.fetchall()
    for row in results:
        print(row)
        hours, remainder = divmod(row[4].total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        # 使用格式化字符串将结果组合成所需格式
        time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        if row[8] == "已取消":
            new_one = {"status": "unbooked",
                       "busId": row[0],
                       "origin": row[1],
                       "destination": row[2],
                       "time": time_str,
                       "busType": row[5],
                       "plate": row[6],
                       "date":row[3]
                       }
            all_finished.append(new_one)
        elif row[8] == "已完成":
            new_one = {"status": "finished",
                       "busId": row[0],
                       "origin": row[1],
                       "destination": row[2],
                       "time": time_str,
                       "busType": row[5],
                       "plate": row[6],
                       "date": row[3]
                       }
            all_finished.append(new_one)
    print(all_finished)
    return all_finished

@app.post("/queryUser")
async def queryUser(user: User):
    user.userId = Now_ID
    return {'status': 'success',
            "userType": Now_Type,
            "username": Now_Username,
            "email": Now_Email}

class UserInfo(BaseModel):
    userId: str
    userType: str
    username: str
    email: str

@app.post("/submitUser")
async def submitUser(user: UserInfo):
    #userId = user.userId
    userId = Now_ID
    username = user.username
    email = user.email
    sql = f"UPDATE users SET username = '{username}' , email = '{email}' WHERE userId = '{userId}'"
    cursor.execute(sql)
    # 提交更改到数据库
    db.commit()
    return {"status": "success"}

class Password(BaseModel):
    originPassword: str
    newPassword: str

@app.post("/changePassword")
async def change_password(p: Password):
    originPassword = p.originPassword
    newPassword = p.newPassword
    userId = Now_ID
    if (originPassword != Now_Password):
        return {"status": "passwordWrong"}
    sql = f"UPDATE users SET password = '{newPassword}' WHERE userId = '{userId}' AND password = '{originPassword}'"
    cursor.execute(sql)
    db.commit()
    return {"status": "success"}


class Book(BaseModel):
    userId: str
    busId: str

@app.post("/book")
async def book(book: Book):
    userid = book.userId
    busid = book.busId
    print(userid,busid)
    sql = f"SELECT * from buses WHERE busId = {busid}"
    cursor.execute(sql)
    results = cursor.fetchall()
    reseat = results[0][8]
    if reseat:
        return {"status": "available"}

@app.post("/payed")
async def payed(book: Book):
    # userid = book.userId
    userid = Now_ID
    busid = book.busId
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    sql_1 = f"UPDATE buses SET available_seats = available_seats-1 WHERE busId = {busid}"
    cursor.execute(sql_1)
    sql_2 = f"INSERT INTO bookings (userId, busId, status, created_at) VALUES('{userid}', {busid}, '已预约', '{now_time}')"
    cursor.execute(sql_2)
    db.commit()
    return {"status": "success"}


@app.post("/unbook")
async def unbook(book: Book):
    # userid = book.userId
    userid = Now_ID
    busid = book.busId
    sql_1 = f"UPDATE buses SET available_seats = available_seats + 1 WHERE busId = {busid}"
    cursor.execute(sql_1)
    sql_2 = f"UPDATE bookings SET status = '已取消' where busId = {busid} AND userId = '{userid}' AND status = '已预约'"
    cursor.execute(sql_2)
    db.commit()
    return {"status": "success"}

@app.post("/initPassword")
async def init_password(user: User):
    return {'status': 'success'}

class Bus(BaseModel):
    origin: str
    destination: str
    busType: str
    date: str
    time: str
    plate: str
    seats: str

@app.post("/addBus")
async def addBus(bus: Bus):
    new_origin = bus.origin
    new_destination = bus.destination
    new_busType = bus.busType
    new_date = bus.date
    new_time = bus.time
    new_plate = bus.plate
    new_seats = bus.seats
    # 执行插入语句
    sql = f"INSERT INTO buses (origin, destination, busType, date, time, plate, total_seats, available_seats) " \
          f"VALUES ('{new_origin}','{new_destination}','{new_busType}','{new_date}'," \
          f"'{new_time}','{new_plate}','{new_seats}','{new_seats}')"
    print(sql)
    cursor.execute(sql)
    # # 提交事务
    db.commit()
    return {'status': 'success'}

class BusId(BaseModel):
    busId: str

@app.post("/deleteBus")
async def deleteBus(busId: BusId):
    # 执行插入语句
    id_to_delete = 10
    sql_1 = f"SELECT * from buses WHERE busId = {id_to_delete}"
    sql_2 = f"DELETE FROM buses WHERE busId = {id_to_delete}"
    cursor.execute(sql_1)
    results = cursor.fetchall()
    if results:
        cursor.execute(sql_2)
        # 提交事务
        db.commit()
    return {'status': 'success'}


# 运行应用
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
    # Now_ID = 123
    # sql_update_2 = f"UPDATE bookings SET status = '已预约' WHERE bookingId = 8"
    # cursor.execute(sql_update_2)
    # db.commit()

