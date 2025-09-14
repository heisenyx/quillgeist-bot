import pytest
from unittest.mock import MagicMock, AsyncMock
from telegram import InputMediaPhoto, InputMediaVideo
from instagrapi.exceptions import MediaNotFound

from services.instagram import process

pytestmark = pytest.mark.asyncio

BASE_URL = "https://www.instagram.com/p/qwe123/"
SHARE_URL = "https://www.instagram.com/share/qwe123/"
RESOLVED_URL = "https://www.instagram.com/reel/qwe123/"
MEDIA_ID = "1234567890123456789"

def create_mock_media(media_type, url):
    mock = MagicMock()
    mock.media_type = media_type
    if media_type == 1:
        mock.thumbnail_url = url
    else:
        mock.video_url = url
    return mock

def setup_mock_client(mocker, media_info):
    mock_client = MagicMock()
    mock_client.media_pk_from_url.return_value = MEDIA_ID
    mock_client.media_info_v1.return_value = media_info
    mocker.patch("services.instagram.get_client", return_value=mock_client)
    return mock_client

async def test_process_single_photo(mocker):
    mock_media_info = create_mock_media(1, "https://example.com/photo.jpg")
    setup_mock_client(mocker, mock_media_info)

    result = await process(BASE_URL)

    assert result is not None
    assert len(result) == 1
    assert isinstance(result[0], InputMediaPhoto)
    assert result[0].media == "https://example.com/photo.jpg"

async def test_process_single_video(mocker):
    mock_media_info = create_mock_media(2, "https://example.com/video.mp4")
    setup_mock_client(mocker, mock_media_info)

    result = await process(BASE_URL)

    assert result is not None
    assert len(result) == 1
    assert isinstance(result[0], InputMediaVideo)
    assert result[0].media == "https://example.com/video.mp4"

async def test_process_album_with_mixed_media(mocker):
    mock_album_info = MagicMock()
    mock_album_info.media_type = 8  # Album type
    mock_album_info.resources = [
        create_mock_media(1, "https://example.com/photo1.jpg"),
        create_mock_media(2, "https://example.com/video1.mp4"),
        create_mock_media(1, "https://example.com/photo2.jpg"),
    ]
    setup_mock_client(mocker, mock_album_info)

    result = await process(BASE_URL)

    assert result is not None
    assert len(result) == 3
    assert isinstance(result[0], InputMediaPhoto)
    assert isinstance(result[1], InputMediaVideo)
    assert isinstance(result[2], InputMediaPhoto)
    assert result[1].media == "https://example.com/video1.mp4"

async def test_process_album_limits_to_10_items(mocker):
    mock_album_info = MagicMock()
    mock_album_info.media_type = 8
    mock_album_info.resources = [
        create_mock_media(1, f"https://example.com/photo{i}.jpg") for i in range(12)
    ]
    setup_mock_client(mocker, mock_album_info)

    result = await process(BASE_URL)

    assert result is not None
    assert len(result) == 10
    assert result[9].media == "https://example.com/photo9.jpg"

async def test_process_resolves_share_link(mocker):
    mock_http_response = MagicMock()
    mock_http_response.url = RESOLVED_URL
    mock_get = mocker.patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_http_response)

    mock_media_info = create_mock_media(2, "https://example.com/video.mp4")
    mock_client = setup_mock_client(mocker, mock_media_info)

    result = await process(SHARE_URL)

    assert result is not None
    assert len(result) == 1
    mock_get.assert_called_once_with(SHARE_URL, timeout=5)
    mock_client.media_pk_from_url.assert_called_once_with(RESOLVED_URL)

async def test_process_media_not_found_returns_none(mocker):
    mock_client = MagicMock()
    mock_client.media_pk_from_url.side_effect = MediaNotFound("Media not found")
    mocker.patch("services.instagram.get_client", return_value=mock_client)

    result = await process(BASE_URL)

    assert result is None

async def test_process_unexpected_error_returns_none(mocker):
    mock_client = MagicMock()
    mock_client.media_pk_from_url.side_effect = Exception("A generic error occurred")
    mocker.patch("services.instagram.get_client", return_value=mock_client)

    result = await process(BASE_URL)

    assert result is None