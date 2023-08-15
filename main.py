from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from gradio_client import Client

# Import Gradio Server https and Ai Model from a Secrets.py file
from Secrets import *

app = FastAPI()

# Allowed origins add your domain if needed
origins = [
    "http://localhost",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

connection_string = connection_string
database_client = MongoClient(connection_string)


def request_gradio(message):
    try:
        client = Client(Gradio_Server)
        result = client.predict(
            Model, "user_and_ai", message, "", "", "", "", "", "", "", 0, 0.75, 40, 2, 1.2, 128, False, False,
            api_name="/inference"
        )
        print(result)
        modified_result = result[0]
        print(modified_result["value"])
        return modified_result["value"]

# Responses an error message if an error occurs
    except ValueError as e:
        error_message = "I'm sorry, but I've got an error, please contact Support or wait until we've fixed this."
        print(e)
        return error_message


# Endpoint for you to chat with our AI
@app.post('/ai')
async def process_request(data: dict):
    message = data.get('message')
    if message:
        result = request_gradio(message)
        return {"result": result}
    else:
        return {"error": "Invalid request"}


# Endpoint to Translate with DeepL Ai
@app.post('/translate')
async def process_request(data:dict):
    url = "https://api-free.deepl.com/v2/translate"

    source = data.get('source')
    target = data.get('target')
    text = data.get('text')

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "auth_key": DeepL_Key,
        "text": text,
        "source_lang": source,
        "target_lang": target,
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        translated_text = response.json()["translations"][0]["text"]
        return {translated_text, response.status_code}
    else:
        return {"Translation failure Sorry", response.status_code}


# Endpoint to check my bots status
@app.get('/bobby-bot')
async def process_request():
    bot_status = "offline"
    return{bot_status}


# Endpoint to receive user notes (requires user email)
@app.post('/get-notes')
async def process_request(data: dict):
    email = data.get('email')
    db = database_client.bobby68
    result = list(db.notes.find({"email": email}))  # Convert MongoDB cursor to a list

    if result:
        for note in result:
            note['_id'] = str(note['_id'])  # Convert ObjectId to a string for JSON serialization
        print(f"Notes found for the email address {email}: {result}")
        return {"notes": result}
    else:
        print(f"No notes found for the email address {email}")
        return {"notes": [{
      "_id": {
        "$oid": "0"
      },
      "email": "luca@bobby68.de",
      "title": "No Notes Found",
      "description": "Create a new one by clicking the plus sign in the top right hand corner.",
      "steps": ""
    }]}


# Endpoint for creating user notes (requires user email)
@app.post('/create-notes')
async def process_request(data: dict):
    collection = database_client["notes"]
    result = collection.insert_one(
{
  "email": {data.get("email")},
  "title": {data.get("title")},
  "description": {data.get("description")},
  "steps": {data.get("steps")}
})
    return {"created: " + result.inserted_id}


# Endpoint to edit user notes (requires user email)
@app.post('/edit-notes')
async def process_request(data: dict):
    notes_id = data.get('_id')
    return {"/edit-notes currently in development"}


# Endpoint to delete user note (requires user email)
@app.post('/delete-notes')
async def process_request(data: dict):
    data = data.get('notes')
    print(data)
    return {"/delete-notes currently in development"}
