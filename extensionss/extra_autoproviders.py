from modules.AutoProviderPlugin import AutoProviderPlugin
from urllib.parse import urlencode, urlunparse, quote_plus
import requests
from bs4 import BeautifulSoup
import os
import re
from aplustools.web.webtools import Search


class AutoProviderPluginManhwaClan(AutoProviderPlugin):
    def __init__(self, title, chapter, chapter_rate, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, chapter_rate=chapter_rate, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.manhwaclan.com", logo_path="./data/ManhwaClanLogo.png")
        if not os.path.isfile(os.path.join(data_folder, "ManhwaClanLogo.png")):
            try: self._download_logo_image('https://manhwaclan.com/wp-content/uploads/2022/02/Logo_230.png', "ManhwaClanLogo", img_format='png')
            except: return

    def _direct_provider(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://manhwaclan.com',
            'Referer': 'https://manhwaclan.com/',
        }

        # Define the URL for the request
        url = 'https://manhwaclan.com/wp-admin/admin-ajax.php'

        # Define the data for the first POST request
        data = {
            'action': 'wp-manga-search-manga',
            'title': self.title
        }

        # Send the first POST request
        response = requests.post(url, headers=headers, data=data)

        # Check for a successful response (HTTP status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            response_data = response.json()
            url = self._get_url(response_data["data"][0]["url"] + f"chapter-{self.chapter_str}/", f'chapter {self.chapter} {self.title.title()}')
            if url:
                print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
                return url
        else:
            print(f'Error: {response.status_code}')
        return None
    
    def _indirect_provider(self):
        url = self._get_url(f'https://{self.specific_provider_website}/manga/{"-".join(self.url_title.lower().split())}/chapter-{self.chapter_str}/', f'chapter {self.chapter} {self.title.title()}')
        if url:
            print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
            return url
        return None

class AutoProviderPluginMangaKakalot(AutoProviderPlugin):
    def __init__(self, title, chapter, chapter_rate, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, chapter_rate=chapter_rate, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website=None, logo_path="./data/MangaKakalotLogo.png")
        self.websites = ['https://www.manga-kakalot.net/', 'https://mangakakalot.com/']
        if not os.path.isfile(os.path.join(data_folder, "MangaKakalotLogo.png")):
            try:
                if not self._download_logo_image(f'{self.websites[0]}themes/home/icons/logo.png', "MangaKakalotLogo", img_format='png'):
                    self._download_logo_image(f'{self.websites[1]}themes/home/icons/logo.png', "MangaKakalotLogo", img_format='png')
            except: return
        self.specific_provider_website = self.websites[0]
        self.manga_abbreviation = None
        
    def _switch_website(self):
        if self.specific_provider_website == self.websites[0]:
            self.specific_provider_website = self.websites[1]
        else:
            self.specific_provider_website = self.websites[0]
        print(f"Switched to {self.specific_provider_website}")
        
    def _direct_provider(self):
        pass
    
    def _indirect_provider(self):
        if not self.manga_abbreviation:
            query = f'manga "{self.title}" site:{self.specific_provider_website} -chapter'
            result = Search.duckduckgo_provider(query)
            #if self.title.lower() in i.title.lower() and not "chapter" in i.title.lower():
            self.manga_abbreviation = result.split("/")[-1]

        if not self.manga_abbreviation:
            self._switch_website()  # Switch website if abbreviation is not found and retry
            return self._direct_provider()

        return f'https://{self.specific_provider_website}/chapter/{self.manga_abbreviation}/chapter_{self.chapter}/'
        
    def _make_cache_readable(self):
        # List all files in the directory
        files = os.listdir(self.cache_folder)
        # Filter out files that are not numerical
        numerical_files = [f for f in files if f.split('.')[0].isdigit()]
        # Sort files numerically
        numerical_files.sort(key=lambda x: int(''.join(x.split('.')[0]).split("-")[0]))
        if len(numerical_files) < 5 and self.provider.lower() != "direct":
            self.blacklisted_websites.append(self.current_url.split("/")[2])
        for i, file in enumerate(numerical_files):
            # Define file name
            file_name = file.split(".")[0]
            # Generate a new file name with three digits and .png extension
            new_name = str(i+1).zfill(3) + '.png'
            # Rename the file
            os.rename(os.path.join(self.cache_folder, file), os.path.join(self.cache_folder, new_name))
            print(f'Renamed {file} to {new_name}')
        
        #if "-o" in [str(x) if not x.isdigit() else "" for x in img_name] and sum([int(x) if x.isdigit() else 0 for x in img_name]) > 0:
        #    count += 1
        #    # Send a HTTP request to get the content of the image
        #    img_data = requests.get(img_url).content
        #    # Write image data to a file
        #    with open(os.path.join(self.cache_folder, f"{count:03d}"), 'wb') as img_file: # f"00{count}"[-3:]
        #        img_file.write(img_data)
        
class AutoProviderPluginMangaDex(AutoProviderPlugin): # W.I.P
    def __init__(self, title, chapter, chapter_rate, data_folder, cache_folder, provider):
        self.title = title
        self.chapter = chapter
        self.provider = provider
        self.logo_path = './data/Untitled-1-noBackground.png'
        
    def _direct_provider(self):
        pass
    def _indirect_provider(self):
        pass
        
class AutoProviderPluginMangaQueen(AutoProviderPlugin):
    def __init__(self, title, chapter, chapter_rate, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, chapter_rate=chapter_rate, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.mangaqueen.com", logo_path="./data/MangaQueenLogo.png")
        if not os.path.isfile(os.path.join(data_folder, "MangaQueenLogo.png")):
            try: self._download_logo_image('https://mangaqueen.com/wp-content/uploads/2022/11/mangaqueen-2.png', "MangaQueenLogo", img_format='png')
            except: return        

    def _direct_provider(self):
        pass
    
    def _indirect_provider(self):
        url = self._get_url(f'https://{self.specific_provider_website}/manga/{"-".join(self.url_title.lower().split())}/chapter-{self.chapter}/', f'chapter {self.chapter} {self.title}')
        if url:
            print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
            return url
        return None

class AutoProviderPluginMangaGirl(AutoProviderPlugin):
    def __init__(self, title, chapter, chapter_rate, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, chapter_rate=chapter_rate, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.mangagirl.me", logo_path="./data/MangaGirlLogo.png")
        if not os.path.isfile(os.path.join(data_folder, "MangaGirlLogo.png")): 
            try: self._download_logo_image('https://mangagirl.me/wp-content/uploads/2022/09/mangagirl-logo-1.png', "MangaGirlLogo", img_format='png')
            except: return

    def _direct_provider(self):
        pass
    
    def _indirect_provider(self):
        url = self._get_url(f'https://{self.specific_provider_website}/manga/{"-".join(self.url_title.lower().split())}/chapter-{self.chapter}/', f'chapter {self.chapter} {self.title}')
        if url:
            print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
            return url
        return None

class AutoProviderPluginMangaBuddy(AutoProviderPlugin):
    def __init__(self, title, chapter, chapter_rate, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, chapter_rate=chapter_rate, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.mangabuddy.com", logo_path="./data/MangaBuddyLogo.png")
        if not os.path.isfile(os.path.join(data_folder, "MangaBuddyLogo.png")):
            try:
                self._download_logo_image(
                    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAABYlBMVEUAAIAAAKkAAKsAAKoAAKsAAKodHbSmpuHU1PEzM7u1tebm5vdCQsAICKxsbM7a2vPGxuwPD68CAqpfX8nMzO47O70BAapcXMnPz+9SUsU2Nrz19fv////b2/P9/f7q6vjj4/aRkdqhod/f3/THx+z5+f0yMrqLi9ikpOCDg9b6+v19fdO3t+cREbDz8/uCgtWuruSNjdlERMBzc9CqquItLbkHB6zw8Prl5fbY2PLZ2fIqKriTk9s/P7+IiNcfH7SFhdbLy+0lJbZ0dNB3d9KQkNr7+/739/xZWccDA6vR0fDx8fpkZMssLLhISMKYmNwgILTa2vJ/f9RBQcDQ0O8LC64hIbVGRsHm5vY4OLze3vQoKLe/v+mXl9zc3POJidcUFLA8PL74+P3p6fdoaMwEBKt7e9PNze5BQb8cHLPp6fjy8vugoN8+Pr5UVMZWVsYFBaspKbgODq41NbseHrQJCa3K28caAAAABnRSTlMCfOb/fOfvJMB8AAABEElEQVR4AbzKU4IDUQAF0U5uzDFrbPXYtm3vfxWx8fov9VvHslxu1c3tSn0Z81heM/BacqhhwOcP+IKhcCQaizc1q6W1rb2js6u7CHp6oa8fBgaBIQ3DyCiMjReAJmByahpmZmFEczb98wuwWARLsKwVWF1bZ0PaZEvbsFMEu2mwlwLqyoP9anCQBod5cOQEjuHEAMKnZ+cXMgCA0KUJXF3DTTW4zYM+3cG9AWzpwQnsm8FjNXhKg+cUsNf0gv36Vgbe4eMzBb6+D+FHvxD/I/BeBP9sPCWXkJiUnJKaJpOewZyZJZOdk4uUYPJi8guAVGERkCgWAhIl4aUoKUpsYFM14azHQijzMjCy4tHPwgAAoVBHJ6Y0EhcAAAAASUVORK5CYII=', 
                    "MangaBuddyLogo", img_format='png')
            except: return

    def _make_cache_readable(self):
        # List all files in the directory
        files = os.listdir(self.cache_folder)
        
        # Regular expression pattern to match hash-like file names
        pattern = re.compile(r'^[a-fA-F0-9]+\.\w+$')
        
        # Filter out files that match the pattern
        hash_files = [f for f in files if pattern.match(f)]
        
        # Additional operations can be performed on hash_files if needed
        for i, file in enumerate(hash_files):
            # Define file name
            file_name = file.split(".")[0]
            # Generate a new file name with three digits and .png extension
            new_name = str(i+1).zfill(3) + '.png'
            # Rename the file
            os.rename(os.path.join(self.cache_folder, file), os.path.join(self.cache_folder, new_name))
            print(f'Renamed {file} to {new_name}')
        
    def _direct_provider(self):
        pass
    
    def _indirect_provider(self):
        url = self._get_url(f'https://{self.specific_provider_website}/{"-".join(self.url_title.lower().split())}/chapter-{self.chapter}/', f'chapter {self.chapter} {self.title}')
        if url:
            print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
            return url
        return None

class AutoProviderPluginS2Manga(AutoProviderPlugin):
    def __init__(self, title, chapter, chapter_rate, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, chapter_rate=chapter_rate, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.s2manga.com", logo_path="./data/S2MangaLogo.png")
        if not os.path.isfile(os.path.join(data_folder, "S2MangaLogo.png")):
            try: self._download_logo_image('https://s2manga.com/wp-content/uploads/2017/10/cooltext-357206071789.png', "S2MangaLogo", img_format='png')
            except: return

    def _direct_provider(self):
        pass
    
    def _indirect_provider(self):
        url = self._get_url(f'https://{self.specific_provider_website}/manga/{"-".join(self.url_title.lower().split())}/chapter-{self.chapter}/', f'chapter {self.chapter} {self.title}')
        if url:
            print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
            return url
        return None
        
    def _make_cache_readable(self):
        # List all files in the directory
        files = os.listdir(self.cache_folder)
        # Filter out files that are not numerical
        numerical_files = [f for f in files if f.split('.')[0].isdigit()]
        # Sort files numerically
        numerical_files.sort(key=lambda x: int(''.join(''.join(x.split('.')[0]).split("-"))))
        if len(numerical_files) < 5 and self.provider.lower() != "direct":
            self.blacklisted_websites.append(self.current_url.split("/")[2])
        for i, file in enumerate(numerical_files):
            # Define file name
            file_name = file.split(".")[0]
            # Generate a new file name with three digits and .png extension
            new_name = str(i+1).zfill(3) + '.png'
            # Rename the file
            os.rename(os.path.join(self.cache_folder, file), os.path.join(self.cache_folder, new_name))
            print(f'Renamed {file} to {new_name}')

class AutoProviderPluginNovelCool(AutoProviderPlugin): # W.I.P
    def __init__(self, title, chapter, chapter_rate, data_folder, cache_folder, provider):
        self.logo_path = './data/Untitled-1-noBackground.png'
        return
        super().__init__(title=title, chapter=chapter, chapter_rate=chapter_rate, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.novelcool.com", logo_path="./data/NovelCoolLogo.png")
        if not os.path.isfile(os.path.join(data_folder, "NovelCoolLogo.png")):
            try:
                self._download_logo_image('https://www.novelcool.com/files/images/logo/logo_word.svg', "NovelCoolLogo", img_format='png') 
                # https://www.novelcool.com/files/images/logo/logo.svg
            except: return

    def _direct_provider(self):
        pass
    
    def _indirect_provider(self):
        return
        if not self.current_url:
            query = f'manga "{self.title}" "chapter" site:{self.specific_provider_website}'
            results = search(query, num_results=10, advanced=True)
            for i in results:
                if self.title.lower() in i.title.lower() and "chapter" in i.title.lower():
                    self.current_url = i.url
                    break
        if not self.current_url:
            return None
        return f'https://{self.specific_provider_website}/chapter/{self.manga_abbreviation}/chapter_{self.chapter}/'
        
    def _make_cache_readable(self): # has ?acc=0MF58FZVsb-gJxzmMqV1nQ&exp=1696171800 and hex/hash filenames .webp
        return
        # List all files in the directory
        files = os.listdir(self.cache_folder)
        # Filter out files that are not numerical
        numerical_files = [f for f in files if f.split('.')[0].isdigit()]
        # Sort files numerically
        numerical_files.sort(key=lambda x: int(''.join(''.join(x.split('.')[0]).split("-"))))
        if len(numerical_files) < 5 and self.provider.lower() != "direct":
            self.blacklisted_websites.append(self.current_url.split("/")[2])
        for i, file in enumerate(numerical_files):
            # Define file name
            file_name = file.split(".")[0]
            # Generate a new file name with three digits and .png extension
            new_name = str(i+1).zfill(3) + '.png'
            # Rename the file
            os.rename(os.path.join(self.cache_folder, file), os.path.join(self.cache_folder, new_name))
            print(f'Renamed {file} to {new_name}')
            
    def cache_current_chapter(self):
        super().cache_current_chapter(None)
