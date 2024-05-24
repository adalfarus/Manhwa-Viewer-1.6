import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from googlesearch import search
from duckduckgo_search import DDGS
import urllib3
from urllib.parse import urlencode, urlunparse, quote_plus
from urllib.request import urlopen, Request
import base64
from abc import ABC, abstractmethod
import re
from PIL import Image
from io import BytesIO

# Disable only the specific InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProviderPlugin(ABC):
    def __init__(self, title, chapter, provider, specific_provider_website, logo_path):
        self.title = title
        self.chapter = int(chapter) if not chapter % 2 == 0.5 else chapter
        self.provider = provider
        self.specific_provider_website = specific_provider_website
        self.logo_path = logo_path
        self.data = '.\data'
        self.cache = '.\cache'
        self.blacklisted_websites = [
            "247manga.com",
            "ww6.mangakakalot.tv",
            "jimanga.com",
            "mangapure.net",
            "mangareader.mobi",
            "onepiece.fandom.com"
        ]
        self.current_url = None
        #self.update_current_url()
        
    def get_logo_path(self):
        return self.logo_path
        
    def set_title(self, new_title):
        self.title = new_title
        
    def get_title(self):
        return self.title
        
    def set_chapter(self, new_chapter):
        self.chapter = new_chapter
        self.chapter = int(self.chapter) if not self.chapter % 2 == 0.5 else self.chapter
        
    def get_chapter(self):
        self.chapter = int(self.chapter) if not self.chapter % 2 == 0.5 else self.chapter
        return self.chapter
        
    def set_provider(self, new_provider):
        self.provider = new_provider
        
    def get_provider(self):
        return self.provider
        
    def set_current_url(self, new_current_url):
        self.current_url = new_current_url
        
    def get_current_url(self):
        return self.current_url
        
    def next_chapter(self):
        self.chapter += 0.5
        self.chapter = int(self.chapter) if not self.chapter % 2 == 0.5 else self.chapter
        self.update_current_url()
        self.cache_current_chapter()
        
    def previous_chapter(self):
        self.chapter -= 0.5
        self.chapter = int(self.chapter) if not self.chapter % 2 == 0.5 else self.chapter
        self.update_current_url()
        self.cache_current_chapter()
        
    def reload_chapter(self):
        self.chapter = int(self.chapter) if not self.chapter % 2 == 0.5 else self.chapter
        self.update_current_url()
        self.cache_current_chapter()
        
    def _save_image(self, base_location, img_data, original_name, original_format=None, new_name=None, target_format=None):
        if original_format == '.svg':
            print("SVG format is not supported.")
            return None
        source_path = os.path.join(base_location, f"{original_name}.{original_format}" if original_format else original_name)
        with open(source_path, 'wb') as img_file:
            img_file.write(img_data)
        return _convert_image_format(source_path, new_name, target_format) if target_format else source_path
            
    def _convert_image_format(self, source_path, new_name=None, target_format='png'):
        if source_path.split(".")[-1] == "svg":
            print("SVG format is not supported.")
            return None
        # Extract the base file name without extension
        base_name = os.path.splitext(os.path.basename(source_path))[0]
        # Create the new file path with the desired extension
        if new_name is None:
            new_file_path = os.path.join(os.path.dirname(source_path), f"{base_name}.{target_format}")
        else:
            new_file_path = os.path.join(os.path.dirname(source_path), f"{new_name}.{target_format}")
        # Open, convert and save the image in the new format
        with Image.open(str(source_path)) as img:
            img.save(new_file_path)
        os.remove(source_path) if source_path != new_file_path else print("Skipping deleting ...")
        return new_file_path
            
    def _download_logo_image(self, img_url, new_name, img_format):
        try:
            format_match = re.match(r'^data:image/[^;]+;base64,', img_url)
            if format_match:
                if "image/svg+xml" in img_url:
                    print("SVG format is not supported.")
                    return False
                img_data = base64.b64decode(img_url.split(',')[1])
                img_name = new_name + '.' + img_format
                source_path = os.path.join(self.data, img_name)
                with open(source_path, 'wb') as img_file:
                    img_file.write(img_data)
            else:
                response = requests.get(img_url, verify=False, timeout=5)
                response.raise_for_status()
                img_name = os.path.basename(urlparse(img_url).path)
                source_path = os.path.join(self.data, img_name)
                img_data = response.content
                with open(source_path, 'wb') as img_file:
                    img_file.write(img_data)
            if img_name.strip():
                self._convert_image_format(source_path, new_name, img_format)
                return True
            else:
                return False
        except KeyError:
            print("The image tag does not have a src attribute.")
            return False
        #except Exception as e:
        #    print(f"An error occurred while downloading the image: {e}")
        #    return False
        
    def update_current_url(self):
        print("Updating current URL...")
        self.current_url = self._get_current_chapter_url()
        if self.current_url:
            print(f"Current URL set to: {self.current_url}")
        else:
            print("Failed to update current URL.")
        self.chapter = float(self.chapter.replace("-", "."))
        
    def _get_current_chapter_url(self):
        provider_function = {
            "google": self._google_provider,
            "duckduckgo": self._duckduckgo_provider,
            "bing": self._bing_provider,
            "direct": self._direct_provider
        }.get(self.provider.lower())

        if provider_function:
            self.chapter = str(self.chapter).replace(".", "-")
            return provider_function()
        else:
            print(f"Provider {self.provider} not supported.")
            return None
        
    def _get_url(self, url, title):
        if self.title.lower() in title.lower() and f"chapter {self.chapter}" in title.lower():
            # Checking if the URL is accessible or leads to a 404 error
            try:
                response = requests.head(url, allow_redirects=True)  # Using HEAD request to get the headers
                if response.status_code == 404:
                    print(f"The URL {url} leads to a 404 error, checking next result...")
                    return None
            except requests.RequestException as e:
                print(f"Error accessing URL {url}: {e}, checking next result...")
                return None
            if self._is_crawlable(url):
                if not url.split("/")[2] in self.blacklisted_websites:
                    return url
                else:
                    print("Blacklisted URL:", url)
            else:
                print(f"The URL {url} cannot be crawled, checking next result...")
        return None
        
    def _google_provider(self):
        queries = [
            f'manga "{self.title}" "chapter {self.chapter}" site:{self.specific_provider_website}',
            f'manga "{self.title}" chapter {self.chapter} site:{self.specific_provider_website}',
            f'manga {self.title} chapter {self.chapter} site:{self.specific_provider_website}',
            f'manga {self.title} site:{self.specific_provider_website}',
            f'manga site:{self.specific_provider_website}'
        ]
        for query in queries:
            results = search(query, num_results=10, advanced=True)
            for i in results:
                url = self._get_url(i.url, i.title)
                if url:
                    print("Found URL:", url)
                    return url
        print("No crawlable URL found.")
        return None
        
    def _duckduckgo_provider(self):
        queries = [
            f'manga "{self.title}" "chapter {self.chapter}" site:{self.specific_provider_website}',
            f'manga "{self.title}" chapter {self.chapter} site:{self.specific_provider_website}',
            f'manga {self.title} chapter {self.chapter} site:{self.specific_provider_website}',
            f'manga {self.title} site:{self.specific_provider_website}',
            f'manga site:{self.specific_provider_website}'
        ]
        with DDGS(timeout=20) as ddgs:
            for query in queries:
                results = ddgs.text(query, timelimit=100, safesearch='off')
                for r in results:
                    url = self._get_url(r['href'], r['title'])
                    if url:
                        print("Found URL:", url)
                        return url
        print("No crawlable URL found.")
        return None
        
    def _bing_provider(self):
        queries = [
            f'manga "{self.title}" "chapter {self.chapter}" site:{self.specific_provider_website}',
            f'manga "{self.title}" chapter {self.chapter} site:{self.specific_provider_website}',
            f'manga {self.title} chapter {self.chapter} site:{self.specific_provider_website}',
            f'manga {self.title} site:{self.specific_provider_website}',
            f'manga site:{self.specific_provider_website}'
        ]
        custom_user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
        for query in queries:
            url = f'https://www.bing.com/search?q={quote_plus(query)}'
            headers = {"User-Agent": custom_user_agent}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print("Failed to retrieve the search results.")
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [[a.text, a['href']] for a in soup.find_all('a', href=True) if 'http' in a['href']]
            for link in links:
                url = self._get_url(link[1], link[0])
                if url:
                    print("Found URL:", url)
                    return url
        print("No crawlable URL found.")
        return None
                
    @abstractmethod
    def _direct_provider(self): # Can't be generalized, you need to overwrite this
        return None
        
    def _is_crawlable(self, url):
        """
        Check if the URL can be crawled by checking the robots.txt file of the website.
        """
        try:
            # Parse the given URL to get the netloc (domain) part
            domain = urlparse(url).netloc
            # Create the URL of the website's robots.txt file
            robots_txt_url = urljoin(f'https://{domain}', 'robots.txt')
            # Send a GET request to the robots.txt URL
            response = requests.get(robots_txt_url)
            # If the request was successful, check if the User-agent is allowed to crawl the URL
            if response.status_code == 200:
                # If "Disallow: /" is found for User-agent: *, it means the website can't be crawled
                if 'User-agent: *\nDisallow: /' in response.text:
                    return False
                return True
            else:
                print(f"Failed to retrieve the robots.txt file, status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred while checking the robots.txt file: {e}")
        return False  # Return False if there was an error or the robots.txt file couldn't be retrieved
        
    def _empty_cache(self):
        files = os.listdir(self.cache)
        for f in files:
            os.remove(f"{self.cache}/{f}")
        #list( map( os.unlink, (os.path.join( mydir,f) for f in os.listdir(mydir)) ) )
        
    def _make_cache_readable(self):
        # List all files in the directory
        files = os.listdir(self.cache)
        # Filter out files that are not numerical
        numerical_files = [f for f in files if f.split('.')[0].isdigit()]
        # Sort files numerically
        numerical_files.sort(key=lambda x: int(x.split('.')[0]))
        if len(numerical_files) < 5 and self.provider.lower() != "direct":
            self.blacklisted_websites.append(self.current_url.split("/")[2])
        for i, file in enumerate(numerical_files):
            # Define file name
            file_name = file.split(".")[0]
            # Generate a new file name with three digits
            new_name = str(i+1).zfill(3)
            # Convert the file to png and rename it to new_name var
            self._convert_image_format(os.path.join(self.cache, file), new_name=new_name, target_format='png')
            print(f'Renamed {file} to {new_name}')
            
    def _download_image(self, img_tag):
        try:
            img_url = urljoin(self.current_url, img_tag['src'])
            img_name = os.path.basename(urlparse(img_url).path)
            print(img_name)
            name = img_name.split(".")[0]
            extension = None
            try: extension = img_name.split(".")[1]
            except: pass
            
            if img_name.strip():
                img_data = requests.get(img_url, verify=False).content
                self._save_image(self.cache, img_data, name, extension, new_name=None, target_format=None)
        except KeyError:
            print("The image tag does not have a src attribute.")
        except Exception as e:
            print(f"An error occurred while downloading the image: {e}")
            
    def cache_current_chapter(self):
        if not self.current_url:
            print("URL nor found.")
            return False
        if not self._is_crawlable(self.current_url):
            print("URL not crawlable as per robots.txt.")
            return False
            
        self._empty_cache()
        try:
            response = requests.get(self.current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if not os.path.exists(self.cache):
                os.makedirs(self.cache)
                
            img_tags = soup.find_all('img')
            for img_tag in img_tags:
                self._download_image(img_tag)
                
            print(f"{len(img_tags)} images downloaded!")
        except Exception as e:
            print(f"An error occurred: {e}")
        self._make_cache_readable()
    