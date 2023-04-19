from dotenv import load_dotenv
import os
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine,Column, Integer, String,LargeBinary,DateTime,ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
import logging

Base = declarative_base()

class User(Base):
    __tablename__ = 'User_Data'
    id = Column(Integer, primary_key=True,autoincrement= True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    password = Column(LargeBinary)
    username = Column(String(50),primary_key=True)
    account_created= Column(DateTime)
    account_updated= Column(DateTime)
    user_info=relationship("Product",back_populates="product_info")
    #configure Logging library
    logging.basicConfig(filename="logs/cloudlogs.log", format='%(levelname)s %(message)s', filemode='w',level=logging.DEBUG)

class Product(Base):
    __tablename__ = 'Product_Data'
    id = Column(Integer, primary_key=True,autoincrement= True)
    name = Column(String(50))
    description=Column(String(50))
    sku=Column(String(50),primary_key=True)
    manufacturer=Column(String(50))
    quantity = Column(Integer)
    date_added= Column(DateTime)
    date_last_updated= Column(DateTime)
    owner_user_id=Column(Integer,ForeignKey("User_Data.id"))
    product_info = relationship("User", back_populates="user_info")
    product_images_info= relationship("Image",back_populates="image_info")

class Image(Base):
    __tablename__= 'Image_Data'
    image_id = Column(Integer,primary_key=True,autoincrement=True)
    product_id=Column(Integer,ForeignKey("Product_Data.id"))
    file_name=Column(String(100))
    date_created=Column(DateTime)
    s3_bucket_path=Column(String(100))
    image_info=relationship("Product",back_populates="product_images_info")
    
class create_table():
    def __init__(self):
        load_dotenv(verbose=True)
        host=os.getenv('HOST')
        user=os.getenv('USERNAME')
        password=os.getenv('PASSWORD')
        schema_name=os.getenv('SCHEMA_NAME') 
        db_uri='mysql+pymysql://'+user+':'+password+'@'+host+'/'+schema_name+''
        engine = create_engine(db_uri)
        try:
            Base.metadata.create_all(engine)
            logging.info("Successfully created all database tables")
        except Exception as e:
            logging.fatal(f"Database tables cannot be created due to exception: {e}")
        

