import pytest
from bs4 import BeautifulSoup

from pathlib import Path

from openu_scraper.webdriver import extract_all_video_ids_from_source


@pytest.fixture
def video_library_page() -> BeautifulSoup:
    return BeautifulSoup(Path(__file__).parent.joinpath('fixtures', 'course_video_page.html').read_text(), 'lxml')


def test_correctly_extract_video_ids(video_library_page):
    assert extract_all_video_ids_from_source(video_library_page) == [313075, 312775, 312509, 312157, 311637, 311083,
                                                                     310491, 309833]
