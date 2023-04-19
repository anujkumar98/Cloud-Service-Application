from fastapi import FastAPI,HTTPException,status,Depends,File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from model.model import User_Pydantic,Product_Pydantic,Image_Pydantic
from database.db_functions import database_functions
from pathlib import Path
import os
import logging
import statsd

#Intialize FastAPI
app=FastAPI()

#Database connection object 
db_connection = None
database_obj=database_functions()

security = HTTPBasic()

#configure Logging library
logging.basicConfig(filename="/logs/cloudlogs.log", format='%(levelname)s %(message)s', filemode='w',level=logging.DEBUG)
#statsd for api count
statsd_counter = statsd.StatsClient('localhost', 8125)

#Code for authentication of user
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    username_entered = credentials.username.encode("utf8")
    fetched_user=database_obj.read_user_data(username=credentials.username)
    if fetched_user=='no_user':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    else:
        is_correct_username = secrets.compare_digest(username_entered, fetched_user['username'].encode("utf8"))
        fetched_user_password=database_obj.read_user_password(credentials.username)
        if fetched_user_password=='wrong_username':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
        else:
            salt_used=str(fetched_user_password['password'].decode())[1:31].encode()
            is_correct_password = secrets.compare_digest(database_obj.create_password_hash(credentials.password,salt_used),fetched_user_password['password'][1:-1])
            salt_used=str(fetched_user_password['password'].decode())[1:31].encode()
    if not (is_correct_username and is_correct_password):
        logging.error("Unauthorized access for username: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    logging.info("Access successful for username: {credentials.username}")   
    return credentials.username
##Fetch user details 
@app.get("/v1/user/{userId}")
def searchUser(userId:int,username: str = Depends(get_current_username)):
    statsd_counter.incr("get_user_from_userId",1)
    statsd_counter.incr("Total_Count",1)
    if not type(userId) is int:
        logging.exception("Exception Unprocessable header for get user endpoint")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid header")
    return_code=database_obj.read_user_data(username=username)
    if(return_code == 'no_user'):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    else:
        if(userId == return_code['id']):
            return return_code
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden request")

#Create user and store in database
@app.post('/v1/user',status_code=status.HTTP_201_CREATED)
def createUser(user:User_Pydantic):
    statsd_counter.incr("post_user",1)
    statsd_counter.incr("Total_Count",1)
    return_code_user_search=database_obj.read_user_data(username=user.username)
    if return_code_user_search == 'no_user':
        return_code=database_obj.write_user_data(user)
        if return_code == '400_email' or return_code == '400_bad':
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect username. Must be a valid email"
            )
        else:
            return return_code
    else:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exist"
                )

#healthz
@app.get('/healthz',status_code=status.HTTP_200_OK)
def check_health():
    statsd_counter.incr("healthz",1)
    statsd_counter.incr("Total_Count",1)
    return_code=database_obj.check_connection()
    if return_code == 'error-503':
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str("Error connecting to MYSQL Server "))
    else: return {"status": "connected"}


#health to check cicd
@app.get('/health',status_code=status.HTTP_200_OK)
def check_health():
    return_code=database_obj.check_connection()
    if return_code == 'error-503':
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str("Error connecting to MYSQL Server "))
    else: return {"status": "connected"}


#Put endpoint for user
@app.put("/v1/user/{userId}",status_code=status.HTTP_204_NO_CONTENT)
def update_user(user:User_Pydantic,userId:int,username: str = Depends(get_current_username)):
    statsd_counter.incr("put_user_from_userId",1)
    statsd_counter.incr("Total_Count",1)
    if type(userId) != int:
        logging.exception("Exception Unprocessable header for put user endpoint")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid header")
    return_code=database_obj.read_user_data(username=username)
    if(return_code == 'no_user'):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    else:
        if(userId == return_code['id']):
            return_code_update=database_obj.update_user_data(username,user,userId)
            if return_code_update == '400_bad' or return_code_update == 'user_exception':
              raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden request")

    
