from sqlalchemy import create_engine
from dotenv import load_dotenv
from database.initalize_db import create_table
from sqlalchemy.orm import sessionmaker
import os
from model.model import User_Pydantic,Product_Pydantic,Image_Pydantic
from database.initalize_db import User,Product,Image
from datetime import datetime
import re
import bcrypt
import boto3
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
import json
from fastapi.responses import JSONResponse
import logging

class database_functions():
    def __init__(self):
        load_dotenv(verbose=True)
        host=os.getenv('HOST')
        user=os.getenv('USERNAME')
        password=os.getenv('PASSWORD')
        schema_name=os.getenv('SCHEMA_NAME') 
        self.db_uri='mysql+pymysql://'+user+':'+password+'@'+host+'/'+schema_name+''
        self.engine = create_engine(self.db_uri)
        create_table()
        #configure Logging library
        logging.basicConfig(filename="logs/cloudlogs.log", format='%(levelname)s %(message)s', filemode='w',level=logging.DEBUG)

    def create_password_hash(self,password,salt=None):
        #password is encrypted into array of bytes
        bytes = password.encode('utf-8')
        # generating the salt for password
        if salt==None:
            salt = bcrypt.gensalt(12)
        # Hashing the password and converting to string and removing the leading 'b' 
        password_enrypted=bcrypt.hashpw(bytes, salt)
        return  password_enrypted
    
    def check_connection(self):
        conn = None
        try:
            conn = self.engine.connect()
            logging.info("Database connection is successful")
            return 'connected-200'
        except Exception as e:
            logging.fatal(f"Database connection failed with error: {e}")
            return 'error-503'
        finally:
            if conn ==None:
                return 'error-503'
            conn.close()
    
    # function for validating an Email
    def check_email(self,email):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if re.match(email_pattern,email):
            return True
        else:
            return False

    def write_user_data(self,user:User_Pydantic):
        Session=None
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            if not (self.check_email(user.username)):
                return '400_email'
            dateTimeObj = datetime.now()
            password_enrypted=str(self.create_password_hash(user.password))[1:]
            new_user = User(first_name=user.first_name,
                            last_name=user.last_name,password=password_enrypted.encode(),
                            username=user.username,account_created=dateTimeObj,
                            account_updated=dateTimeObj)
            session.add(new_user)
            session.commit()
            logging.info("User data is added in database")
            return {
                    "id": new_user.id,
                    "first_name": new_user.first_name,
                    "last_name": new_user.last_name,
                    "username": new_user.username,
                    "account_created":new_user.account_created,
                    "account_updated": new_user.account_updated
            }
        except Exception as e:
            logging.exception(f"Exception adding user data to database: {e}")
            return '400_bad'
        finally:
            if Session != None:
                session.close()
    
    def read_user_data(self,user_id=-1,username=None):
        Session=None
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            if user_id != -1 and username == None:
                user = session.query(User).filter(User.id == user_id).first()
            elif user_id == -1 and username != None:
                user = session.query(User).filter(User.username == username).first()
            elif user_id != -1 and username != None:
                user=session.query(User).filter(User.username == username, User.id == user_id).first()
            if user:
                logging.info(f"Read user data from database for configuration user_id: {user_id} and username: {username}")
                return {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "account_created":user.account_created,
                    "account_updated": user.account_updated
            }
            else:
                logging.error(f"No user with user_id: {user_id} and username: {username} exists in the database")
                return 'no_user'
        except Exception as e:
            logging.exception(f"Exception loading user data {e}")
            return 'user_exception'
        finally:
            if Session != None:
                session.close()

    def read_user_password(self,username):
        Session=None
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            user = session.query(User).filter(User.username == username).first()
            if user:
                logging.info(f"Read password for user {username}")
                return {
                'password':user.password
            }
            else:
                logging.error(f"No user with username: {username} exists in the database")
                return 'wrong_username'
        except Exception as e:
            logging.exception(f"Exception reading password for user: {username}, exception {e}")  
            return 'user_exception'
        finally:
            if Session != None:
                session.close()

    def update_user_data(self,username,userReq:User_Pydantic,userId):
        Session=None
        if userReq.first_name=='' or userReq.last_name=='' or userReq.password=='' or userReq.username != username:
            logging.error("Bad request for updating user data")
            return '400_bad'
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            dateTimeObj = datetime.now()
            user=session.query(User).filter(User.id == userId).first()
            user.first_name=userReq.first_name
            user.last_name=userReq.last_name
            password_enrypted=str(self.create_password_hash(userReq.password))[1:].encode()
            user.password=password_enrypted
            user.account_updated=dateTimeObj
            session.commit()
            logging.info(f"Updated user data for username: {username}")
            return '204_nocontent'
        except Exception as e:
            logging.exception(f"Exception updating user data for username: {username}, exception: {e} ")
            return 'user_exception'
        finally:
            if Session != None:
                session.close()

    
    def write_product_data(self,userId,product:Product_Pydantic):
        Session=None
        if product.quantity < 0 or product.quantity > 100:
            logging.error("Bad request for writing product data, quantity not in range")
            return '400_bad'
        elif product.name == None or product.description == None or product.sku == None or product.manufacturer == None or product.quantity == 99999:
            logging.error("Bad request for writing product data, required field is missing")
            return '400_bad'
        elif product.name == "" or product.description == "" or product.sku == "" or product.manufacturer == "" :
            logging.error("Bad request for writing product data, required field is blank")
            return '400_bad'
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            dateTimeObj = datetime.now()
            new_product = Product(name=product.name,
                            description=product.description,sku=product.sku,
                            manufacturer=product.manufacturer,quantity=product.quantity,date_added=dateTimeObj,
                            date_last_updated=dateTimeObj,owner_user_id=userId)
            session.add(new_product)
            session.commit()
            logging.info("Product data added to database")
            return {
                    "id": new_product.id,
                    "name": new_product.name,
                    "description": new_product.description,
                    "sku": new_product.sku,
                    "manufacturer":new_product.manufacturer,
                    "quantity": new_product.quantity,
                    "date_added":new_product.date_added,
                    "date_last_updated":new_product.date_last_updated,
                    "owner_user_id":new_product.owner_user_id
            }
        except Exception as e:
            logging.exception(f"Exception writing product data to database, exception: {e}")
            return 'exception'
        finally:
            if Session != None:
                session.close()

    def read_product_data(self,productId=-1,sku=None):
        Session=None
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            if productId != -1 and sku == None:
                product=session.query(Product).filter(Product.id == productId).first()
            elif productId == -1 and sku != None:
                product=session.query(Product).filter(Product.sku == sku).first()
            elif productId != -1 and sku != None:
                product=session.query(Product).filter(Product.sku == sku,Product.id == productId).first()
            if product:
                logging.info(f"Reading product data for configuration: product_id :{productId} and sku : {sku}")
                return {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "sku": product.sku,
                    "manufacturer":product.manufacturer,
                    "quantity": product.quantity,
                    "date_added":product.date_added,
                    "date_last_updated":product.date_last_updated,
                    "owner_user_id":product.owner_user_id
            }
            else:
                logging.error(f"No product with product_id: {productId} and sku: {sku} exists in the database")
                return 'no_product'
        except Exception as e:
            logging.exception(f"Exception reading product data, exception: {e}")
            return 'product_exception'
        finally:
            if Session != None:
                session.close()

    def update_product_data(self,productId,productReq:Product_Pydantic,type):
        Session=None
        if productReq.quantity < 0 or productReq.quantity > 100 and productReq.quantity != 99999: 
            logging.error("Bad request for update product data, quantity not in range")
            return '400_bad'
        if (type=='put') and (productReq.name == None or productReq.description == None or productReq.manufacturer == None or productReq.sku == None or productReq.quantity == 99999 ):
            logging.error("Bad request for writing product data, required field is missing for put request")
            return '400_bad'
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            dateTimeObj = datetime.now()
            product=session.query(Product).filter(Product.id == productId).first()
            if productReq.name != None:
                product.name=productReq.name
            if productReq.description !=None:
                product.description=productReq.description
            if productReq.manufacturer != None:
                product.manufacturer=productReq.manufacturer
            if productReq.sku != None:
                product.sku=productReq.sku
            if productReq.quantity != 99999:
                product.quantity=productReq.quantity
            product.date_last_updated=dateTimeObj
            session.commit()
            logging.info(f"Updated product data for product_id: {productId}")
            return '204_nocontent'
        except Exception as e:
            logging.exception(f"Exception updating product data, exception: {e}")
            return 'user_exception'
        finally:
            if Session != None:
                session.close()

    def delete_product(self,productId):
        Session = None
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            product=session.query(Product).filter(Product.id == productId).first()
            session.delete(product)
            session.commit()
            self.delete_s3_objects()
            logging.info(f"Deleted product data for product_id: {productId}")
        except Exception as e:
            logging.exception(f"Exception deleting product data for product_id: {productId}, exception: {e}")
            return 'exception'
        finally:
            if Session != None:
                session.close()
                
    def fetch_all_images(self,productId):
        Session = None
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            image_found=session.query(Image).filter(Image.product_id == productId).all()
            logging.info(f"Fetching all image data for product_id: {productId}")
            return image_found
        except Exception as e:
            logging.exception(f"Exception reading image data for product_id: {productId}, exception: {e}")
            return 'exception'
        finally:
            if Session != None:
                session.close()
                
    def fetch_image(self,productId,imageId):
        Session = None
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            image_found=session.query(Image).filter(Image.product_id == productId, Image.image_id==imageId).all()
            if len(image_found) == 0:
                logging.info(f"No image for product_id: {productId} and image_id: {imageId}")
                return 'no_image'
            logging.info(f"Fetching image for product_id: {productId} and image_id: {imageId}")
            return image_found
        except Exception as e:
            logging.exception(f"Exception reading image data for product_id: {productId} and image_id: {imageId}, exception: {e}")
            return 'exception'
        finally:
            if Session != None:
                session.close()
    def delete_s3_objects(self,image_id=-1):
        Session = None
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            if image_id==-1:
                images  = session.query(Image).filter(Image.product_id.is_(None)).all()
            else:
                images  = session.query(Image).filter(Image.image_id==image_id).all()
            json_objects = [img.__dict__ for img in images]
            s3 = boto3.client('s3')
            bucket_name = os.getenv('S3_Bucket_Name')
            for obj in json_objects:
                object_key = obj['s3_bucket_path']
                # delete the object
                s3.delete_object(Bucket=bucket_name, Key=object_key)
            session.query(Image).filter(Image.product_id.is_(None)).delete()
            session.commit()
            logging.info(f"Image deleted from s3, image_id:{image_id}, object_key:{object_key}")
        except Exception as e:
            logging.exception(f"Exception deleting image from s3, image_id:{image_id} , exception: {e}")
            return 'exception'
        finally:
            if Session != None:
                session.close()
            
    def post_image_data(self,productId,image:UploadFile,file_path):
        Session = None
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            dateTimeObj = datetime.now()
            date_str = dateTimeObj.strftime('%Y%m%d')
            time_str = dateTimeObj.strftime('%H%M%S')
            date_time_str = f"{date_str}_{time_str}"
            #Create the s3 bucket path
            s3 = boto3.client('s3')
            bucket_name = os.getenv('S3_Bucket_Name')
            object_key = f'{productId}_'+str(date_time_str)+'_'+str(image.filename)
            with open(file_path, 'rb') as f:
               s3.upload_fileobj(f, bucket_name, object_key)
            s3_bucket_path=object_key
            new_image = Image(product_id=productId,file_name=image.filename,date_created=dateTimeObj,s3_bucket_path=s3_bucket_path)
            session.add(new_image)
            session.commit()
            if new_image:
                logging.info(f"Image data added to database for product_id: {productId}")
                return {
                    "image_id": new_image.image_id,
                    "product_id":new_image.product_id,
                    "file_name":new_image.file_name,
                    "date_created":new_image.date_created,
                    "s3_bucket_path":new_image.s3_bucket_path     
            }
            else:
                logging.error(f"New image record not inserted into database for productId: {productId}")
                return "no_image"
        except Exception as e:
            logging.exception(f"Exception adding image data to database for product_id: {productId}")
            return 'exception'
        finally:
            if Session != None:
                session.close()
    
    def delete_image(self,productId,imageId):
        Session=None
        try:
            Session=sessionmaker(bind=self.engine)
            session=Session()
            image=session.query(Image).filter(Image.product_id == productId, Image.image_id==imageId).first()
            self.delete_s3_objects(imageId)
            session.delete(image)
            session.commit()      
            logging.info(f"Deleted image data from database for product_id: {productId} and image_id: {productId}") 
        except Exception as e:
            logging.exception(f"Exception deleting image data from database for product_id: {productId} and image_id: {productId}") 
            return {'user':'exception'}
        finally:
            if Session != None:
                session.close()
    