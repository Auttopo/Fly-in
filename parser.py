
from pydantic import BaseModel, Field
from os.path import exists
from typing import TextIO

class FlyinError(Exception):
    pass

class FlyinParser(BaseModel):
    """parser class of the project"""

    def __init__(self, file_name: str) -> None:
        if not exists(file_name):
            raise FlyinError(f"the file '{file_name}' do not exist")
        file: TextIO
        with open(file_name, "r") as file:
            file_data = file.read()
        print(file_data)
        

