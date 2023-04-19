from pydantic import BaseModel
from typing import Optional
from datetime import datetime

##base model for post - creating the users
class User_Pydantic(BaseModel):
    id: Optional[int] = -1
    first_name: str
    last_name: str
    password: Optional[str] = ""
    username: Optional[str] = ""
    account_created: Optional[datetime] = '1900-01-00 00:00:00'
    account_updated: Optional[datetime] = '1900-01-00 00:00:00'

class Product_Pydantic(BaseModel):
    id: Optional[int] = -1
    name: Optional[str] = None
    description:Optional[str] = None
    sku:Optional[str] = None
    manufacturer:Optional[str] = None
    quantity : Optional[int]=99999
    date_added: Optional[datetime] = '1900-01-00 00:00:00'
    date_last_updated: Optional[datetime] = '1900-01-00 00:00:00'
    owner_user_id:Optional[int] = -1
    
class Image_Pydantic(BaseModel):
    image_id: Optional[int] = -1
    product_id: Optional[int] =-1
    file_name: Optional[str] = None
    date_created: Optional[datetime] = '1900-01-00 00:00:00'
    s3_bucket_path: Optional[str] = None
    