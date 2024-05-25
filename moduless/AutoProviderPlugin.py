from aplustools.web.webtools import Search
from aplustools.utils.imagetools import OnlineImage, OfflineImage
save_image = OnlineImage.save_image
convert_image_format = OnlineImage.convert_image_format
download_image = OnlineImage.download_image
download_logo_image = OnlineImage.download_logo_image
from aplustools.web.webtools import check_url, is_crawlable
import os
#import requests
from bs4 import BeautifulSoup
import urllib3
from abc import ABC, abstractmethod
from PIL import Image
from typing import Optional#, Union
from urllib.parse import urljoin#, urlparse
#from urllib.parse import urlencode, urlunparse, quote_plus
#from urllib.request import urlopen, Request
import threading
from queue import Queue
import time
from requests.sessions import Session
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import unicodedata

# Disable only the specific InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AutoProviderPlugin(ABC):
    def __init__(self, title: str, chapter: int, chapter_rate: float, data_folder: str, cache_folder: str, provider: str, specific_provider_website: str, logo_path: str):
        self.title = title
        self.url_title = self.urlify(title)
        self.chap(chapter)
        self.chapter_rate = chapter_rate
        self.data_folder = data_folder
        self.cache_folder = cache_folder
        self.provider = provider
        self.specific_provider_website = specific_provider_website
        self.logo_path = logo_path
        self.blacklisted_websites = [
            "247manga.com",
            "ww6.mangakakalot.tv",
            "jimanga.com",
            "mangapure.net",
            "mangareader.mobi",
            "onepiece.fandom.com"
        ]
        self.current_url = None
        self.image_queue = Queue()
        self.total_images = 0
        self.download_progress_queue = Queue()
        self.process_progress_queue = Queue()
        self.session = Session()  # Create a session for connection pooling

    @staticmethod
    def urlify(to_url: str):
        url = unicodedata.normalize('NFKD', to_url)
        url = url.encode('ascii', 'ignore').decode('ascii')
        url = re.sub(r"[^a-zA-Z0-9\s_-]", "", url)  # title = re.sub(r"[^a-zA-Z0-9_-]", "", title)
        return url.strip()

    def get_logo_path(self):
        return self.logo_path
        
    def set_title(self, new_title):
        self.title = new_title
        
    def get_title(self):
        return self.title

    def set_chapter(self, new_chapter):
        self.chapter = new_chapter
        self.chap()
        
    def get_chapter(self):
        self.chap()
        return self.chapter
        
    def set_chapter_rate(self, new_chapter_rate):
        self.chapter_rate = new_chapter_rate
        
    def get_chapter_rate(self):
        return self.chapter_rate

    def set_provider(self, new_provider):
        self.provider = new_provider
        
    def get_provider(self):
        return self.provider
        
    def set_current_url(self, new_current_url):
        self.current_url = new_current_url
        
    def get_current_url(self):
        return self.current_url
        
    def set_blacklisted_websites(self, new_blacklisted_websites):
        self.blacklisted_websites = new_blacklisted_websites
        
    def get_blacklisted_websites(self):
        return self.blacklisted_websites
        
    def chap(self, chapter=None):
        if chapter is not None:
            self.chapter = int(chapter) if float(chapter).is_integer() else chapter
            self.chapter_str = str(self.chapter).replace(".", "-")
        else:
            self.chapter = int(self.chapter) if float(self.chapter).is_integer() else self.chapter
            self.chapter_str = str(self.chapter).replace(".", "-")

    def next_chapter(self, progress_queue=None):
        self.chapter += self.chapter_rate
        self.chap()
        if self.update_current_url():
            return self._handle_cache_result(self.cache_current_chapter(), progress_queue)
        else:
            if progress_queue:
                progress_queue.put(0)
            return False

    def previous_chapter(self, progress_queue=None):
        self.chapter -= self.chapter_rate
        self.chap()
        if self.update_current_url():
            return self._handle_cache_result(self.cache_current_chapter(), progress_queue)
        else:
            if progress_queue:
                progress_queue.put(0)
            return False

    def reload_chapter(self, progress_queue=None):
        self.chap()
        if self.update_current_url():
            return self._handle_cache_result(self.cache_current_chapter(), progress_queue)
        else:
            if progress_queue:
                progress_queue.put(0)
            return False

    def _handle_cache_result(self, cache_gen, progress_queue):
        final_result = None
        for progress_or_result in cache_gen:
            #print("Handle cache result got: ", progress_or_result) # Debug
            if isinstance(progress_or_result, bool):  # Check if it's the final result
                final_result = progress_or_result
            else:
                if progress_queue:
                    progress_queue.put(progress_or_result)  # Put the progress into the queue
                else:
                    continue  # If no progress_queue is provided, just continue to the next iteration
        print("Handle cache result done, returning now ...")
        return final_result
            
    def _download_logo_image(self, img_url: str, new_name: str, img_format: str, img_type: Optional[str]=None):
        image = OnlineImage(img_url)
        if img_type is None:
            download_logo_image(img_url, new_name, img_format)
        elif img_type.lower() == "url":
            image.download_image(self.data_folder, img_url, new_name, img_format)
        elif img_type.lower() == "base64":
            image.base64(self.data_folder, new_name, img_format, img_url) # Moved data to the back to avoid using keyword arguments
        
    def redo_prep(self):
        self._empty_cache()
        image = Image.open(f"{self.data_folder}empty.png")
        image.save(f"{self.cache_folder}empty.png")

    def update_current_url(self):
        print("Updating current URL...")
        self.current_url = self._get_current_chapter_url()
        if self.current_url:
            print(f"Current URL set to: {self.current_url}")
            return True
        else:
            print("Failed to update current URL.")
            return False
        
    def _get_current_chapter_url(self):
        provider_function = {
            "google": self._google_provider,
            "duckduckgo": self._duckduckgo_provider,
            "bing": self._bing_provider,
            "indirect": self._indirect_provider,
            "direct": self._direct_provider
        }.get(self.provider.lower())

        if provider_function:
            return provider_function()
        else:
            print(f"Provider {self.provider} not supported.")
            return None
            
    def _get_url(self, url, title):
        return check_url(url, title, [self.title, str(self.chapter)])
        
    def _google_provider(self):
        queries = [
            f'manga "{self.title}" "chapter {self.chapter}" site:{self.specific_provider_website}',
            f'manga "{self.title}" chapter {self.chapter} site:{self.specific_provider_website}',
            f'manga {self.title} chapter {self.chapter} site:{self.specific_provider_website}',
            f'manga {self.title} site:{self.specific_provider_website}',
            f'manga site:{self.specific_provider_website}'
        ]
        search = Search()
        return search.google_provider(queries)
        
    def _duckduckgo_provider(self):
        queries = [
            f'manga "{self.title}" "chapter {self.chapter}" site:{self.specific_provider_website}',
            f'manga "{self.title}" chapter {self.chapter} site:{self.specific_provider_website}',
            f'manga {self.title} chapter {self.chapter} site:{self.specific_provider_website}',
            f'manga {self.title} site:{self.specific_provider_website}',
            f'manga site:{self.specific_provider_website}'
        ]
        search = Search()
        return search.duckduckgo_provider(queries)
        
    def _bing_provider(self):
        queries = [
            f'manga "{self.title}" "chapter {self.chapter}" site:{self.specific_provider_website}',
            f'manga "{self.title}" chapter {self.chapter} site:{self.specific_provider_website}',
            f'manga {self.title} chapter {self.chapter} site:{self.specific_provider_website}',
            f'manga {self.title} site:{self.specific_provider_website}',
            f'manga site:{self.specific_provider_website}'
        ]
        search = Search()
        return Search.bing_provider(queries)
                
    @abstractmethod
    def _indirect_provider(self): # Can't be generalized, you need to overwrite this
        return None
    
    @abstractmethod
    def _direct_provider(self): # Can't be generalized, you need to overwrite this
        return None
            
    def _empty_cache(self):
        files = os.listdir(self.cache_folder)
        for f in files:
            os.remove(f"{self.cache_folder}{f}")

    def _download_image(self, img_tag):
        image = OnlineImage(urljoin(self.current_url, img_tag['src']))
        image.download_image(self.cache_folder)
        return img_tag['src'].split("/")[-1]
            
    def download_images(self):
        try:
            response = self.session.get(self.current_url)  # Use the session for connection pooling
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tags = soup.find_all('img')
            self.total_images = len(img_tags)
            
            count = 0
            # Concurrent downloading of images
            with ThreadPoolExecutor(max_workers=10) as executor:
                # Start the load operations and mark each future with its URL
                future_to_img = {executor.submit(self._download_image, img_tag): img_tag for img_tag in img_tags}
            
                for future in as_completed(future_to_img):
                    img_tag = future_to_img[future]
                    try:
                        image_name = future.result()  # This retrieves the result of the function (or raises the exception it threw)
                        count += 1
                        progress = int((count) / self.total_images * 100)
                        #print(f"Putting progress value of {progress} from download_images at iteration {i}") # Debug
                        self.download_progress_queue.put(progress)
                        #print("Put", image_name, "into queue.") # Debug
                        self.image_queue.put(image_name)
                        #print(f"Downloaded image: {image_name}")
                    except Exception as exc:
                        print(f"{img_tag} generated an exception: {exc}")
            self.image_queue.put(True)
            print(f"{len(img_tags)} images downloaded!")
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        return True
    
    def validate_image(self, image):
        if image.split('.')[0].isdigit():
            f_lst = image.split(".")
            file_name = f_lst[0]
            file_extension = f_lst[-1]
            new_name = file_name.zfill(3)
            return file_name, file_extension, new_name
        else: return None, None, None

    def process_images(self):
        count = 0
        async_results = []

        def callback(result):
            nonlocal count
            print(f'Renamed a file.')
            count += 1
            progress = int((count) / self.total_images * 100)
            #print(f"Putting progress value of {progress} from process_images at count {count}") # Debug
            self.process_progress_queue.put(progress)

        try:
            with Pool(processes=4) as pool:
                while True:
                    if not self.image_queue.empty():
                        image = self.image_queue.get()
                        if image == True: break
                        #print("Got", image, "from queue.") # Debug
                        count += 1
                        file_name, file_extension, new_name = self.validate_image(image)
                        if None in [file_name, file_extension, new_name]:
                            #print("Didn't validate", image) # Debug
                            continue
                        #else: print("Validated", image) # Debug

                        # Call apply_async and append the result to our results list
                        args = ('', self.cache_folder, file_name, file_extension, new_name, "png")
                        async_result = pool.apply_async(convert_image_format, args, callback=callback)
                        async_results.append(async_result)

                # Wait for all asynchronous results to complete
                for async_result in async_results:
                    async_result.get()

            return True
        except Exception as e:
            print(f"Error occurred: {e}")
            return False

    def cache_current_chapter(self):
        if not self.current_url:
            print("URL nor found.")
            yield 0
            return False
        if not is_crawlable(self.current_url):
            print("URL not crawlable as per robots.txt.")
            yield 0
            return False
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)
        self._empty_cache()
        
        download_result_queue = Queue()
        process_result_queue = Queue()
        download_thread = threading.Thread(target=lambda q=download_result_queue: q.put(self.download_images()))
        process_thread = threading.Thread(target=lambda q=process_result_queue: q.put(self.process_images()))
        download_thread.start()
        process_thread.start()

        current_download_progress = 0
        current_process_progress = 0
        combined_progress = 0

        yield 0

        while True:
            if not download_thread.is_alive() and not process_thread.is_alive() and (self.download_progress_queue.empty() and self.process_progress_queue.empty()):
                break
            #print("Download Thread alive: " + str(download_thread.is_alive()), "Process Thread alive: " + str(process_thread.is_alive())) # Debug

            # Handle download progress
            if not self.download_progress_queue.empty():
                new_download_progress = self.download_progress_queue.get()
                progress_diff = new_download_progress - current_download_progress
                combined_progress += progress_diff
                current_download_progress = new_download_progress
    
            # Handle process progress
            if not self.process_progress_queue.empty():
                new_process_progress = self.process_progress_queue.get()
                progress_diff = new_process_progress - current_process_progress
                combined_progress += progress_diff
                current_process_progress = new_process_progress
    
            yield combined_progress // 2
            time.sleep(0.1)
        
        download_result = download_result_queue.get()
        process_result = process_result_queue.get()

        print("Cache current chapter done, returning now")
        print("Download Thread alive: " + str(download_thread.is_alive()), "Provess Thread alive: " + str(process_thread.is_alive()))
        return download_result and process_result
