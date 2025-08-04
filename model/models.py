"""
Built upon Python type hints, are primarily used for data validation, parsing, 
and serialization in Python applications
"""
from pydantic import BaseModel, Field, RootModel
from typing import Optional, List, Dict, Any, Union

class Metadata(BaseModel):
    """
        Document Metadata Model
    """
    Summary: List[str] = Field(default_factory=list, description="Summary of the document")
    Title: str
    Author: str
    DateCreated: str
    LastModifiedDate: str
    Publisher: str
    Language: str
    PageCount: Union[int, str]
    Sentimenttone: str

class ChangeFormat(BaseModel):
    """
        Document Comparison Response Model
    """
    page: str
    changes: str

class SummaryResponse(RootModel[list:[ChangeFormat]]):
    """
    Summary Response
    """
    pass
