from __future__ import unicode_literals, absolute_import

import contextlib
import os
import asyncio
from pathlib import Path
import re

import aiohttp
import logbook

from .constants import MAX_CONCURRENT_DOWNLOADS, LOG_PATH, MAX_RETRIES, RETRY_DURATION

logger = logbook.Logger(__name__)
logger.handlers.append(logbook.FileHandler(LOG_PATH, bubble=True, level=logbook.DEBUG))
logger.handlers.append(logbook.StderrHandler())


async def remove_partial_file(file_path):
    yield
    os.remove(file_path)


class AsyncDownloader(object):
    def __init__(self, loop=asyncio.get_event_loop()):
        self.loop = loop
        self.busy = set()
        self.done = {}
        self.tasks = set()

        self.sem = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)


    async def async_download_video(self, video_url, chunk_size=1024, folder=r'C:\Temp', filename='', retry_count=0):
        if retry_count > 0:
            logger.info('going to retry {} for the {} time'.format(video_url, retry_count + 1))

        with aiohttp.ClientSession(loop=self.loop) as session, (await self.sem):
            try:
                vid = await session.get(video_url)
                if not filename:
                    filename = video_url.split('/')[-1]
            except Exception:

                logger.error(f'Error trying to read url {video_url}')
                if retry_count >= MAX_RETRIES:
                    logger.exception('Max retries reached, exiting!')
                    raise

                logger.error(f'Failure trying to download from {video_url}, going to retry later..')
                logger.debug(f'sleeping for {RETRY_DURATION}')
                await asyncio.sleep(RETRY_DURATION)
                task = asyncio.Task(self.async_download_video(video_url=video_url,
                                                              folder=str(folder),
                                                              filename=filename,
                                                              retry_count=retry_count+1))
                task.add_done_callback(self.tasks.remove)
                self.tasks.add(task)
                self.sem.release()
                return

            with open(os.path.join(folder, filename), 'wb') as fd, contextlib.closing(vid):
                while True:
                    try:
                        chunk = await vid.content.read(chunk_size)
                    except Exception:

                        logger.error('Error in midst of reading from stream {}'.format(video_url))
                        if retry_count >= MAX_RETRIES:
                            logger.exception('Max retries reached, exiting!')
                            raise

                        logger.error(f'Failure trying to download from {video_url}, going to retry later..')
                        logger.debug(f'sleeping for {RETRY_DURATION}')
                        await asyncio.sleep(RETRY_DURATION)
                        task = asyncio.Task(self.async_download_video(video_url=video_url,
                                                                      folder=str(folder),
                                                                      filename=filename))
                        task.add_done_callback(self.tasks.remove)
                        self.tasks.add(task)
                        self.loop.create_task(remove_partial_file(os.path.join(folder, filename)))
                        self.sem.release()
                        return

                    if not chunk:
                        break
                    fd.write(chunk)

        logger.info(f'Finished downloading file {filename}')
        self.done[video_url] = True

    def download_link(self, link, output_folder_path):
        if not isinstance(output_folder_path, Path):
            output_folder_path = Path(output_folder_path)

        if not output_folder_path.exists():
            os.makedirs(str(output_folder_path))

        ext = link.link.split('.')[-1]
        filename = get_valid_filename(link.name) + '.{}'.format(ext)

        if output_folder_path.joinpath(filename).exists():
            logger.debug(f'file {filename} exists in disk, not downloading')
            return None

        logger.debug(f'going to download {filename} to folder {str(output_folder_path)}')
        task = asyncio.Task(self.async_download_video(video_url=link.link,
                                                      folder=str(output_folder_path),
                                                      filename=filename))
        task.add_done_callback(self.tasks.remove)
        self.tasks.add(task)

    def run(self):
        if self.tasks:
            self.loop.run_until_complete(asyncio.wait(self.tasks))
        return


def get_valid_filename(s):
    """
    Returns the given string converted to a string that can be used for a clean
    filename. Specifically, leading and trailing spaces are removed; other
    spaces are converted to underscores; and anything that is not a unicode
    alphanumeric, dash, underscore, or dot, is removed.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = s.strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)
