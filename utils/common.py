import uuid
import os
from urllib.parse import urlparse

def validate_analyzed_data_response(analyzed_data: dict) -> bool:
    return all(value >= 1 for value in analyzed_data.values()) and isinstance(analyzed_data, dict)

def generate_uuid():
    return str(uuid.uuid4())

def get_file_url_extension(url):
    MAPPED_EXTENSIONS = {
        ".pdf": "PDF",
        ".csv": "CSV"
    }
    print (f"url=={url}")
    parsed_url = urlparse(url)
    path = parsed_url.path
    file_extension = os.path.splitext(path)[1]
    print (f"file_extension{file_extension}")
    try:
        file_extension = MAPPED_EXTENSIONS[file_extension]
    except Exception as e:
        file_extension = "UNKNOWN"
    return file_extension

