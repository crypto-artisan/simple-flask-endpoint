#!/usr/bin/env python
import os, requests, json, mammoth, time
from rich import print
from rich.markdown import Markdown
from dotenv import load_dotenv
from lib.openlib import OpenAI
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langchain_openai.llms import OpenAI
from tools.functions import handle_user_input, save_conversation
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

app = Flask(__name__)
# app.debug = True
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
CORS(app)

# Get API key
load_dotenv()
api_key = os.getenv("open_ai_key")
# brave_api = os.getenv("brave_api")
llm = OpenAI(model="gpt-3.5-turbo-instruct",api_key=api_key, temperature=0.9)
print("api_key-----", api_key)

# If modifying these scopes, delete the file token.json.
SCOPE_DOC = ["https://www.googleapis.com/auth/documents.readonly"]

# The ID of the Google Docs document you want to read.
FILE_FORMATING_DOC_ID = "1coS8dsXq9tO4PAnTooxH4e_6SvuEEnssT9fSu8W4CYo"
FACEBOOK_ENGAGEMENT_DOC_ID = "1NrP8hsZKqohkB9ddBgQg8Iq5B6bXAMW5nDIKrrIvxGQ"

# If modifying these scopes, delete the file token.json.
SCOPES_SHEET = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1q7zyacK3vczYxtuQ1II5hD9gCY_142qHuuEdQTac64M"
SINGLE_PERSON_PROMPT = "Singleperson Prompt!C2:C2"
MULTI_PERSON_PROMPT = "Multiperson Prompt!C2:C2"

# Read Content from  Google Doc with "XXX" ID
def readFileFormatingDoc():
    """Shows basic usage of the Docs API.
    Prints the title and all content of a sample document.
    """
    creds = None
    if os.path.exists("token_doc.json"):
        creds = Credentials.from_authorized_user_file("token_doc.json", SCOPE_DOC)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPE_DOC
            )
            creds = flow.run_local_server(port=0)
        with open("token_doc.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("docs", "v1", credentials=creds)
        document = service.documents().get(documentId=FILE_FORMATING_DOC_ID).execute()
        print(f"The title of the document is: {document.get('title')}")

        # Get the content of the document
        content = document.get('body').get('content')
        document_content = "" # Initialize a list to store the content
        for item in content:
            # Check if the item is a paragraph
            if 'paragraph' in item:
                elements = item.get('paragraph').get('elements')
                for element in elements:
                    text_run = element.get('textRun')
                    if text_run:
                        text_content = text_run.get('content')
                        # print(text_content)
                        document_content += text_content # Add the content to the list
        return document_content # Return the content

    except HttpError as err:
        print(f"An error occurred: {err}")
        return "error" # Return an "error" in case of an error

# Read Content from  Google Doc with "XXX" ID
def readFacebookEngagementDoc():
    """Shows basic usage of the Docs API.
    Prints the title and all content of a sample document.
    """
    creds = None
    if os.path.exists("token_doc.json"):
        creds = Credentials.from_authorized_user_file("token_doc.json", SCOPE_DOC)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPE_DOC
            )
            creds = flow.run_local_server(port=0)
        with open("token_doc.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("docs", "v1", credentials=creds)
        document = service.documents().get(documentId=FACEBOOK_ENGAGEMENT_DOC_ID).execute()
        print(f"The title of the document is: {document.get('title')}")

        # Get the content of the document
        content = document.get('body').get('content')
        document_content = "" # Initialize a list to store the content
        for item in content:
            # Check if the item is a paragraph
            if 'paragraph' in item:
                elements = item.get('paragraph').get('elements')
                for element in elements:
                    text_run = element.get('textRun')
                    if text_run:
                        # print(text_run.get('content'))
                        document_content += text_run.get('content') # Add the content to the list
        return document_content # Return the content    
    except HttpError as err:
        print(err)
        return "error" # Return an "error" in case of an error

# Read Prompt from Sheet named "Singleperson Prompt" within Google Sheet with "XXX" ID
def readSiglePersonPrompt_SHEET():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token_sheet.json"):
    creds = Credentials.from_authorized_user_file("token_sheet.json", SCOPES_SHEET)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES_SHEET
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token_sheet.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SINGLE_PERSON_PROMPT)
        .execute()
    )
    values = result.get("values", [])

    if not values:
      print("No data found.")
      return

    print("MegaPrompt:")
    document_content = "" # Initialize a list to store the content
    for row in values:
      # Print columns A and E, which correspond to indices 0 and 4.
      print(f"{row[0]}")
      document_content += row[0] # Add the content to the list
    return document_content # Return the content
  except HttpError as err:
    print(err)
    return "error"

# Read Prompt from Sheet named "Multiperson Prompt"  within Google Sheet with "XXX" ID
def readMultiPersonPrompt_SHEET():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES_SHEET)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES_SHEET
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=MULTI_PERSON_PROMPT)
        .execute()
    )
    values = result.get("values", [])

    if not values:
      print("No data found.")
      return

    print("MegaPrompt:")
    document_content = "" # Initialize a list to store the content
    for row in values:
      # Print columns A and E, which correspond to indices 0 and 4.
      print(f"{row[0]}")
      document_content += row[0] # Add the content to the list
    return document_content # Return the content
  except HttpError as err:
    print(err)
    return "error" 

@app.route('/api/proprietary-assistant', methods = ['POST'])
def proprietary_assistant():
    prompt = request.json["prompt"]
    gpt_output = llm(prompt)
    markdown = Markdown(gpt_output, code_theme="one-dark")
    print('-------------------MARK-----------------', markdown)
    return jsonify({'result': gpt_output})

#Endpoint
@app.route('/api/file-format', methods = ['GET'])
def file_format():
    result = readFileFormatingDoc()
    return jsonify({'result': result})

#Endpoint
@app.route('/api/facebook-engagement', methods = ['GET'])
def facebook_engagement():
    result = readFacebookEngagementDoc()
    return jsonify({'result': result})

#Endpoint
@app.route('/api/singleperson-prompt', methods = ['GET'])
def singleperson_prompt():
    result = readSiglePersonPrompt_SHEET()
    return jsonify({'result': result})

#Endpoint
@app.route('/api/multiperson-prompt', methods = ['GET'])
def multiperson_prompt():
    result = readMultiPersonPrompt_SHEET()
    return jsonify({'result': result})
    
@app.route('/', methods = ['GET'])
def home():
    return render_template("/api/index.html")

