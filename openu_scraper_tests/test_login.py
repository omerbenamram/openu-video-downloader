from pathlib import Path

import pytest
import yaml
from capybara.dsl import Page

from openu_scraper.webdriver import login_to_openu


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

def test_login(page: Page, username, password, nid):
    # will raise if login fails
    login_to_openu(page, username, password, nid)

