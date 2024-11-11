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
async def create_item(login: Login):
    import json
    # 这里可以添加处理 item 的逻辑
    # 例如，保存到数据库等
    username = login.username
    password = login.password
    print("username: " + username + " password: " + password)
    return {'status': 'success'}

# 运行应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)