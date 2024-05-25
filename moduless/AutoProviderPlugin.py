from aplustools.webtools import Search
from aplustools.imagetools import OnlineImage, OfflineImage
save_image = OnlineImage.save_image
convert_image_format = OnlineImage.convert_image_format
download_image = OnlineImage.download_image
download_logo_image = OnlineImage.download_logo_image
from aplustools.webtools import check_url, is_crawlable
import os
import requests
from bs4 import BeautifulSoup
import urllib3
from abc import ABC, abstractmethod
from PIL import Image
from typing import Optional, Union
from urllib.parse import urljoin, urlparse
from urllib.parse import urlencode, urlunparse, quote_plus
from urllib.request import urlopen, Request

# Disable only the specific InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AutoProviderPlugin(ABC):
    def __init__(self, title: str, chapter: int, chapter_rate: float, data_folder: str, cache_folder: str, provider: str, specific_provider_website: str, logo_path: str):
        self.title = title
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

    def next_chapter(self):
        self.chapter += self.chapter_rate
        self.chap()
        if self.update_current_url():
            return self.cache_current_chapter()
        else:
            return False
        
    def previous_chapter(self):
        self.chapter -= self.chapter_rate
        self.chap()
        if self.update_current_url():
            return self.cache_current_chapter()
        else:
            return False
        
    def reload_chapter(self):
        self.chap()
        if self.update_current_url():
            return self.cache_current_chapter()
        else:
            return False
            
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

    def _make_cache_readable(self):
        # List all files in the directory
        files = os.listdir(self.cache_folder)
        # Filter out files that are not numerical
        numerical_files = [f for f in files if f.split('.')[0].isdigit()]
        # Sort files numerically
        numerical_files.sort(key=lambda x: int(x.split('.')[0]))
        if len(numerical_files) < 5 and self.provider.lower() != "direct":
            self.blacklisted_websites.append(self.current_url.split("/")[2])
        for i, file in enumerate(numerical_files):
            f_lst = file.split(".")
            # Define file name and extension
            file_name = f_lst[0]
            file_extension = f_lst[-1]
            # Generate a new file name with three digits
            new_name = str(i+1).zfill(3)
            # Convert the file to png and rename it to new_name var
            convert_image_format('', self.cache_folder, file_name, file_extension, new_name=new_name, target_format='png')
            print(f'Renamed {file} to {new_name}')
            
    def _download_image(self, img_tag):
        image = OnlineImage(urljoin(self.current_url, img_tag['src']))
        image.download_image(self.cache_folder)
            
    def cache_current_chapter(self):
        if not self.current_url:
            print("URL nor found.")
            return False
        if not is_crawlable(self.current_url):
            print("URL not crawlable as per robots.txt.")
            return False
            
        self._empty_cache()
        try:
            response = requests.get(self.current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if not os.path.exists(self.cache_folder):
                os.makedirs(self.cache_folder)
                
            img_tags = soup.find_all('img')
            for img_tag in img_tags:
                self._download_image(img_tag)
                
            print(f"{len(img_tags)} images downloaded!")
        except Exception as e:
            print(f"An error occurred: {e}")
        self._make_cache_readable()
        return True
        