#Post endpoint for product
@app.post('/v1/product',status_code=status.HTTP_201_CREATED)
def create_product(product:Product_Pydantic,username: str = Depends(get_current_username)):
    statsd_counter.incr("post_product",1)
    statsd_counter.incr("Total_Count",1)
    if not type(product.quantity) is int:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    if product.name == None or product.description==None or product.sku==None or product.manufacturer==None or product.quantity==99999:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) 
    return_code=database_obj.read_user_data(username=username)
    if(return_code == 'no_user'):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    else:
        return_code_product_find=database_obj.read_product_data(sku=product.sku)
        if return_code_product_find == 'no_product':
            userId=return_code['id']
            return_code_product_add=database_obj.write_product_data(userId=userId,product=product)
            if return_code_product_add == '400_bad':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST
                    )
            elif return_code_product_add == 'exception':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Error in request body'
                    )
            else:
                return return_code_product_add
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product sku already exist"
            )
    
#Get request for product
@app.get('/v1/product/{productId}',status_code=status.HTTP_200_OK)
def find_product(productId:int):
    statsd_counter.incr("get_product_from_productId",1)
    statsd_counter.incr("Total_Count",1)
    if not type(productId) is int:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid header")
    return_code=database_obj.read_product_data(productId=productId)
    if(return_code == 'no_product'):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return return_code


#put request for product
@app.put('/v1/product/{productId}',status_code=status.HTTP_204_NO_CONTENT)
def update_product(productId:int, product:Product_Pydantic,username: str = Depends(get_current_username)):
    statsd_counter.incr("put_product_from_productId",1)
    statsd_counter.incr("Total_Count",1)
    if not type(product.quantity) is int:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return_code_fetch_user=database_obj.read_user_data(username=username)
    if(return_code_fetch_user == 'no_user'):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return_code_fetch_product=database_obj.read_product_data(productId=productId)
    if return_code_fetch_product == 'no_product':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    elif return_code_fetch_product == 'exception':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST
                )
    else:
        if return_code_fetch_product['owner_user_id']==return_code_fetch_user['id']:
            if product.sku != return_code_fetch_product['sku']:
                if product.sku != None:
                    return_code_fetch_product_sku=database_obj.read_product_data(sku=product.sku)
                else: return_code_fetch_product_sku='no_product'
                if return_code_fetch_product_sku == 'no_product':
                    return_code_update_product=database_obj.update_product_data(productId=productId,productReq=product,type='put')
                    if return_code_update_product== '400_bad':
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU Exists")
            else:
                return_code_update_product=database_obj.update_product_data(productId=productId,productReq=product,type='put')
                if return_code_update_product== '400_bad':
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden request")
@app.patch("/v1/product/{productId}",status_code=status.HTTP_204_NO_CONTENT)
def update_product(productId:int, product:Product_Pydantic,username: str = Depends(get_current_username)):
    statsd_counter.incr("patch_product_from_productId",1)
    statsd_counter.incr("Total_Count",1)
    if not type(product.quantity) is int:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return_code_fetch_user=database_obj.read_user_data(username=username)
    if(return_code_fetch_user == 'no_user'):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return_code_fetch_product=database_obj.read_product_data(productId=productId)
    if return_code_fetch_product == 'no_product':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    elif return_code_fetch_product == 'exception':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST
                )
    else:
        if return_code_fetch_product['owner_user_id']==return_code_fetch_user['id']:
            if product.sku != return_code_fetch_product['sku']:
                if product.sku != None:
                    return_code_fetch_product_sku=database_obj.read_product_data(sku=product.sku)
                else: return_code_fetch_product_sku='no_product'
                if return_code_fetch_product_sku == 'no_product':
                    return_code_update_product=database_obj.update_product_data(productId=productId,productReq=product,type='patch')
                    if return_code_update_product== '400_bad':
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU Exists")
            else:
                return_code_update_product=database_obj.update_product_data(productId=productId,productReq=product,type='patch')
                if return_code_update_product== '400_bad':
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden request")

#delete request for product
@app.delete("/v1/product/{productId}",status_code=status.HTTP_204_NO_CONTENT)
def delete_product(productId:int,username: str = Depends(get_current_username)):
    statsd_counter.incr("delete_product_from_productId",1)
    statsd_counter.incr("Total_Count",1)
    return_code_fetch_user=database_obj.read_user_data(username=username)
    if(return_code_fetch_user == 'no_user'):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return_code_fetch_product=database_obj.read_product_data(productId=productId)
    if return_code_fetch_product == 'no_product':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    elif return_code_fetch_product == 'exception':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST
                )
    else:
        if return_code_fetch_product['owner_user_id']==return_code_fetch_user['id']:
            database_obj.delete_product(productId=productId)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden request")

