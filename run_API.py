import logging
import os
import argparse
import boto3
from flask import Flask, jsonify, request
from flask_cors import CORS
import PyPDF2
import docx
from io import BytesIO

from load_model import load_Bedrock_model
from prompt_template import get_prompt_template
# from constants import file_load

LLM = load_Bedrock_model()
prompt = get_prompt_template()

S3_BUCKET_NAME = 'ttg-resume'
s3_client = boto3.client('s3')


app = Flask(__name__)
CORS(app)

@app.route('/api/upload', methods=['POST'])
def upload_document():
    username = request.args.get('username')
    uploaded_file = request.files['file']

    if not username:
        return jsonify({'error': 'Username not provided'}), 400
    if not uploaded_file:
        return jsonify({'error': 'No file provided'}), 400

    folder_name = f"{username}/"
    # try:
    #     s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=folder_name)
    # except s3_client.exceptions.ClientError:
    #     # Folder doesn't exist, create it
    #     s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=folder_name, Body='')
    try:
        # Check if the folder exists
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=folder_name)
        existing_contents = [obj['Key'] for obj in response.get('Contents', [])]

        if existing_contents:
            # Delete existing contents of the folder
            for obj_key in existing_contents:
                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=obj_key)

    except s3_client.exceptions.ClientError:
        # Folder doesn't exist, create it
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=folder_name, Body='')

    # Upload the file to the folder
    file_key = f"{folder_name}{uploaded_file.filename}"
    s3_client.upload_fileobj(uploaded_file, S3_BUCKET_NAME, file_key)

    return jsonify({'message': 'File uploaded successfully'}), 200

# @app.route('/api/fetch', methods=['GET'])
def fetch_documents(username):
    # username = request.args.get('username')

    # if not username:
    #     return jsonify({'error': 'Username not provided'}), 400

    # List objects (documents) within the folder corresponding to the username
    folder_name = f"{username}/"
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=folder_name)
        documents = []
        for obj in response.get('Contents', []):
            key = obj['Key']
            # Check if the key represents a folder (by ending with '/')
            if not key.endswith('/'):
                # Fetch document data from S3
                try:
                    document_data = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)['Body'].read()
                    # Parse document contents based on file type
                    if key.endswith('.docx'):
                        document = docx.Document(BytesIO(document_data))
                        text = "\n".join([paragraph.text for paragraph in document.paragraphs])
                        print(text)  # Print the contents of the document
                    # Add document name to the list
                    elif key.endswith('.pdf'):
                        pdf_reader = PyPDF2.PdfReader(BytesIO(document_data))
                        text = ""
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            text += page.extract_text()
                    else:
                        text = "Unsupported file format"
                    documents.append({
                        'name': key.split('/')[-1],
                        'content': text 
                    })
                except s3_client.exceptions.ClientError:
                    print(f"Failed to fetch document data for key: {key}")
        return {'documents': documents} 
    except s3_client.exceptions.ClientError:
        return {'error': 'Failed to fetch documents'}

@app.route("/api/summary", methods=["GET"])
def summary():
    global prompt
    username = request.args.get("username")

    if not username:
        return "No user signed in", 400
    try:
        documents_data = fetch_documents(username)

        # Process the fetched documents
        document_text = ""
        for document_data in documents_data.get("documents", []):
            document_name = document_data.get("name")
            document_content = document_data.get("content")
            document_text += f"Document: {document_name}\nContent: {document_content}\n"

        prompt_full = prompt.format(context=document_text)
        print(prompt_full)
        result = LLM(prompt_full)      

        prompt_response_dict = {
            "Summary": result
        }
        return jsonify(prompt_response_dict), 200
    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5110, help="Port to run the API on. Defaults to 5110.")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to run the UI on. Defaults to 127.0.0.1. "
        "Set to 0.0.0.0 to make the UI externally "
        "accessible from other devices.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO
    )
    app.run(debug=True, host=args.host, port=args.port)
