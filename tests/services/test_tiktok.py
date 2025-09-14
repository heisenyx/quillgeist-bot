import pytest
import httpx
from urllib.parse import quote
from telegram import InputMediaPhoto, InputMediaVideo

from services.tiktok import process
from services.exceptions import VideoUnavailable

pytestmark = pytest.mark.asyncio

BASE_URL = "https://www.tiktok.com/t/some_video_id"
SAFE_URL = quote(BASE_URL)
API_URL = f"https://douyin.wtf/api/hybrid/video_data?url={SAFE_URL}"

MOCK_VIDEO_RESPONSE = {
    "data": {
        "content_type": "video",
        "video": {"play_addr": {"url_list": ["https://example.com/video.mp4"]}},
        "image_post_info": None,
    }
}

MOCK_MULTI_PHOTO_RESPONSE = {
    "data": {
        "content_type": "multi_photo",
        "video": None,
        "image_post_info": {
            "images": [
                {"display_image": {"url_list": ["https://example.com/img1.jpg"]}},
                {"display_image": {"url_list": ["https://example.com/img2.jpg"]}},
            ]
        },
    }
}

MOCK_LARGE_ALBUM_RESPONSE = {
    "data": {
        "content_type": "multi_photo",
        "image_post_info": {
            "images": [
                {"display_image": {"url_list": [f"https://example.com/img{i}.jpg"]}}
                for i in range(15)
            ]
        },
    }
}

async def test_process_valid_video_url(mocker):
    mock_request = httpx.Request("GET", API_URL)
    mock_response = httpx.Response(
        200,
        json=MOCK_VIDEO_RESPONSE,
        headers={"Content-Type": "application/json"},
        request=mock_request
    )
    mock_get = mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    result = await process(BASE_URL)

    assert result is not None
    assert len(result) == 1
    assert isinstance(result[0], InputMediaVideo)
    assert result[0].media == "https://example.com/video.mp4"
    mock_get.assert_called_once_with(API_URL, timeout=10)


async def test_process_valid_multi_photo_url(mocker):
    mock_request = httpx.Request("GET", API_URL)
    mock_response = httpx.Response(
        200,
        json=MOCK_MULTI_PHOTO_RESPONSE,
        headers={"Content-Type": "application/json"},
        request=mock_request
    )
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    result = await process(BASE_URL)

    assert result is not None
    assert len(result) == 2
    assert isinstance(result[0], InputMediaPhoto)
    assert isinstance(result[1], InputMediaPhoto)
    assert result[0].media == "https://example.com/img1.jpg"
    assert result[1].media == "https://example.com/img2.jpg"


async def test_process_multi_photo_url_limits_to_10_images(mocker):
    mock_request = httpx.Request("GET", API_URL)
    mock_response = httpx.Response(
        200,
        json=MOCK_LARGE_ALBUM_RESPONSE,
        headers={"Content-Type": "application/json"},
        request=mock_request
    )
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    result = await process(BASE_URL)

    assert result is not None
    assert len(result) == 10
    assert result[9].media == "https://example.com/img9.jpg"


async def test_process_deleted_url_raises_exception():
    deleted_url = "https://www.tiktok.com/t/deleted_video"
    with pytest.raises(VideoUnavailable, match="Video unavailable"):
        await process(deleted_url)


async def test_process_private_url_raises_exception():
    private_url = "https://www.tiktok.com/t/private_video"
    with pytest.raises(VideoUnavailable, match="Video unavailable"):
        await process(private_url)


async def test_process_http_request_error_returns_none(mocker):
    mocker.patch(
        "httpx.AsyncClient.get", side_effect=httpx.RequestError("Network error")
    )

    result = await process(BASE_URL)

    assert result is None


async def test_process_http_status_error_returns_none(mocker):
    mock_response = httpx.Response(404)
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    result = await process(BASE_URL)

    assert result is None


async def test_process_non_json_response_returns_none(mocker):
    mock_response = httpx.Response(
        200, text="<html><body>Error</body></html>", headers={"Content-Type": "text/html"}
    )
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    result = await process(BASE_URL)

    assert result is None


async def test_process_api_response_without_data_field_returns_none(mocker):
    mock_response = httpx.Response(
        200, json={"status": "error", "message": "No data found"}, headers={"Content-Type": "application/json"}
    )
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    result = await process(BASE_URL)

    assert result is None