from extensions.AutoProviderPlugin import AutoProviderPlugin
import requests
from bs4 import BeautifulSoup
import os

class AutoProviderPluginDynastyScans(AutoProviderPlugin):
    def __init__(self, title, chapter, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.dynasty-scans.com", logo_path="./data/DynastyScansLogo.png")
        self._download_logo_image('https://dynasty-scans.com/assets/brand-e61682a5fc714c8b69bdb66191d450eb.png', "DynastyScansLogo", img_format='png')
        
    def _direct_provider(self):
        url = self._get_url(f'https://{self.specific_provider_website}/chapters/{"_".join(self.title.lower().split())}_ch{int(self.chapter):02d}', f'chapter {self.chapter} {self.title}')
        if url:
            print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
            return url
        return None
        
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
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', class_='page') # del a[-1]
            link = ''.join(links[0]['href'].split("/").pop(-1)) # del a[2:4]
            for i in range(len(links) + 1): # img urls have pattern
                response = requests.get(self.current_url + f"#{i+1}")
                print(self.current_url + f"#{i+1}")
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
