from pydantic import BaseModel, Field
from typing import Annotated, List


class New_Shipment(BaseModel):
    shipment_number : int
    no_of_devices: int
    destination : str
    source : str
    device_ids: List[int]
    po_number: int
    ndc_number: int
    shipping_comp : str
    del_number : int
    serialno_goods : int
    container_no: int
    goods_type: str
    dispatch_date : str
    exp_deliver_date : str
    batch_id : int
    shipment_description : str
    status : str
    active : bool
    user_email : str



class UserNew(BaseModel):
    username: str
    email: str
    admin : bool
    password: str
    
class UserLogin(BaseModel):
    email :str
    password :str
    recaptcha_token: str


class readings(BaseModel):
    battery_level : str
    sensor_temp : str
    source : str
    destination : str
    timestamp : str

class devicedatastream(BaseModel):
    shipnum : str
    deviceId : str
    readings : List[readings]
    