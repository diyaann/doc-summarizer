import boto3
from langchain.llms import Bedrock

def load_Bedrock_model():
    bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name='us-east-1')
    model_id = 'amazon.titan-text-lite-v1'
    model_kwargs ={
        "maxTokenCount":4096,
        "stopSequences":[],
        "temperature":0,
        "topP":1
    }
    llm = Bedrock (model_id=model_id,region_name='us-east-1',client= bedrock_runtime, model_kwargs=model_kwargs)
    return llm