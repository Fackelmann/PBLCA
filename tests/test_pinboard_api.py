import pytest # type: ignore
from pblca import pinboard_api

VALID_TOKEN = "Fackelmann:684F2A20A02C40B69970"
INVALID_TOKEN = "FAKE:NONE"


def test_pinboard_invalid_token() -> None:
    with pytest.raises(pinboard_api.APIInitializationException):
        pinboard_api.PinboardAPI(INVALID_TOKEN)


def test_get_all_posts() -> None:
    pb = pinboard_api.PinboardAPI(VALID_TOKEN)
    try:
        pb.get_all_posts()
    except pinboard_api.APIAccessException as e:
        raise(e)


def test_add_and_delete() -> None:
    post = {"url": "https://test_address.com",
            "description": "test bookmark"}
    pb = pinboard_api.PinboardAPI(VALID_TOKEN)
    params = {"url": "https://test_address.com"}
    response = pb.get_post(**params)["posts"]
    assert len(pb.get_post(**params)["posts"]) == 0
    pb.add_post(**post)
    response = pb.get_post(**params)["posts"]
    print(f"response: {response}")
    assert len(response) == 1
    assert response[0]["href"] == post["url"]
    assert response[0]["description"] == post["description"]
    pb.delete_post(**post)
    assert len(pb.get_post(**params)["posts"]) == 0
