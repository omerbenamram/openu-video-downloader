from __future__ import unicode_literals, absolute_import

import re
import time
from enum import Enum
from typing import List
from urllib.error import URLError

import logbook
import m3u8 as m3u8
from bs4 import BeautifulSoup
from capybara.dsl import Page
from retry import retry
from selenium.common.exceptions import WebDriverException

from openu_scraper.constants import OPENU_VIDEO_COLLECTION_TEMPLATE
from .constants import LOG_PATH, OPENU_LOGIN_PAGE

logger = logbook.Logger(__name__)
logger.handlers.append(logbook.FileHandler(LOG_PATH, bubble=True))
logger.handlers.append(logbook.StderrHandler())


class JWPlayerStates(Enum):
    IDLE = 'IDLE'
    PLAYING = 'PLAYING'
    PAUSED = 'PAUSED'


def login_to_openu(page: Page, username, password, nid):
    logger.info(f'Connecting to artistworks with user {username}')

    page.visit(OPENU_LOGIN_PAGE)

    username_input = page.find('xpath', '//*[@id="p_user"]')
    username_input.send_keys(username)

    password_input = page.find('xpath', '//*[@id="p_sisma"]')
    password_input.send_keys(password)

    nid_input = page.find('xpath', '//*[@id="p_mis_student"]')
    nid_input.send_keys(nid)

    page.click_button('כניסה >')
    assert page.has_current_path('https://sheilta.apps.openu.ac.il/pls/dmyopt2/myop.myop_screen'), "Login Failed"


def get_lesson_by_id(self, lesson_id):
    logger.info(f'grabbing info for lesson {lesson_id}')
    if not self.driver.current_url == (ARTISTWORKS_LESSON_BASE + str(lesson_id)):
        self.driver.get(ARTISTWORKS_LESSON_BASE + str(lesson_id))

    lesson_name_element = self.driver.find_element_by_xpath('//*[@id="tabs-wrapper"]/h2')
    lesson_name = lesson_name_element.text
    elements = self._fetch_current_page_playlist_elements()

    lesson_links = self._handle_elements(elements, lesson_name=lesson_name)

    content = self.driver.page_source
    soup = BeautifulSoup(content)
    masterclasses_ids = list(map(lambda x: re.findall('\d+', x['href'])[0],
                                 soup.find_all('a', href=re.compile('/masterclass/(\d+)'))))

    if self.fetch_extras:
        logger.debug('Looking for pdf materials to download')
        pdf_links = map(lambda x: x['href'], soup.find_all('a', href=re.compile('.+\.pdf')))
        lesson_links.extend([LessonLink(link.split('/')[-1], link) for link in pdf_links])

    ret = Lesson(lesson_id, lesson_name, lesson_links, masterclasses_ids)
    self.last_lesson = ret
    return ret


def _get_all_jwplayer_instances(self):
    logger.debug('Discovering all instances of JWPlayer on page')
    ids = []
    player_exists = True
    player_id = 0
    while player_exists:
        jw = self.driver.execute_script(f"return jwplayer({player_id})")
        # empty objects are a dict with only registerPlugin
        if len(jw) > 1:
            ids.append(player_id)
            player_id += 1
        else:
            player_exists = False
    logger.debug(f'Found {len(ids)} instances')
    return ids


def _get_active_jwplayer_instance(self):
    logger.debug('checking all jwplayer state')
    players = self._get_all_jwplayer_instances()
    for player_id in players:
        state = self.driver.execute_script(f"return jwplayer({player_id}).getState()")
        logger.debug(f'state of player {player_id} is {state}')
        if not state == JWPlayerStates.IDLE.value:
            return player_id

    return None


def _get_video_link_for_element(self, element):
    logger.info('grabbing links for element {}'.format(element.text))
    element.click()
    # small sleep is still needed for some js to initialize
    i = 0
    link = None
    while i <= 3:
        try:
            time.sleep(5)
            active_player_id = self._get_active_jwplayer_instance() or 0
            link = self.driver.execute_script(
                f"return jwplayer({active_player_id}).getPlaylistItem()['file']")
            self.driver.execute_script(f"return jwplayer({active_player_id}).stop()")
        except WebDriverException as e:
            logger.exception(e)
            logger.debug('waiting and retrying')
            i += 1
        break
    if not link:
        raise Exception('Could not find link!')

    logger.info('found link {}'.format(link))
    return link


def _handle_elements(self, elements, lesson_name=None):
    lesson_links = []
    for element in elements:
        link = self._get_video_link_for_element(element)

        link_base_name = lesson_name if element.text.strip() == '' else element.text
        if link.endswith('m3u8'):
            logger.info('Got playlist instead of video, handling')
            video_parts = self._handle_playlist(link)
            if video_parts:
                for i, part in enumerate(video_parts):
                    lesson_links.append(LessonLink(link_base_name + '_part{}'.format(i), part))

        else:
            lesson_links.append(LessonLink(link_base_name, link))

    return lesson_links


@retry(URLError, tries=10, delay=5, logger=logger)
def _handle_playlist(playlist_link):
    playlist = m3u8.load(playlist_link)
    highest_quality_video = max(playlist.playlists, key=lambda p: p.stream_info.resolution[0])
    segments = m3u8.load(highest_quality_video.absolute_uri)
    videos = [segment.absolute_uri for segment in segments.segments]
    logger.info('resolved playlist {} into {} videos'.format(playlist_link, len(videos)))
    return videos


def get_all_video_ids_for_course(page: Page, collection_id: int):
    logger.info(f'Grabbing all links for video collection {collection_id}')
    page.visit(OPENU_VIDEO_COLLECTION_TEMPLATE.format(collection_id=collection_id))
    return extract_all_video_ids_from_source(BeautifulSoup(page.source), 'lxml')

def extract_all_video_ids_from_source(soup: BeautifulSoup) -> List[int]:
    lessons = soup.find_all('div', id=re.compile('playlist\d+'))
    return [int(re.match('playlist(\d+)', lesson['id']).groups()[0]) for lesson in lessons]
