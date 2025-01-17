from fastapi import FastAPI, HTTPException, Depends, status,Header
from app.auth import *
from app.models import *
from app.database import *
from fastapi.middleware.cors import CORSMiddleware
import requests


app = FastAPI()

# status and active update function ------------------------------------------------------------------------------------------------------------->>


# status and active update function ------------------------------------------------------------------------------------------------------------->>

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing (change while deploying)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#Login&Register page----------------------------------------------------------------------------------------------------------------------------->>

@app.post("/register", status_code=201)
async def register_user(user: UserNew):
    """Registers a new user and saves to DB."""
    db = get_user_database()

    # Check if the user already exists
    if db["users"].find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hashing the password
    hashed_password = pwd_context.hash(user.password)

    # Saving the user to the database
    user_data = {
        "username": user.username,
        "email": user.email,
        "admin": user.admin,
        "hashed_password": hashed_password,  # Storing hashed password
    }
    db["users"].insert_one(user_data)

    return {"message": "User successfully registered, Login now!"}

@app.post("/login")
async def login(
    user: UserLogin,
    db: get_user_database = Depends(get_user_database),
):
    recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        "secret": "6LdnWpkqAAAAAN0QTrEdcGtLazAT3-SbGmpWhB6f",  
        "response": user.recaptcha_token
    }

    try:
        recaptcha_response = requests.post(recaptcha_url, data=payload, timeout=20)
        recaptcha_response.raise_for_status() # to raise exception when request fails
        recaptcha_result = recaptcha_response.json()

        # Log the response to help with debugging
        print(f"reCAPTCHA verification response: {recaptcha_result}")
        
        if not recaptcha_result.get("success"):
            raise HTTPException(status_code=400, detail="Invalid reCAPTCHA")
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error verifying reCAPTCHA: {str(e)}")

    # Authenticating user
    db_user = get_user(db, user.email)
    name = db_user.get("username")
    admin = db_user.get("admin")
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    #JWT token creation
    access_token = create_access_token(data={"sub": user.email,"username": name , "admin" : admin})
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "name" : name
    }

#Login&Register page----------------------------------------------------------------------------------------------------------------------------->>

