import logging
import os
import argparse

from flask import Flask, jsonify, request
# from flask_cors import CORS

from load_model import load_Bedrock_model
from prompt_template import get_prompt_template
from constants import file_load

LLM = load_Bedrock_model()
prompt = get_prompt_template()

app = Flask(__name__)
# CORS(app)


@app.route("/api/summary", methods=["GET"])
def summary():
    global prompt
    username = request.args.get("username")

    if not username:
        return "No user signed in", 400

    # folder_path = os.path.join("SOURCE_DOCUMENTS", username)
    # if os.path.exists(folder_path):
    #     files = os.listdir(folder_path)
    #     for file_name in files:
    #         file_path = os.path.join(folder_path, file_name)
    #         if os.path.isfile(file_path):  
    #             docs = file_load(file_path)
    print("called Summary")
    docs = file_load(username)
    print("File loaded")
    prompt_full = prompt.format(context=docs)
    result = LLM(prompt_full)      

    prompt_response_dict = {
        "Summary": result,
        "Sources" : docs
    }
    return jsonify(prompt_response_dict), 200


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
