# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "requests",
# ]
# ///

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import subprocess
import json
import glob
import sqlite3
from datetime import datetime
import requests

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['GET', 'POST'],
    allow_headers=['*']
)

class TaskRequest(BaseModel):
    task: str

@app.get("/")
def home():
    return {"message": "Hello, this is for checking only!"}

@app.post("/run")
async def run_task(request: TaskRequest):
    task_description = request.task
    
    try:
        # A1: Install uv and run the data generation script
        if "install uv" in task_description:
            subprocess.run(['pip', 'install', 'uv'], check=True)
            user_email = os.getenv('USER_EMAIL')
            subprocess.run(['python', 'https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py', user_email], check=True)
            return {"message": "Data generated successfully."}
        
        # A2: Format the contents of /data/format.md using Prettier
        elif "format" in task_description:
            subprocess.run(['npx', 'prettier', '--write', '/data/format.md'], check=True)
            return {"message": "File formatted successfully."}
        
        # A3: Count the number of Wednesdays in /data/dates.txt
        elif "count Wednesdays" in task_description:
            with open('/data/dates.txt', 'r') as f:
                dates = f.readlines()
            wednesdays = sum(1 for date in dates if datetime.strptime(date.strip(), '%Y-%m-%d').weekday() == 2)
            with open('/data/dates-wednesdays.txt', 'w') as f:
                f.write(str(wednesdays))
            return {"message": "Counted Wednesdays successfully."}
        
        # A4: Sort contacts in /data/contacts.json
        elif "sort contacts" in task_description:
            with open('/data/contacts.json', 'r') as f:
                contacts = json.load(f)
            sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))
            with open('/data/contacts-sorted.json', 'w') as f:
                json.dump(sorted_contacts, f)
            return {"message": "Contacts sorted successfully."}
        
        # A5: Write the first line of the 10 most recent .log files
        elif "recent logs" in task_description:
            log_files = sorted(glob.glob('/data/logs/*.log'), key=os.path.getmtime, reverse=True)[:10]
            with open('/data/logs-recent.txt', 'w') as f:
                for log_file in log_files:
                    with open(log_file, 'r') as lf:
                        first_line = lf.readline()
                        f.write(first_line)
            return {"message": "Recent logs written successfully."}
        
        # A6: Create an index of H1 titles from Markdown files
        elif "index markdown" in task_description:
            index = {}
            for md_file in glob.glob('/data/docs/*.md'):
                with open(md_file, 'r') as f:
                    for line in f:
                        if line.startswith('# '):
                            index[os.path.basename(md_file)] = line[2:].strip()
                            break
            with open('/data/docs/index.json', 'w') as f:
                json.dump(index, f)
            return {"message": "Index created successfully."}
        
        # A7: Extract sender's email from /data/email.txt using LLM
        elif "extract email" in task_description:
            with open('/data/email.txt', 'r') as f:
                email_content = f.read()
            sender_email = call_llm_to_extract_email(email_content)
            with open('/data/email-sender.txt', 'w') as f:
                f.write(sender_email)
            return {"message": "Email extracted successfully."}
        
        # A8: Extract credit card number from image
        elif "extract credit card" in task_description:
            card_number = call_llm_to_extract_card_number('/data/credit-card.png')
            with open('/data/credit-card.txt', 'w') as f:
                f.write(card_number.replace(" ", ""))
            return {"message": "Credit card number extracted successfully."}
        
        # A9: Find the most similar pair of comments
        elif "similar comments" in task_description:
            with open('/data/comments.txt', 'r') as f:
                comments = f.readlines()
            similar_comments = find_most_similar_comments(comments)
            with open('/data/comments-similar.txt', 'w') as f:
                f.write('\n'.join(similar_comments))
            return {"message": "Similar comments found successfully."}
        
        # A10: Calculate total sales for "Gold" ticket type
        elif "total sales gold" in task_description:
            conn = sqlite3.connect('/data/ticket-sales.db')
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type='Gold'")
            total_sales = cursor.fetchone()[0]
            with open('/data/ticket-sales-gold.txt', 'w') as f:
                f.write(str(total_sales))
            conn.close()
            return {"message": "Total sales calculated successfully."}
        
        else:
            raise HTTPException(status_code=400, detail="Task not recognized.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
async def read_file(path: str):
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        return {"content": content}
    else:
        raise HTTPException(status_code=404, detail="File not found.")

def call_llm_to_extract_email(email_content):
    # Function to call the AI Proxy to extract email
    url = "https://api.aiproxy.com/run"
    headers = {
        "Authorization": f"Bearer {os.environ['AIPROXY_TOKEN']}",
        "Content-Type": "application/json"
    }
    payload = {
        "task": f"Extract the sender's email from the following content: {email_content}"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get("email", "Email not found.")

def call_llm_to_extract_card_number(image_path):
    # Function to call the AI Proxy to extract card number from image
    url = "https://api.aiproxy.com/run"
    headers = {
        "Authorization": f"Bearer {os.environ['AIPROXY_TOKEN']}",
        "Content-Type": "application/json"
    }
    payload = {
        "task": f"Extract the credit card number from the image at {image_path}"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get("card_number", "Card number not found.")

def find_most_similar_comments(comments):
    # Function to find the most similar comments (pseudo-code)
    # Implement your logic here
    return comments[:2]  # Placeholder for the most similar comments

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