# Home page-------------------------------------------------------------------------------------------------------------------------------------->>
@app.get('/acshipdata')
async def get_acdata(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format. Expected 'Bearer <token>'")

    token = authorization.split(" ")[1]  
    
    
    payload = decode_jwt_token(token)
    user_email = payload.get("sub")  
    if user_email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    del_update()
    db = get_shipment_database()
    
    cursor = db['shipment_info'].find(
        {"user_email" : user_email ,"active": True},  
        {"shipment_number": 1, "no_of_devices": 1, "source": 1, "destination": 1,
         "po_number": 1, "goods_type": 1, "exp_deliver_date": 1, "_id": 0}  
    )

    result = []
    for doc in cursor:
        result.append({
            "shipment_number": doc.get("shipment_number", ""),
            "no_of_devices": doc.get("no_of_devices", ""),
            "source": doc.get("source", ""),
            "destination": doc.get("destination", ""),
            "po_number": doc.get("po_number", ""),
            "goods_type": doc.get("goods_type", ""),
            "exp_deliver_date": doc.get("exp_deliver_date", "")
        })
    
    return result

# Home page-------------------------------------------------------------------------------------------------------------------------------------->>

#  create Shipment section----------------------------------------------------------------------------------------------------------------------->>


@app.post("/createshipment")
async def create_shipment(shipment: New_Shipment):
    db = get_shipment_database()
    payload = decode_jwt_token(shipment.user_email)
    user_email = payload.get("sub")

    if db["shipment_info"].find_one({"shipment_number" : shipment.shipment_number, "user_email" : user_email}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="shipment already exists")
    shipmentdata = {
        "shipment_number" : shipment.shipment_number ,
        "no_of_devices": shipment.no_of_devices,
        "destination" : shipment.destination ,
        "source" : shipment.source,
        "device_ids": shipment.device_ids,
        "po_number": shipment.po_number,
        "ndc_number": shipment.ndc_number,
        "shipping_comp" : shipment.shipping_comp,
        "del_number" : shipment.del_number,
        "serialno_goods" : shipment.serialno_goods,
        "container_no": shipment.container_no,
        "goods_type": shipment.goods_type,
        "dispatch_date" : shipment.dispatch_date,
        "exp_deliver_date" : shipment.exp_deliver_date,
        "batch_id" : shipment.batch_id,
        "shipment_description" : shipment.shipment_description,
        "status" : shipment.status,
        "active" : shipment.active,
        "user_email" : user_email
    }
    db["shipment_info"].insert_one(shipmentdata)
    return {"message: shipment successfully created"}

#  create Shipment section----------------------------------------------------------------------------------------------------------------------->>

# Myshipment Section----------------------------------------------------------------------------------------------------------------------------->>

@app.get("/allshipments")
async def get_all_shipments(authorization: str = Header(...)):
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format. Expected 'Bearer <token>'")

    token = authorization.split(" ")[1]  # Extract token part after "Bearer"
    
    
    payload = decode_jwt_token(token)
    user_email = payload.get("sub")  
    if user_email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
   
    db = get_shipment_database()
    collection = db["shipment_info"]
    
    try:
        # Fetching all documents associated with the user email
        shipments = list(collection.find({"user_email": user_email}))
        
        # Converting ObjectId to string for JSON serialization
        for shipment in shipments:
            shipment["_id"] = str(shipment["_id"])
        
        return {"message": "All shipments retrieved successfully!", "data": shipments}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Myshipment Section----------------------------------------------------------------------------------------------------------------------------->>

#Device data Stream section---------------------------------------------------------------------------------------------------------------------->>

@app.get("/getshipnums")
async def getshipNums():
    db = get_shipment_database()

    shipnumbers = list(db['shipment_info'].find({ }, {"shipment_number" : 1 , "_id" : 0}))

    return shipnumbers

@app.get("/getdeviceids")
async def getdeviceIds(shipnum: int):
    db = get_shipment_database()

    deviceIds = list(db['shipment_info'].find({'shipment_number' : shipnum} , {"device_ids" : 1, "_id" : 0}))
    print(deviceIds)
    return deviceIds

@app.get("/devdatastream")
async def get_devdatastream(
    shipment_number: str,
    device_id: str ):

    db = get_shipment_database()
    
    shipment = list(db["device_data_stream"].find({"shipnum": shipment_number, "deviceId": device_id},{"shipnum": 1, "deviceId": 1, "readings": 1, "_id": 0}))
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")


   
    # device_streams = list(db['Device Data Stream'].find(readings))
    # if not device_streams:
    #     raise HTTPException(status_code=404, detail="No data streams found for the devices")


    return shipment



#Device data Stream section---------------------------------------------------------------------------------------------------------------------->>

#Account page------------------------------------------------------------------------------------------------------------------------------------>>

@app.get("/userinfo")
def get_user_info(authorization: str = Header(...)):
    # Extract token from "Bearer <token>"
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.split(" ")[1]
    decoded_payload = decode_jwt_token(token)
    
    return {"username": decoded_payload.get("username"), "email": decoded_payload.get("sub")}


#Account page------------------------------------------------------------------------------------------------------------------------------------>>

#misc-------------------------------------------------------------------------------------------------------------------------------------------->>

@app.post("/protected")
def protected_route(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    token = authorization[7:]   
    if verify_token(token):
        return {"is_valid": True, "message": "Access granted"}
    else:
        return {"is_valid": False, "message": "Access denied"}
    

@app.get("/adminval")
def admin_val(authorization: str = Header(None)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.split(" ")[1]
    decoded = decode_jwt_token(token)
    admin = decoded.get("admin")
    print(f"Admin value: {admin}, Type: {type(admin)}")
    if "admin" not in decoded:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin claim missing in token"
        )
    if not decoded.get("admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an admin",
        ) 
    
    return admin
   
#misc-------------------------------------------------------------------------------------------------------------------------------------------->>
