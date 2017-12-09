from pathlib import Path

import pytest
import yaml
from capybara.dsl import Page
from capybara.node.element import Element
from selenium.common.exceptions import StaleElementReferenceException

from openu_scraper.artistworks_downloader.webdriver import login_to_openu

@pytest.fixture
def creds():
    yml = yaml.load(Path('./creds.yml').read_text())
    return yml['credentials']

@pytest.fixture
def username(creds):
    return creds['username']

@pytest.fixture
def password(creds):
    return creds['password']

@pytest.fixture
def nid(creds):
    return creds['nid']

def test_login():
    login_to_openu()
