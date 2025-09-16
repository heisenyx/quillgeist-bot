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


@pytest.fixture
def mock_ig_client(mocker):
    mock_client_instance = MagicMock()
    mocker.patch('services.instagram.ig_client', new=mock_client_instance)
    return mock_client_instance

async def test_process_single_photo(mock_ig_client):
    mock_media_info = create_mock_media(1, "https://example.com/photo.jpg")
    mock_ig_client.media_pk_from_url.return_value = MEDIA_ID
    mock_ig_client.media_info_v1.return_value = mock_media_info

    result = await process(BASE_URL)

    assert result is not None
    assert len(result) == 1
    assert isinstance(result[0], InputMediaPhoto)
    assert result[0].media == "https://example.com/photo.jpg"
    mock_ig_client.media_pk_from_url.assert_called_once_with(BASE_URL)
    mock_ig_client.media_info_v1.assert_called_once_with(MEDIA_ID)


async def test_process_single_video(mock_ig_client):
    mock_media_info = create_mock_media(2, "https://example.com/video.mp4")
    mock_ig_client.media_pk_from_url.return_value = MEDIA_ID
    mock_ig_client.media_info_v1.return_value = mock_media_info

    result = await process(BASE_URL)

    assert result is not None
    assert len(result) == 1
    assert isinstance(result[0], InputMediaVideo)
    assert result[0].media == "https://example.com/video.mp4"


async def test_process_album_with_mixed_media(mock_ig_client):
    mock_album_info = MagicMock()
    mock_album_info.media_type = 8
    mock_album_info.resources = [
        create_mock_media(1, "https://example.com/photo1.jpg"),
        create_mock_media(2, "https://example.com/video1.mp4"),
    ]
    mock_ig_client.media_pk_from_url.return_value = MEDIA_ID
    mock_ig_client.media_info_v1.return_value = mock_album_info

    result = await process(BASE_URL)

    assert result is not None
    assert len(result) == 2
    assert isinstance(result[0], InputMediaPhoto)
    assert isinstance(result[1], InputMediaVideo)


async def test_process_resolves_share_link(mock_ig_client, mocker):
    mock_http_response = MagicMock()
    mock_http_response.url = RESOLVED_URL
    mock_get = mocker.patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_http_response)

    mock_media_info = create_mock_media(2, "https://example.com/video.mp4")
    mock_ig_client.media_pk_from_url.return_value = MEDIA_ID
    mock_ig_client.media_info_v1.return_value = mock_media_info

    result = await process(SHARE_URL)

    assert result is not None
    mock_get.assert_called_once_with(SHARE_URL, timeout=5)
    mock_ig_client.media_pk_from_url.assert_called_once_with(RESOLVED_URL)


async def test_process_media_not_found_returns_none(mock_ig_client):
    mock_ig_client.media_pk_from_url.side_effect = MediaNotFound("Media not found")

    result = await process(BASE_URL)

    assert result is None


async def test_process_uninitialized_client_returns_none(mocker):
    mocker.patch('services.instagram.ig_client', new=None)

    result = await process(BASE_URL)

    assert result is None