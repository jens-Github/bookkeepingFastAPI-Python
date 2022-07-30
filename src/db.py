from motor.motor_asyncio import AsyncIOMotorClient
import os


# mongo_client = AsyncIOMotorClient("mongodb://localhost:27018/")
mongo_client = AsyncIOMotorClient(os.environ['MONGODB_CONNSTRING'])
db = mongo_client['BookKeepingDb']
expense_documents = db['expenses']
income_documents = db['incomes']
user_documents = db['users']
