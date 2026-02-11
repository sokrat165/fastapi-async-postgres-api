# header is used to get the value of the header from the request and use it in the function
from fastapi import FastAPI, Depends, Header

app = FastAPI()

async def common_header(x_token: str = Header(...)):
    return {"header_value": x_token}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_header)):
    return {
        "message": "Hello World",
        "header_value": commons["header_value"]
    }
