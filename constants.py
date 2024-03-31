import os
import boto3
from io import BytesIO
from langchain.document_loaders import UnstructuredWordDocumentLoader, PyPDFLoader

# ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
# SOURCE_DIRECTORY = f"{ROOT_DIRECTORY}/SOURCE_DOCUMENTS"
DOCUMENT_MAP = {
    ".pdf": PyPDFLoader,
    ".docx": UnstructuredWordDocumentLoader
}

# def file_load(file_path):
    
#     try:
#         file_extension = os.path.splitext(file_path)[1]
#         loader_class = DOCUMENT_MAP.get(file_extension)
#         if loader_class:
#             loader = loader_class(file_path)
#         else:
#             raise ValueError("Document type is undefined")

#         return loader.load()
#     except Exception as ex:
#         raise Exception('%s loading error: \n%s' % (file_path, ex))

def file_load(username):
    s3 = boto3.client(
        service_name = 's3',
        region_name = 'us-east-1')
    bucket_name = 'ttg-resume'
    response = s3.list_objects_v2(
        Bucket= bucket_name,
        Prefix=f'{username}/'
    )
    if 'Contents' in response:
        if len(response['Contents']) == 1:
            key = response['Contents'][0]['Key']
            
            file_extension = os.path.splitext(key)
            loader_class = DOCUMENT_MAP.get(file_extension)
            obj = s3.get_object(Bucket=bucket_name, Key=key)["Body"].read()

            if loader_class:
                loader = loader_class(BytesIO(obj))
            else:
                raise ValueError("Document type is undefined")

            return loader.load()
        else:
            print("Multiple files found in the folder.")
    else:
        print("No files found in the folder.")
