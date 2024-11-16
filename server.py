from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 设置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

from fastapi import FastAPI, Request
from pydantic import BaseModel

# 创建数据模型
class Login(BaseModel):
    username: str
    password: str

# 创建一个 POST 路由
@app.post("/login")
async def login(login: Login):
    import json
    # 这里可以添加处理 item 的逻辑
    # 例如，保存到数据库等
    username = login.username
    password = login.password
    print("username: " + username + " password: " + password)
    if username == '123' and password == '123':
        return {'status': 'success', 'userType': '学生', 'init': '1'}
    if username == 'admin':
        return {'status': 'success'}
    return {'status': 'fail'}

class Query(BaseModel):
    date: str
    userType: str

@app.post("/queryAll")
async def queryAll(query: Query):
    d = query.date
    userType = query.userType
    # 模拟查询数据库
    if (d == '2024-11-18'):
        return []
    if (d == '2024-11-17'):
        return [{"busId": "1",
                 "origin": "清水河",
                "destination": "沙河",
                "time": "16:10",
                "busType": "师生车",
                "seats": "24",
                 "plate": "川A66666"
                },
                {"busId": "2",
                 "origin": "沙河",
                "destination": "清水河",
                "time": "17:10",
                "busType": "教职工车",
                "seats": "13",
                 "plate": "川A66666"
                }]
    return [{"busId": "3",
             "origin": "清水河",
             "destination": "沙河",
             "time": "16:10",
             "busType": "师生车",
             "seats": "8",
             "plate": "川A66666"
             }]

class User(BaseModel):
    userId: str

@app.post("/queryBooked")
async def queryBooked(user: User):
    id = user.userId
    print(id)
    # return []
    return [{"busId": "1",
             "origin": "清水河",
             "destination": "沙河",
             "time": "16:10",
             "busType": "师生车",
             "plate": "川A66666"
             },
            {"busId": "2",
             "origin": "沙河",
            "destination": "清水河",
             "time": "17:20",
             "busType": "教职工车",
             "plate": "川A12345"
             }]

@app.post("/queryFinished")
async def queryFinished(user: User):
    id = user.userId
    return [{"status": "finished",
            "busId": "1",
            "origin": "清水河",
            "destination": "沙河",
            "time": "16:10",
            "busType": "师生车",
            "plate": "川A66666",
            "date": "2024-11-11"
            },
            {"status": "unbooked",
            "busId": "2",
            "origin": "沙河",
            "destination": "清水河",
            "time": "17:10",
            "busType": "教职工车",
            "plate": "川A12345",
            "date": "2024-11-10"
            }]

@app.post("/queryUser")
async def queryUser(user: User):
    id = user.userId
    return {'status': 'success',
            "userType": "学生",
            "username": "张三",
            "email": "123@qq.com"}

class UserInfo(BaseModel):
    userId: str
    userType: str
    username: str
    email: str

@app.post("/submitUser")
async def submitUser(user: UserInfo):
    userId = user.userId
    username = user.username
    email = user.email
    return {"status": "success"}

class Password(BaseModel):
    originPassword: str
    newPassword: str

@app.post("/changePassword")
async def change_password(p: Password):
    originPassword = p.originPassword
    newPassword = p.newPassword
    if (originPassword != '123'):
        return {"status": "passwordWrong"}
    return {"status": "success"}


class Book(BaseModel):
    userId: str
    busId: str

@app.post("/book")
async def book(book: Book):
    userid = book.userId
    busid = book.busId
    if (busid == '3'):
        return {"status": "booked"}
    return {"status": "available"}

@app.post("/payed")
async def payed(book: Book):
    userid = book.userId
    busid = book.busId
    if (busid == '3'):
        return {"status": "booked"}
    return {"status": "success"}


@app.post("/unbook")
async def unbook(book: Book):
    userid = book.userId
    busid = book.busId
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
    return {'status': 'success'}

class BusId(BaseModel):
    busId: str

@app.post("/deleteBus")
async def deleteBus(busId: BusId):
    return {'status': 'success'}

# 运行应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)