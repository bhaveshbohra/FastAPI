from fastapi import FastAPI


app = FastAPI() # create object which is object of fastapi 

# for end point we defind route @
# get signify that ki hamara jo request aayega vo e k get api hoga , simple fetching data get , send that from serve uss post
@app.get("/")  # /path suppose someone hit futuergo/ the come here  
def hello():   ## method 
    return {'message': 'hello world' }

## to run this we use /take help from unicorn 
# unicorn main:app --reload 

@app.get('/about') # one another end point when some hit about section 
def about():
    return{'message': "Futergo is platform where you can see the daily stock news "}

## so basic we defind route for each end point and defind method for each route 

#CRUD
## profile se kuch maanh rahe ho http :- verb :- Get (retrive)
##form fill karke website par bhej rahe ho http :- verb :- post (Create)
## update some thing  http : verb -  put ( update)
## http -0verb -delete 
