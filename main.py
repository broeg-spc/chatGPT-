from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # 导入 Pydantic 的 BaseModel
from typing import Dict, Any
from decouple import config
import mysql.connector
import openai
import requests

app = FastAPI()
# 连接数据库
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="MyDB_one"
)

# # 获取数据库中所有的表名及数据 终端中展示 已弃用
# cursor.execute("SHOW TABLES")
# tables = cursor.fetchall()
# for table in tables:#打印在终端查看 已弃用
#     table_name = table[0]
#     print(f"Table: {table_name}")
#
#     # 获取表结构
#     cursor.execute(f"DESCRIBE {table_name}")
#     columns = cursor.fetchall()
#     print("Columns:")
#     for column in columns:
#         print(column[0])
#
#     # 获取表数据
#     cursor.execute(f"SELECT * FROM {table_name}")
#     rows = cursor.fetchall()
#     print("Data:")
#     for row in rows:
#         print(row)
#
#     print()

# 定义 OpenAI API 的 URL 和密钥
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = config('API_KEY')


# 向chatGPT发送请求
@app.post("/api/chat")
async def chat(message: Dict[str, Any]):
    try:
        user_message = message.get("msg")

        # 构建请求数据
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": user_message}]
        }

        # 添加 OpenAI API 密钥到请求头
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        # 转发请求到 OpenAI API
        response = requests.post(OPENAI_API_URL, headers=headers, json=request_data)
        response_data = response.json()

        chatgpt_response = response_data["choices"][0]["message"]["content"]

        return {"msg": chatgpt_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/getAll")  # 展示所有数据
def getAll():
    # 创建游标
    cursor = db_connection.cursor()
    query = "SELECT * FROM dad"
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    return {"records": records}


@app.get("/get/{id}")  # 展示指定数据
def get_by_id(id: int):
    # 创建游标
    cursor = db_connection.cursor()
    query = "SELECT * FROM dad WHERE id = %s"
    cursor.execute(query, (id,))
    record = cursor.fetchone()
    cursor.close()
    if record:
        return {"record": record}
    else:
        return {"message": "Record not found"}


cursor = db_connection.cursor()


class RecordCreate(BaseModel):  # 请求体
    name: str
    age: int
    phone: int


@app.post("/create")  # 增加数据
def create_record(record: RecordCreate):  # 使用 RecordCreate 模型作为参数
    try:
        # 创建游标并使用with语句
        with db_connection.cursor() as cursor:
            # 构建插入查询语句
            insert_query = "INSERT INTO dad (name, age, phone) VALUES (%s, %s, %s)"
            data_to_insert = (record.name, record.age, record.phone)

            # 执行插入操作
            cursor.execute(insert_query, data_to_insert)
            db_connection.commit()

        return {"message": "Record created successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update/{id}")  # 修改数据
def update_record(id: int, record: RecordCreate):  # 使用 RecordUpdate 模型作为参数
    try:
        # 创建游标并使用with语句
        with db_connection.cursor() as cursor:
            # 构建更新查询语句
            update_query = "UPDATE dad SET name = %s, age = %s, phone = %s WHERE id = %s"
            data_to_update = (record.name, record.age, record.phone, id)

            # 执行更新操作
            cursor.execute(update_query, data_to_update)
            db_connection.commit()

        return {"message": "Record updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete/{id}")  # 删除数据
def delete_record(id: int):
    try:
        # 创建游标
        cursor = db_connection.cursor()

        # 构建删除查询语句
        delete_query = "DELETE FROM dad WHERE id = %s"

        # 执行删除操作
        cursor.execute(delete_query, (id,))
        db_connection.commit()

        # 关闭游标
        cursor.close()

        return {"message": "Record deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 关闭游标和数据库连接

# 在终端键入 uvicorn main:app --reload   （对应名启动）
