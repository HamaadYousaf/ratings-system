from fastapi import FastAPI, HTTPException
from mangum import Mangum
import boto3
from pydantic import BaseModel
import uuid


class ContentReq(BaseModel):
    title: str
    up: str
    down: str
    comment: str


class CommentReq(BaseModel):
    comment: str


app = FastAPI()
handler = Mangum(app)
client = boto3.client("dynamodb")


@app.get("/")
async def root():
    payload = {"title": "Pytest", "up": "5", "down": "5"}
    print(payload)
    return {"msg": "Hello World!"}


# Get all contents
@app.get("/content")
async def getAll():
    res = client.scan(TableName="contents")
    return {"data": res["Items"], "count": res["Count"]}


# Get content by content_id
@app.get("/content/{content_id}")
async def getContent(content_id: str):
    res = client.get_item(
        TableName="contents",
        Key={"content_id": {"S": content_id}},
        AttributesToGet=["content_id", "title", "up", "down", "comments"],
    )

    item = res.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail=f"Content {content_id} not found")

    return {"data": item}


# Create content
@app.post("/content")
async def addContent(content_req: ContentReq):
    content_id = str(uuid.uuid4())

    content = {
        "content_id": {"S": content_id},
        "title": {"S": content_req.title},
        "up": {"N": content_req.up},
        "down": {"N": content_req.down},
        "comments": {"SS": ["dummy"]},
    }
    res = client.put_item(TableName="contents", Item=content)

    return {"data": res, "id": content_id}


# Add comment to content by content_id
@app.put("/content/comment/{content_id}")
async def addComment(content_id: str, comment_req: CommentReq):
    res = client.update_item(
        TableName="contents",
        Key={"content_id": {"S": content_id}},
        UpdateExpression="ADD comments :element",
        ExpressionAttributeValues={":element": {"SS": [comment_req.comment]}},
    )

    return {"data": res}


# Add up votes to content by content_id
@app.put("/content/upvote/{content_id}")
async def addUpVote(content_id: str):
    res = client.update_item(
        TableName="contents",
        Key={"content_id": {"S": content_id}},
        ExpressionAttributeValues={":inc": {"N": "1"}},
        UpdateExpression="ADD up :inc",
    )

    return {"data": res}


# Add down votes to content by content_id
@app.put("/content/downvote/{content_id}")
async def addDownVote(content_id: str):
    res = client.update_item(
        TableName="contents",
        Key={"content_id": {"S": content_id}},
        ExpressionAttributeValues={":inc": {"N": "1"}},
        UpdateExpression="ADD down :inc",
    )

    return {"data": res}


# Delete content by content_id
@app.delete("/content/{content_id}")
async def delContent(content_id: str):
    res = client.delete_item(
        TableName="contents",
        Key={"content_id": {"S": content_id}},
    )

    return {"data": res}
