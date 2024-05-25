# ManhwaViewer 1.6-dev

If you want to use ManhwaViewer v1.6.x, just download the latest release [here](https://github.com/adalfarus/Manhwa-Viewer-1.6/releases/latest).

<p float="center">
  <img src="/repo_images/repo_image_1.png" width="41%" />
  <img src="/repo_images/repo_image_4.png" width="48%" />
</p>

MV 1.6.5 Preview (Both windows are the same size)
<p float="center">
    <img src="/repo_images/repo_image_8.png" width="100%" />
</p>
<p float="center">
    <img src="/repo_images/repo_image_9.png" width="100%" />
</p>

(Everything below this point is accurate for MV 1.6.2)
## For Users

### Basics:

- **Search Bar**: At the top, which can be lowered. It will be grayed out if the current "Provider" does not support search.
- **Side Menu**: Contains all important features. It's less frequently used if you don't change stories often.
- **Optimal Settings**:
  - Chapter rate set to 0.5 (set to 1.0 if you don't want extra chapters without a story).
  - Provider type: Choose between indirect and direct. Direct is generally better or necessary.
  - Scale buttons and default width setting should be self-explanatory.
  - Window modification options: Borderless, Hide Scrollbar, Stay On Top.
  - Change your current provider using the "Provider" dropdown menu in the side menu. Included providers are AsuraToon, CoffeManga, HariManga, MangaQueen (can be slow), and ManhwaClan. Additional providers can be added through modding.

To read, type relevant keywords into the search bar and double-click the desired result. Restart the program if the chapter and title don't update automatically. Manual entry of the title in the side menu is possible but can cause errors.

**Note**: Exporting chapters is not recommended due to performance issues.

The program takes 1-2 seconds to load initially. Images are loaded while scrolling through a chapter, avoiding additional loading times.

# Modding Guide for ManhwaViewer

## Introduction
To mod ManhwaViewer, you need a basic understanding of Python, as the program is written in this language. The windows 7 version runs on [CPython 3.10 by NulAsh](https://github.com/NulAsh/cpython/releases/tag/v3.10.1win7-1) with [PySide2](https://pypi.org/project/PySide2/) and the windows 10-11 version runs on Python 3.12 with [PySide6](https://pypi.org/project/PySide6/). All standard libraries are included.

## Getting Started
1. **Accessing the App Folder**:
   - Right-click on the ManhwaViewer shortcut or search result.
   - Select "Open File Location".
   - Navigate to the `_internal` directory and then open the `extensions` folder.
   - Here, you can either create a new file or modify an existing one.
   - For detailed information, explore the `_interal/modules/AutoProviderPlugin.py` file.

2. **Working with Packages**:
   - Packages can be added to the `_interal/libs` folder, this location is the first python will check so you can overwrite packages.
   - All standard libs have been included as a [pyinstaller option](https://stackoverflow.com/questions/62602954/force-pyinstaller-to-include-all-built-in-modules).
   - Two key steps:
     - Add `from modules.AutoProviderPlugin import AutoProviderPlugin, AutoProviderBaseLike` at the beginning of your code.
     - Your extensions must be a subclass of either `AutoProviderPlugin` or `AutoProviderBaseLike`.

## Creating Extensions
1. **Using `AutoProviderPlugin` and `AutoProviderBaseLike` Classes**:
   - `AutoProviderPlugin` is the base class for all extensions.
   - `AutoProviderBaseLike` inherits from `AutoProviderPlugin` and is tailored for websites that use the same website-base as the ManhwaClan website.

2. **Implementing a Simple Base-like Extension**:
   - Subclass `AutoProviderBaseLike`.
   - Your `__init__` method should accept the parameters (`title`, `chapter`, `chapter_rate`, `data_folder`, `cache_folder`, `provider`).
   - Pass these parameters along with the website you've chosen as **specific_provider_website** (only the core url, so from `https://www.manhwaclan.com` -> `manhwaclan.com`).
   - Restart the app to see your provider and test it out. Check the logs at **./_internal/data/logs.txt** for errors even if everything seems to work fine.

3. **Creating Custom Site Extensions (Advanced)**:
   - Subclass `AutoProviderPlugin`.
   - Follow similar steps as Base-like extensions, but include additional error handling for logo downloads as any uncaught exception will crash the program.

## Important Methods and Variables
- Internal Variables: 
  - `title` -- The current Manhwa Title
  - `url_title` -- The current Manhwa Title, made url safe
  - `chapter` -- The current chapter, integer if it's whole and float if it's decimal.
  - `chapter_str` -- A string of the current chapter
  - `chapter_rate` -- Float
  - `data_folder` & `chache_folder` -- Not really used for modding
  - `provider` -- The current provider as a string, can either be "indirect" or "direct"
  - `specific_provider_website` -- Whatever you passed to the parents init call
  - `blacklisted_websites` -- Was used for search engine provider
  - `current_url` -- Holds the current chapter url

### Key Methods Overview
Understanding these methods is crucial for successful modding. They play a vital role in how the application processes images and retrieves chapter URLs.

#### 1. `validate_image`
- **Purpose**: Determines which downloaded images qualify as "Chapter Images" for conversion to PNG (as the program only loads PNGs for chapters).
- **Input**: Receives a string representing an image file (e.g., `"image003.png"`).
- **Output**:
  - Returns `None, None, None` if the image is invalid.
  - Returns `file_name` (original name), `file_extension` (original extension), and `new_name` (simplified name for internal use) for valid images.

#### 2. `_indirect_provider`
- **Purpose**: Finds the URL for the currently selected chapter based on the current chapter and title. It's an estimation method.
- **Output**: Returns the chapter URL as a string.
- **Behavior**: Utilizes class attributes for its operation.

#### 3. `_direct_provider`
- **Purpose**: Similar to `_indirect_provider`, but designed to actively search for the chapter URL.
- **Output**: Returns the chapter URL as a string.
- **Behavior**: Leverages class attributes and a search mechanism.

#### 4. `get_search_results`
- **Purpose**: Provides search results, primarily used by the search feature of the application.
- **Input**: Takes in a search query as text.
- **Output**: Returns a list in the format `[title, empty_string]`. Should return `False` if the method is not implemented.

### Implementation Recommendations
- Implement a general `_search` method to streamline support for both `get_search_results` and `_direct_provider`.
- Avoid altering other methods to prevent application crashes.
- Custom helper methods can be created, but refrain from using specific reserved method names (listed above).

## Guidelines and Libraries
- Avoid modifying certain methods to prevent crashes.
- Helper methods can be implemented, but avoid any already used names (`__init__`, `urlify`, `get_logo_path`, `set_title`, `get_title`, `set_chapter`, `get_chapter`, `set_chapter_rate`, `get_chapter_rate`, `set_provider`, `get_provider`, `set_current_url`, `get_current_url`, `set_blacklisted_websites`, `get_blacklisted_websites`, `chap`, `next_chapter`, `previous_chapter`, `reload_chapter`, `_handle_cache_result`, `_download_logo_image`, `redo_prep`, `update_current_url`, `_get_current_chapter_url`, `_get_url`, `_google_provider`, `_duckduckgo_provider`, `_bing_provider`, `_indirect_provider`, `_direct_provider`, `get_search_results`, `_empty_cache`, `_download_image`, `download_images`, `validate_image`, `process_images`, `callback`, `cache_current_chapter`).
- Included non-standard libraries:
  - `aplustools==0.1.4.2`
  - `beautifulsoup4==4.12.2`
  - `duckduckgo_search==3.9.6`
  - `Pillow==10.3.0`
  - `PySide6==6.6.0`
  - `Requests==2.31.0`
  - `urllib3==2.1.0`
  - `packaging==24.0`
  - `stdlib-list==0.10.0`

To compatabilty: 
- Windows Vista and lower are untested
- Windows 10-1703 has a different dark mode reg key (you need to set the environment variable to change themes).
- All other Windows versions should work without problems.
- Linux and Mac would need more modification but are also okay, just that I wouldn't be able to easily test them.

## For Programmers

### Bugs
#### The title doesn't update internally and you need to restart the program.
##### Affected versions: 1.6.2 & 1.6.3
##### Fix:
- ~~Open the file {install_location}/_internal/modules/AutoProviderPlugin.py~~
- ~~Go to `line 68` or to the function `set_title`~~
- ~~Add the line **self.url_title = self.urlify(new_title)**~~
- None

#### The task window keeps popping up if the task failed and you close it too quickly.
##### Affected versions: 1.6.2 & 1.6.3
##### Fix (1.6.3):
- ~~Open the file {install_location}/_internal/modules/Classes.py~~
- ~~Go to to the function `updateProgress`~~
- ~~Change the line **while self.current_value == 0 and self.value() < 10:** to **if self.current_value == 0 and self.value() < 10:**~~
- None