#List of all images for a product
@app.get("/v1/product/{productId}/image",status_code=status.HTTP_200_OK)
def list_images(productId:int,username: str = Depends(get_current_username)):
    statsd_counter.incr("get_all_image_from_productId",1)
    statsd_counter.incr("Total_Count",1)
    return_code_fetch_user=database_obj.read_user_data(username=username)
    if(return_code_fetch_user == 'no_user'):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return_code_fetch_product=database_obj.read_product_data(productId=productId)
    if return_code_fetch_product == 'no_product':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    elif return_code_fetch_product == 'exception':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    else:
        if return_code_fetch_product['owner_user_id']==return_code_fetch_user['id']:
            return_code_fetch_images= database_obj.fetch_all_images(productId)
            return return_code_fetch_images
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden request")
  
#List the property of an image
@app.get("/v1/product/{productId}/image/{imageId}",status_code=status.HTTP_200_OK)
def list_images(productId:int,imageId:int,username: str = Depends(get_current_username)):
    statsd_counter.incr("get_image_from_productId_and_imageId",1)
    statsd_counter.incr("Total_Count",1)
    return_code_fetch_user=database_obj.read_user_data(username=username)
    if(return_code_fetch_user == 'no_user'):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return_code_fetch_product=database_obj.read_product_data(productId=productId)
    if return_code_fetch_product == 'no_product':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    elif return_code_fetch_product == 'exception':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    else:
        if return_code_fetch_product['owner_user_id']==return_code_fetch_user['id']:
            return_code_fetch_images= database_obj.fetch_image(productId,imageId)
            if return_code_fetch_images == 'no_image':
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden request")
            return return_code_fetch_images
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden request")
     
#Post images and creating metadata -> handle upload and s3 logic      
@app.post('/v1/product/{productId}/image',status_code=status.HTTP_201_CREATED)
def post_images(productId:int,image: UploadFile=File(...),username: str = Depends(get_current_username)):
    statsd_counter.incr("post_image_from_productId",1)
    statsd_counter.incr("Total_Count",1)
    return_code_fetch_user=database_obj.read_user_data(username=username)
    if(return_code_fetch_user == 'no_user'):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return_code_fetch_product=database_obj.read_product_data(productId=productId)
    if return_code_fetch_product == 'no_product':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    elif return_code_fetch_product == 'exception':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    else:
        if return_code_fetch_product['owner_user_id']==return_code_fetch_user['id']:
            with open(image.filename, "wb") as buffer:
                import shutil
                shutil.copyfileobj(image.file, buffer)
             # Get the full path of the saved file
            file_path = os.path.join(os.getcwd(), image.filename)
            if not 'image' in image.content_type:
                raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="UNSUPPORTED_MEDIA_TYPE")
            return_code_post_product= database_obj.post_image_data(productId,image,file_path)
            os.remove(file_path)
            ##Add s3 logic
            if return_code_post_product == 'exception':
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden request")
    return  return_code_post_product   
#Delete the image
@app.delete('/v1/product/{productId}/image/{imageId}',status_code=status.HTTP_204_NO_CONTENT)
def delete_image(productId:int,imageId:int,username:str = Depends(get_current_username)):
    statsd_counter.incr("delete_image_from_productId_and_imageId",1)
    statsd_counter.incr("Total_Count",1)
    return_code_fetch_user=database_obj.read_user_data(username=username)
    if(return_code_fetch_user == 'no_user'):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return_code_fetch_product=database_obj.read_product_data(productId=productId)
    if return_code_fetch_product == 'no_product':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    elif return_code_fetch_product == 'exception':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    else:
        if return_code_fetch_product['owner_user_id']==return_code_fetch_user['id']:
            return_code_fetch_images= database_obj.fetch_image(productId,imageId)
            if return_code_fetch_images == 'no_image':
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden request")
            database_obj.delete_image(productId,imageId)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden request")
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000,reload=True)