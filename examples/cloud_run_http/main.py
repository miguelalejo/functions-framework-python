from typing import Union
from fastapi import FastAPI
from starlette.responses import StreamingResponse
from bson.objectid import ObjectId
from MongoService import *

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


async def fake_video_streamer(report_xls):
    yield report_xls

@app.get("/reportes/{item_id}")
def read_item(item_id: str):
    uri = "cluster0.2gzpcvj.mongodb.net/?retryWrites=true&w=majority"
    user = "m001-student"
    password = "m001-mongodb-basics"    
    mgConectorServ = MongoServiceConector(uri, user, password)
    objInstance = ObjectId(item_id)
    document = mgConectorServ.find_one(bd_name="edocuments",collecion="excel_dev_reports",query= {"_id":objInstance},projection={ "blob_excel": 1})
    report_xls = None
    if "blob_excel" in document.keys():
        report_xls = document["blob_excel"]
        print(type(report_xls))
        print(report_xls)
    print("Final")
    response = StreamingResponse(fake_video_streamer(report_xls), 
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response.headers["Content-Disposition"] = "attachment; filename={name}".format(name=item_id+".xlsx")
    return  response