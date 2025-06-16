from fastapi import FastAPI, Path, HTTPException, Query
from pydantic import BaseModel , Field, computed_field
from typing import Annotated, Literal, Optional
import json
from fastapi.responses import JSONResponse

app = FastAPI()


class Patient(BaseModel):
    id : Annotated[str, Field(...,description="Id of the patient", examples=['P001'] )]
    name : Annotated[str, Field(...,description="name of the patient")]
    city : Annotated[str, Field(...,description="patient city ")]
    age : Annotated[int, Field(...,gt=0, lt=120, description="Age of the patient")] 
    gender : Annotated[Literal['male','female', 'other'], Field(...,description="Gender of the patient ")]
    height : Annotated[float,Field(...,gt=0, description="height of the patient in mtrs  ") ]
    weight : Annotated[float,Field(...,gt=0, description="weight of the patient in kgs ") ]
                       
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'underWeight'
        elif self.bmi < 25 :
            return "Normal"
        elif self.bmi < 30 :
            return "boader line"
        else:
            return "obese"


class PatientUpdate(BaseModel):

    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male','female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]
    ##note id is removed beacause is path parameter 


# from fastapi import path , inside this path we can use for clear read ablity 
def load_data():
    with open(r"C:\Users\hp\Desktop\Fast_api\patients.json",'r') as f:
        data= json.load(f)
    return data 

def save_data(data):
    with open(r'C:\Users\hp\Desktop\Fast_api\patients.json','w') as f:
        json.dump(data,f)

@app.get('/')
def patient_Api():
    return{'message':'Patient details and history checkup tool'}


@app.get('/about')
def about():
    return{'message':' A fully functional api to manage your patient record'}


## retriver works 
@app.get("/view")
def view():
    data =load_data()
    return data 
## NOte suppose we want to see only 3 patient information
## so how for example localhost:8000/view/<3> 
#here 3 is dyanmic we can change localhost:8000/view/1 
# so for handling dynnamic segments of URL we us ****path params***

### path params are dynamic segments of a url path used to identify a specific resource 
## ****localhost:8000/view/{3}**** 



## but http request follow 200, 404, 201, 
# for this we require ****HTTPException****

@app.get('/patient/{patient_id}')
# ... means is required parameter ##readablity esay way 
def view_patient(patient_id: str = Path(...,description ='Id of the patient in the DB', examples= ['P001'])):  
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    return HTTPException(status_code= 404, detail = "patient not found ")


### uvicorn main1:app --reload
### netstat -aon | findstr :8000
### taskkill /PID 11432 /F
### since you closed the terminal without stopping the server, the Uvicorn process is still running in the background, keeping the port busy (probably port 8000).



"""

**Query Parameter after end point , send (key value pair) multip query by & 
in the view section the can use sorted order base on height , weigtg , naming order 
## sortbt ,order desc, asec else default 

for eg /patients?city _delhi & sort_by = age 
"""

@app.get('/sort')
def sort_patients(sort_by :str = Query(...,description='Sort on the basis of height, weight, bmi'), order :str =Query('asc',description='sort in asc, desc order')): ## ... means required , asc =default 

    Valid_fields =['height','weight','bmi']

    if sort_by not in Valid_fields:
        raise HTTPException(status_code=400, detail= f"invalid field select from {Valid_fields}")
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail= "invalid field select from asc and desc")
    
    data = load_data()
    # sorted_data =  sorted(my_dict.values(), keys= lambda x: x.get('height',0), reverse=True)

    sort_order= True if order =='desc' else False
    sorted_data =  sorted(data.values(), key= lambda x: x.get(sort_by, 0 ), reverse=sort_order)

    return sorted_data

        

### create end point (user can add data inside 
### before this we required pydantic please watch before move here )

# end point is post and route is create     
@app.post('/create')
def create_patient(patient:Patient):
     ## dataype is Patient (send to pydantic for validation 
    # load existing data
    data = load_data()

    # check if the paitent already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient is already exists')
    # add new patient to the database
    # adding pydantic data in existing data (json etc)
    # convert pydantic to dictionary 
    data[patient.id] = patient.model_dump(exclude=['id'])
    #bmi and verdict is not presnt but pydantic esay to handle by calculating 

    # save into json 
    # for this we create utilty finction
    save_data(data)

    return JSONResponse(status_code=201, content={'message':'patient create successfully'})


### for update : put method 
## 1 new pydantic model previous  class patient 
## 2 new data update in existing data 

## new pydantic class : PatientUpdate 

@app.put('/edit/{patient_id}') ## patient_id is path parameter
def update_patient(patient_id: str, patient_update:PatientUpdate):
    data =load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found ')
    
    existing_patient_info = data[patient_id]

    update_patient_info = patient_update.model_dump(exclude_unset=True) 
    # why exclude_unset if i don't want to update all field 
    # only field which required 

    for key, value in update_patient_info.items():
        existing_patient_info[key]= value

    ## but when we update weight, then bmi anf verdict also change 
    ## existing_patient_info -> pydantic object -> updated bmi and verdict
    existing_patient_info['id'] =patient_id
    patient_pydantic_obj= Patient(**existing_patient_info)
    ## -> pydantic object -> dict -> data[patient_id] = existing_patient_info
    existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')

    # add this dict to data 
    data[patient_id] = existing_patient_info

    # save data 
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id : str):
    
    data= load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200,content={'message':'patient_deleted '})


