import json
import base64
from io import BytesIO
from PIL import Image
import requests
import urllib3
import os
from urllib.parse import urlencode, urlunparse, quote_plus
from urllib.request import urlopen, Request
from urllib.parse import urljoin, urlparse

# Disable only the specific InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ManhwaFilePlugin:
    def __init__(self, title, chapter, file_path, data_folder, cache_folder):
        self.title = title # You can't really choose the title?
        self.chapter = chapter
        self.file_path = file_path
        self.data_folder = data_folder
        self.cache_folder = cache_folder
        self.current_chapter_data = None  # This will hold the current chapter data after reading
        
    def set_title(self, new_title):
        self.title = new_title
        
    def get_title(self):
        return self.title
        
    def set_chapter(self, new_chapter):
        self.chapter = new_chapter
        
    def get_chapter(self):
        return self.chapter
        
    def set_file_path(self, new_file_path):
        self.file_path = new_file_path
        
    def get_file_path(self):
        return self.file_path
        
    def redo_prep(self):
        self._empty_cache()
        image = Image.open(f"{self.data_folder}empty.png")
        image.save(f"{self.cache_folder}empty.png")
        
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
                return url
            else:
                print(f"The URL {url} cannot be crawled, checking next result...")
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
        
    def _save_image(self, base_location, img_data, original_name, original_format=None, new_name=None, target_format=None):
        if original_format == '.svg':
            print("SVG format is not supported.")
            return None
        source_path = os.path.join(base_location, f"{original_name}.{original_format}" if original_format else original_name)
        with open(source_path, 'wb') as img_file:
            img_file.write(img_data)
        return self._convert_image_format(source_path, new_name, target_format) if target_format else source_path
            
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

    def _empty_cache(self):
        files = os.listdir(self.cache_folder)
        for f in files:
            os.remove(f"{self.cache_folder}/{f}")
        #list( map( os.unlink, (os.path.join( mydir,f) for f in os.listdir(mydir)) ) )

    def _make_cache_readable(self):
        # List all files in the directory
        files = os.listdir(self.cache_folder)
        # Filter out files that are not numerical
        numerical_files = [f for f in files if f.split('.')[0].isdigit()]
        # Sort files numerically
        numerical_files.sort(key=lambda x: int(x.split('.')[0]))
        for i, file in enumerate(numerical_files):
            # Define file name
            file_name = file.split(".")[0]
            # Generate a new file name with three digits
            new_name = str(i+1).zfill(3)
            # Convert the file to png and rename it to new_name var
            self._convert_image_format(os.path.join(self.cache_folder, file), new_name=new_name, target_format='png')
            print(f'Renamed {file} to {new_name}')

    def read_mwa_file_chapter(self): # Maybe read and set title here
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            for chapter in data['chapters']:
                if chapter['chapterNumber'] == self.chapter:
                    self.current_chapter_data = chapter
                    return chapter
            print("Chapter not found")
            raise Exception("Chapter not found")#return None

    def cache_current_chapter(self):
        if not self.current_chapter_data:
            print("Chapter data not found.")
            return False

        self._empty_cache()

        for i, page in enumerate(self.current_chapter_data['pages']):
            if page['type'] == 'base64':
                image_data = base64.b64decode(page['data'])
            elif page['type'] == 'url':
                response = requests.get(page['data'])
                image_data = response.content
            else:
                print(f"Unknown type: {page['type']}")
                continue

            self._save_image(self.cache_folder, image_data, str(i), target_format='png')

        self._make_cache_readable()
        return True

    def next_chapter(self):
        self.chapter += 1
        try: self.read_mwa_file_chapter()
        except: return False
        return self.cache_current_chapter()

    def previous_chapter(self):
        self.chapter -= 1
        try: self.read_mwa_file_chapter()
        except: return False
        return self.cache_current_chapter()

    def reload_chapter(self):
        try: self.read_mwa_file_chapter()
        except: return False
        return self.cache_current_chapter()
        