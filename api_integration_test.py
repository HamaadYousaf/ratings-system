import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
URL = config["LAMBDA_URL"]


def test_can_get_all_content():
    response = get_all_content()
    count = response.json()["count"]
    assert count > 1


def test_post_put_del():
    create_response = create_content().json()
    assert create_response["data"]["ResponseMetadata"]["HTTPStatusCode"] == 200

    test_id = create_response["id"]
    get_response = get_content_by_id(test_id)
    assert get_response.status_code == 200
    assert get_response.json()["data"]["title"]["S"] == "Pytest"

    comment_response = add_comment(test_id).json()
    assert comment_response["data"]["ResponseMetadata"]["HTTPStatusCode"] == 200

    upvote_response = add_upvote(test_id).json()
    assert upvote_response["data"]["ResponseMetadata"]["HTTPStatusCode"] == 200

    downvote_response = add_downvote(test_id).json()
    assert downvote_response["data"]["ResponseMetadata"]["HTTPStatusCode"] == 200

    get_response = get_content_by_id(test_id)
    assert get_response.status_code == 200
    assert len(get_response.json()["data"]["comments"]["SS"]) > 1
    assert get_response.json()["data"]["up"]["N"] == "6"
    assert get_response.json()["data"]["down"]["N"] == "6"

    delete_response = del_content(test_id)
    assert delete_response.status_code == 200

    get_response = get_content_by_id(test_id)
    assert get_response.status_code == 404


def get_all_content():
    return requests.get(f"{URL}/content")


def get_content_by_id(content_id: str):
    return requests.get(f"{URL}/content/{content_id}")


def create_content():
    payload = {"title": "Pytest", "up": "5", "down": "5", "comment": "string"}
    return requests.post(f"{URL}/content", json=payload)


def add_comment(test_id):
    payload = {"comment": "Pytest"}
    return requests.put(f"{URL}/content/comment/{test_id}", json=payload)


def add_upvote(test_id):
    return requests.put(f"{URL}/content/upvote/{test_id}")


def add_downvote(test_id):
    return requests.put(f"{URL}/content/downvote/{test_id}")


def del_content(test_id):
    return requests.delete(f"{URL}/content/{test_id}")
