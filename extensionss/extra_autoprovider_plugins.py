from extensions.AutoProviderPlugin import AutoProviderPlugin
from duckduckgo_search import DDGS
from googlesearch import search
from urllib.parse import urlencode, urlunparse, quote_plus
import requests
from bs4 import BeautifulSoup
import os
import re

class AutoProviderPluginGoogle(AutoProviderPlugin):
    def __init__(self, title, chapter, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.google.com", logo_path="./data/GoogleLogo.png")
        self._download_logo_image('https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/220px-Google_2015_logo.svg.png', "GoogleLogo", img_format='png')
        # https://www.google.com/images/branding/googlelogo/1x/googlelogo_light_color_272x92dp.png
    def _direct_provider(self):
        queries = [
            f'manga "{self.title}" "chapter {self.chapter}"',
            f'manga "{self.title}" chapter {self.chapter}',
            f'manga {self.title} chapter {self.chapter}',
            f'manga {self.title}'
        ]
        for query in queries:
            results = search(query, num_results=10, advanced=True)
            for i in results:
                url = self._get_url(i.url, i.title)
                if url:
                    print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
                    return url
        print("No crawlable URL found.")
        return None
        
class AutoProviderPluginDuckDuckGo(AutoProviderPlugin):
    def __init__(self, title, chapter, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.duckduckgo.com", logo_path="./data/DuckDuckGoLogo.png")
        self._download_logo_image('data:image/png;base64,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', "DuckDuckGoLogo", img_format='png') # data:image/svg+xml;base64,PHN2ZyBmaWxsPSJub25lIiB2aWV3Qm94PSIwIDAgMTg0IDE0OCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cGF0aCBmaWxsPSIjZmZmIiBkPSJNNjkuOTQyIDEyOS4yNkg2Ni40NmwtNi4zMzggNi41MTd2LTEzLjAzM2gtMi42Nzh2MjIuMjI4aDIuNjc4di03LjMybDcuMjMgNy4yMy4wOS4wOWgzLjIxNHYtLjI2OGwtOC4xMjQtOC4wMzR6bS0xNy4xNCAxMS44NzNjLS45ODIuOTgyLTIuNDEgMS41MTgtNC4wMTcgMS41MTgtMi43NjcgMC01LjUzNC0xLjY5Ni01LjUzNC01LjYyNCAwLTMuMzAzIDIuMzItNS42MjQgNS41MzQtNS42MjQgMS40MjggMCAyLjc2Ny41MzYgMy44MzkgMS41MThsLjA4OS4wODkgMS42OTYtMS43ODYtLjA5LS4wODljLTEuNjA2LTEuNTE3LTMuNDgtMi4yMzItNS42MjMtMi4yMzItNC45MSAwLTguMjEzIDMuMzAzLTguMjEzIDguMTI0IDAgNS42MjQgNC4xMDYgOC4xMjMgOC4yMTMgOC4xMjNoLjA5YzIuMTQxIDAgNC4xOTUtLjgwMyA1LjYyMy0yLjMyMWwuMDktLjA4OS0xLjc4Ni0xLjc4NXptLTE4LjEyMi0zLjQ4MWMwIDIuODU2LTEuOTYzIDQuOTk5LTQuNzMgNS4wODgtMi45NDYgMC00LjczMi0xLjc4NS00LjczMi00Ljgydi04LjY2SDIyLjU0djguNjZjMCA0LjQ2MyAyLjY3OCA3LjMyIDYuODc0IDcuMzJoLjA5YzIuMDUyIDAgMy45MjctLjk4MiA1LjE3Ny0yLjVsLjA4OS0uMTc5LjA5IDIuNDExaDIuNDk5VjEyOS4yNkgzNC42OHpNOC4zNDcgMTIyLjY1NUguMjIzdjIyLjMxN2g4LjEyNGM3Ljc2NiAwIDExLjE1OC01LjcxMyAxMS4xNTgtMTEuMzM3IDAtNS4yNjctMy40ODEtMTAuOTgtMTEuMTU4LTEwLjk4em04LjM5IDEwLjg5YzAgNC4yODUtMi41ODggOC41Ny04LjMwMSA4LjU3SDMuMDh2LTE2LjY5M2g1LjI2N2M1LjcxMyAwIDguMzkgNC4xOTYgOC4zOSA4LjEyM3ptMTM4LjI3NyAxLjY5N2g2Ljg3NHY1LjE3N2MtMS42OTYgMS40MjgtMy43NDkgMi4yMzItNS45ODEgMi4yMzItNi4wNyAwLTguODM4LTQuMzc0LTguODM4LTguNjU5IDAtNC4zNzQgMi43NjgtOS4xMDYgOC43NDktOS4xMDYgMi40MSAwIDQuNjQyLjg5MyA2LjQyNyAyLjVsLjA4OS4wODkgMS42MDctMS44NzQtLjA4OS0uMDljLTIuMTQzLTIuMTQyLTQuOTk5LTMuMjEzLTguMTI0LTMuMjEzLTMuMzkyIDAtNi4yNDggMS4wNzEtOC4zMDIgMy4yMTMtMi4xNDIgMi4xNDMtMy4zMDIgNS4xNzgtMy4yMTMgOC41NyAwIDUuMjY3IDMuMDM1IDExLjMzNyAxMS42MDUgMTEuMzM3aC4xNzhjMy4yMTQgMCA2LjI0OS0xLjMzOSA4LjM5MS0zLjc0OXYtOC44MzhoLTkuNDYydjIuNDExem0tNzMuNzM1LTEyLjU4N2gtOC4xMjR2MjIuMzE3aDguMTI0YzcuNzY2IDAgMTEuMTU4LTUuNzEzIDExLjE1OC0xMS4zMzcgMC01LjI2Ny0zLjQ4MS0xMC45OC0xMS4xNTgtMTAuOTh6bTguMzkgMTAuODljMCA0LjI4NS0yLjU4OCA4LjU3LTguMzAxIDguNTdoLTUuMjY3di0xNi42OTNoNS4yNjdjNS42MjQgMCA4LjMwMiA0LjE5NiA4LjMwMiA4LjEyM3ptODUuNjA5LTQuNjQyYy00LjczMSAwLTguMTIzIDMuNDgyLTguMTIzIDguMjEzczMuMzkyIDguMTI0IDguMTIzIDguMTI0IDguMjEzLTMuMzkzIDguMjEzLTguMTI0YzAtNC44Mi0zLjM5Mi04LjIxMy04LjIxMy04LjIxM3ptNS41MzUgOC4yMTNjMCAzLjMwMy0yLjMyMSA1LjYyNC01LjUzNSA1LjYyNC0zLjEyNCAwLTUuNDQ1LTIuMzIxLTUuNDQ1LTUuNjI0IDAtMy4zOTIgMi4yMzItNS44MDIgNS41MzQtNS44MDIgMy4xMjUuMDg5IDUuNDQ2IDIuNDk5IDUuNDQ2IDUuODAyem0tNzMuMi41MzZjMCAyLjg1Ni0xLjk2NCA0Ljk5OS00LjczMSA1LjA4OC0yLjk0NiAwLTQuNzMxLTEuNzg1LTQuNzMxLTQuODJ2LTguNjZoLTIuNjc5djguNjZjMCA0LjQ2MyAyLjY3OSA3LjMyIDYuNzg1IDcuMzJoLjA4OWMyLjA1MyAwIDMuOTI4LS45ODIgNS4xNzgtMi41bC4wODktLjE3OS4wODkgMi40MTFoMi41VjEyOS4yNmgtMi42Nzh2OC4zOTJ6bTE4LjEyMSAzLjQ4MWMtLjk4Mi45ODItMi40MSAxLjUxOC00LjAxNyAxLjUxOC0yLjc2NyAwLTUuNTM0LTEuNjk2LTUuNTM0LTUuNjI0IDAtMy4zMDMgMi4zMjEtNS42MjQgNS41MzQtNS42MjQgMS40MjkgMCAyLjc2OC41MzYgMy44MzkgMS41MThsLjA4OS4wODkgMS42OTYtMS43ODYtLjA4OS0uMDg5Yy0xLjYwNy0xLjUxNy0zLjQ4Mi0yLjIzMi01LjYyNC0yLjIzMi00LjkxIDAtOC4yMTMgMy4zMDMtOC4yMTMgOC4xMjQgMCA1LjYyNCA0LjEwNyA4LjEyMyA4LjIxMyA4LjEyM2guMDg5YzIuMTQzIDAgNC4xOTYtLjgwMyA1LjYyNC0yLjMyMWwuMDg5LS4wODktMS43ODUtMS43ODV6bTE3LjE0LTExLjg3M2gtMy40ODJsLTYuMzM4IDYuNTE3di0xMy4wMzNoLTIuNjc4djIyLjIyOGgyLjY3OHYtNy4zMmw3LjIzMSA3LjIzLjA4OS4wOWgzLjIxNHYtLjI2OGwtOC4xMjMtOC4wMzR6Ii8+CiAgPHBhdGggZmlsbD0iI2RlNTgzMyIgZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNOTEuOTQ2IDEwNy4xMjJjMjkuNTgxIDAgNTMuNTYxLTIzLjk4IDUzLjU2MS01My41NjFTMTIxLjUyNyAwIDkxLjk0NyAwQzYyLjM2NCAwIDM4LjM4NCAyMy45OCAzOC4zODQgNTMuNTYxczIzLjk4IDUzLjU2MSA1My41NjEgNTMuNTYxeiIgY2xpcC1ydWxlPSJldmVub2RkIi8+CiAgPHBhdGggZmlsbD0iI2RkZCIgZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNOTkuNDc4IDkzLjUyMmMwLS40MTguMTAzLS41MTMtMS4yMjctMy4xNjUtMy41MzUtNy4wNzktNy4wODgtMTcuMDU5LTUuNDcyLTIzLjQ5NS4yOTQtMS4xNy0zLjMzLTQzLjMwNC01Ljg5Mi00NC42NjEtMi44NDgtMS41MTgtNi4zNTEtMy45MjUtOS41NTYtNC40Ni0xLjYyNi0uMjYtMy43NTgtLjEzOC01LjQyNS4wODctLjI5Ni4wNC0uMzA4LjU3Mi0uMDI1LjY2OCAxLjA5NC4zNyAyLjQyMyAxLjAxNCAzLjIwNiAxLjk4OC4xNDguMTg0LS4wNTEuNDc0LS4yODcuNDgyLS43MzguMDI4LTIuMDc3LjMzNy0zLjg0NCAxLjgzOC0uMjA0LjE3My0uMDM1LjQ5NS4yMjguNDQzIDMuNzk3LS43NSA3LjY3NC0uMzggOS45NiAxLjY5Ni4xNDguMTM1LjA3LjM3Ny0uMTIzLjQzQzYxLjE5IDMwLjc2IDY1LjExNyA0OC4wMSA3MC4zOTYgNjkuMTc3YzQuNjU0IDE4LjY2NiA2LjQzNSAyNC44MSA3LjAxMiAyNi43MjdhLjcyLjcyIDAgMCAwIC40MjQuNDY5YzYuODUgMi42OTcgMjEuNjQ2IDIuODA1IDIxLjY0Ni0xLjgwNXoiIGNsaXAtcnVsZT0iZXZlbm9kZCIvPgogIDxwYXRoIGZpbGw9IiNmZmYiIGQ9Ik0xMDIuMTk4IDk3LjQ5OGMtMi40MDYuOTQxLTcuMTE0IDEuMzYtOS44MzMgMS4zNi0zLjk4OCAwLTkuNzMtLjYyOC0xMS44MjEtMS41Ny0xLjI5My0zLjk3Ni01LjE2LTE2LjMwMy04Ljk3OC0zMS45NTZsLS4zNzQtMS41My0uMDAzLS4wMTJjLTQuNTQtMTguNTQyLTguMjQ4LTMzLjY4NyAxMi4wNzQtMzguNDQ1LjE4NS0uMDQzLjI3Ni0uMjY1LjE1My0uNDExLTIuMzMxLTIuNzY2LTYuNy0zLjY3My0xMi4yMjItMS43NjgtLjIyNy4wNzktLjQyNC0uMTUtLjI4My0uMzQ0IDEuMDgzLTEuNDkzIDMuMi0yLjY0IDQuMjQ0LTMuMTQ0LjIxNi0uMTA0LjIwMy0uNDItLjAyNS0uNDkxYTIzLjI5OSAyMy4yOTkgMCAwIDAtMy4xNTYtLjc1M2MtLjMxLS4wNS0uMzM4LS41OC0uMDI3LS42MjMgNy44My0xLjA1MyAxNi4wMDYgMS4yOTggMjAuMTA5IDYuNDY2YS4yNzIuMjcyIDAgMCAwIC4xNTUuMDk2YzE1LjAyNCAzLjIyNiAxNi4xIDI2Ljk3NyAxNC4zNjkgMjguMDU5LS4zNDEuMjEzLTEuNDM0LjA5LTIuODc3LS4wNy01Ljg0Ni0uNjU1LTE3LjQyMi0xLjk1LTcuODY4IDE1Ljg1Ni4wOTQuMTc2LS4wMy40MDktLjIyOC40NC01LjM4OC44MzcgMS41MTcgMTcuNzE5IDYuNTkxIDI4Ljg0eiIvPgogIDxwYXRoIGZpbGw9IiMzY2E4MmIiIGQ9Ik0xMDguOTE5IDc1LjkwNGMtMS4xNDQtLjUzLTUuNTQyIDIuNjI0LTguNDYxIDUuMDQ1LS42MS0uODYzLTEuNzYtMS40OS00LjM1NS0xLjA0LTIuMjcuMzk2LTMuNTI0Ljk0My00LjA4NCAxLjg4Ny0zLjU4NC0xLjM1OS05LjYxNC0zLjQ1Ni0xMS4wNy0xLjQzLTEuNTkzIDIuMjE0LjM5NyAxMi42ODcgMi41MTIgMTQuMDQ3IDEuMTA0LjcxIDYuMzg2LTIuNjg1IDkuMTQ0LTUuMDI2LjQ0NS42MjcgMS4xNjIuOTg2IDIuNjM0Ljk1MiAyLjIyOC0uMDUyIDUuODQxLS41NyA2LjQwMS0xLjYwOC4wMzQtLjA2My4wNjQtLjEzNy4wODktLjIyMiAyLjgzNSAxLjA2IDcuODI0IDIuMTggOC45MzkgMi4wMTQgMi45MDUtLjQzNy0uNDA1LTEzLjk5Ni0xLjc0OS0xNC42MTl6Ii8+CiAgPHBhdGggZmlsbD0iIzRjYmEzYyIgZD0iTTEwMC43MjUgODEuMjZjLjEyMS4yMTQuMjE3LjQ0LjMuNjcuNDA0IDEuMTMgMS4wNjIgNC43MjYuNTY0IDUuNjE0LS40OTguODg4LTMuNzMyIDEuMzE3LTUuNzI3IDEuMzUxcy0yLjQ0NC0uNjk1LTIuODQ4LTEuODI1Yy0uMzI0LS45MDQtLjQ4My0zLjAzLS40NzktNC4yNDctLjA4Mi0xLjgwNi41NzgtMi40NCAzLjYyNy0yLjkzNCAyLjI1Ny0uMzY1IDMuNDUuMDYgNC4xMzguNzg2IDMuMjA0LTIuMzkgOC41NDktNS43NjUgOS4wNy01LjE0OCAyLjYgMy4wNzUgMi45MjggMTAuMzk0IDIuMzY1IDEzLjM0LS4xODQuOTYyLTguNzkxLS45NTUtOC43OTEtMS45OTMgMC00LjMxMS0xLjExOS01LjQ5NC0yLjIxOS01LjYxNXpNODEuODcgNzkuOTEzYy43MDYtMS4xMTYgNi40MjIuMjcyIDkuNTYgMS42NjggMCAwLS42NDQgMi45MjIuMzgyIDYuMzY0LjMgMS4wMDctNy4yMiA1LjQ4OC04LjIwMSA0LjcxNy0xLjEzNC0uODkxLTMuMjIyLTEwLjQwNC0xLjc0LTEyLjc1eiIvPgogIDxwYXRoIGZpbGw9IiNmYzMiIGZpbGwtcnVsZT0iZXZlbm9kZCIgZD0iTTg0LjY0IDU3LjI0OWMuNDYyLTIuMDEyIDIuNjE3LTUuODAyIDEwLjMxLTUuNzEgMy44OS0uMDE2IDguNzIyLS4wMDEgMTEuOTI2LS4zNjVhNDIuODg1IDQyLjg4NSAwIDAgMCAxMC42NS0yLjU5YzMuMzMxLTEuMjcgNC41MTMtLjk4OCA0LjkyNy0uMjI3LjQ1Ni44MzUtLjA4MSAyLjI3OC0xLjI0NSAzLjYwNi0yLjIyMyAyLjUzNi02LjIxOSA0LjUwMi0xMy4yNzcgNS4wODUtNy4wNTguNTgzLTExLjczNC0xLjMxLTEzLjc0NiAxLjc3Mi0uODY4IDEuMzMtLjE5NyA0LjQ2MyA2LjYyOCA1LjQ1IDkuMjIzIDEuMzMgMTYuNzk4LTEuNjA0IDE3LjczNC4xNjhzLTQuNDU1IDUuMzgtMTMuNjkzIDUuNDU1Yy05LjIzOS4wNzYtMTUuMDA5LTMuMjM0LTE3LjA1NS00Ljg4LTIuNTk3LTIuMDg3LTMuNzU4LTUuMTMyLTMuMTYtNy43NjR6IiBjbGlwLXJ1bGU9ImV2ZW5vZGQiLz4KICA8ZyBmaWxsPSIjMTQzMDdlIiBvcGFjaXR5PSIuOCI+CiAgICA8cGF0aCBkPSJNOTYuNDA0IDM1LjI1NmMuNTE2LS44NDQgMS42NTgtMS40OTUgMy41MjgtMS40OTVzMi43NS43NDQgMy4zNTkgMS41NzNjLjEyNC4xNy0uMDY0LjM2OC0uMjU2LjI4NWwtLjE0LS4wNjFjLS42ODQtLjI5OS0xLjUyNC0uNjY2LTIuOTYzLS42ODYtMS41MzgtLjAyMi0yLjUwOC4zNjMtMy4xMi42OTUtLjIwNS4xMTItLjUzLS4xMTEtLjQwOC0uMzExem0tMjEuMDUzIDEuMDc5YzEuODE2LS43NTkgMy4yNDMtLjY2IDQuMjUyLS40MjIuMjEzLjA1LjM2LS4xNzguMTktLjMxNS0uNzgzLS42MzItMi41MzUtMS40MTYtNC44MjEtLjU2NC0yLjAzOS43Ni0zIDIuMzQtMy4wMDYgMy4zNzktLjAwMS4yNDUuNTAzLjI2NS42MzMuMDU4LjM1Mi0uNTYuOTM3LTEuMzc3IDIuNzUyLTIuMTM2eiIvPgogICAgPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNMTAxLjUyMSA0Ni43OTljLTEuNjA2IDAtMi45MDgtMS4yOTktMi45MDgtMi44OTdzMS4zMDItMi44OTcgMi45MDgtMi44OTdjMS42MDUgMCAyLjkwNyAxLjI5OSAyLjkwNyAyLjg5N3MtMS4zMDIgMi44OTctMi45MDcgMi44OTd6bTIuMDQ3LTMuODU3YS43NTIuNzUyIDAgMCAwLTEuNTA1IDAgLjc1Mi43NTIgMCAwIDAgMS41MDUgMHptLTIxLjMxIDIuOTY1YTMuMzgzIDMuMzgzIDAgMCAxLTMuMzg5IDMuMzc4Yy0xLjg3IDAtMy4zODktMS41MTMtMy4zODktMy4zNzhzMS41Mi0zLjM3OSAzLjM4OS0zLjM3OWEzLjM4NSAzLjM4NSAwIDAgMSAzLjM4OSAzLjM3OXptLS45OTktMS4xMmEuODc4Ljg3OCAwIDAgMC0xLjc1NSAwIC44NzYuODc2IDAgMCAwIDEuNzU1IDB6IiBjbGlwLXJ1bGU9ImV2ZW5vZGQiLz4KICA8L2c+CiAgPHBhdGggZmlsbD0iI2ZmZiIgZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNOTEuOTQ2IDk4LjU0NGMyNC44NDMgMCA0NC45ODMtMjAuMTQgNDQuOTgzLTQ0Ljk4MyAwLTI0Ljg0My0yMC4xNC00NC45ODMtNDQuOTgzLTQ0Ljk4My0yNC44NDMgMC00NC45ODMgMjAuMTQtNDQuOTgzIDQ0Ljk4MyAwIDI0Ljg0MyAyMC4xNCA0NC45ODMgNDQuOTgzIDQ0Ljk4M3ptMCA0LjE4NGMyNy4xNTQgMCA0OS4xNjctMjIuMDEzIDQ5LjE2Ny00OS4xNjdTMTE5LjEgNC4zOTQgOTEuOTQ2IDQuMzk0IDQyLjc4IDI2LjQwNyA0Mi43OCA1My41NnMyMi4wMTMgNDkuMTY3IDQ5LjE2NyA0OS4xNjd6IiBjbGlwLXJ1bGU9ImV2ZW5vZGQiLz4KPC9zdmc+Cg==
        
    def _direct_provider(self):
        queries = [
            f'manga "{self.title}" "chapter {self.chapter}"',
            f'manga "{self.title}" chapter {self.chapter}',
            f'manga {self.title} chapter {self.chapter}',
            f'manga {self.title}'
        ]
        with DDGS(timeout=20) as ddgs:
            for query in queries:
                results = ddgs.text(query, timelimit=100, safesearch='off')
                for r in results:
                    url = self._get_url(r['href'], r['title'])
                    if url:
                        print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
                        return url
        print("No crawlable URL found.")
        return None
        
class AutoProviderPluginBing(AutoProviderPlugin):
    def __init__(self, title, chapter, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.bing.com", logo_path="./data/BingLogo.png")
        self._download_logo_image('https://www.bing.com/rp/ZHDMbHUEYDt5NGP3ON8vXjxtCaA.png', "BingLogo", img_format='png')
        
    def _direct_provider(self):
        queries = [
            f'manga "{self.title}" "chapter {self.chapter}"',
            f'manga "{self.title}" chapter {self.chapter}',
            f'manga {self.title} chapter {self.chapter}',
            f'manga {self.title}'
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
                    print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
                    return url
        print("No crawlable URL found.")
        return None

class AutoProviderPluginManhwaClan(AutoProviderPlugin):
    def __init__(self, title, chapter, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.manhwaclan.com", logo_path="./data/ManhwaClanLogo.png")
        self._download_logo_image('https://manhwaclan.com/wp-content/uploads/2022/02/Logo_230.png', "ManhwaClanLogo", img_format='png')
        
    def _direct_provider(self):
        url = self._get_url(f'https://{self.specific_provider_website}/manga/{"-".join(self.title.lower().split())}/chapter-{self.chapter}/', f'chapter {self.chapter} {self.title}')
        if url:
            print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
            return url
        return None

class AutoProviderPluginMangaKakalot(AutoProviderPlugin):
    def __init__(self, title, chapter, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website=None, logo_path="./data/MangaKakalotLogo.png")
        self.websites = ['https://www.manga-kakalot.net/', 'https://mangakakalot.com/']
        if not self._download_logo_image(f'{self.websites[0]}themes/home/icons/logo.png', "MangaKakalotLogo", img_format='png'):
            self._download_logo_image(f'{self.websites[1]}themes/home/icons/logo.png', "MangaKakalotLogo", img_format='png')
        self.specific_provider_website = self.websites[0]
        self.manga_abbreviation = None
        
    def _switch_website(self):
        if self.specific_provider_website == self.websites[0]:
            self.specific_provider_website = self.websites[1]
        else:
            self.specific_provider_website = self.websites[0]
        print(f"Switched to {self.specific_provider_website}")
        
    def _direct_provider(self):
        if not self.manga_abbreviation:
            query = f'manga "{self.title}" site:{self.specific_provider_website} -chapter'
            results = search(query, num_results=10, advanced=True)
            for i in results:
                if self.title.lower() in i.title.lower() and not "chapter" in i.title.lower():
                    self.manga_abbreviation = i.url.split("/")[-1]
                    break  # Break the loop once the abbreviation is found

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
    def __init__(self, title, chapter, data_folder, cache_folder, provider):
        self.title = title
        self.chapter = chapter
        self.provider = provider
        self.logo_path = './data/logo3.png'
        
    def _direct_provider(self):
        pass
        
class AutoProviderPluginMangaQueen(AutoProviderPlugin):
    def __init__(self, title, chapter, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.mangaqueen.com", logo_path="./data/MangaQueenLogo.png")
        self._download_logo_image('https://mangaqueen.com/wp-content/uploads/2022/11/mangaqueen-2.png', "MangaQueenLogo", img_format='png')
        
    def _direct_provider(self):
        url = self._get_url(f'https://{self.specific_provider_website}/manga/{"-".join(self.title.lower().split())}/chapter-{self.chapter}/', f'chapter {self.chapter} {self.title}')
        if url:
            print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
            return url
        return None

class AutoProviderPluginMangaGirl(AutoProviderPlugin):
    def __init__(self, title, chapter, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.mangagirl.me", logo_path="./data/MangaGirlLogo.png")
        #self._download_logo_image('https://cdn.mangagirl.me/wp-content/uploads/2022/09/mangagirl-logo.png', "MangaGirlLogo", img_format='png')
        
    def _direct_provider(self):
        url = self._get_url(f'https://{self.specific_provider_website}/manga/{"-".join(self.title.lower().split())}/chapter-{self.chapter}/', f'chapter {self.chapter} {self.title}')
        if url:
            print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
            return url
        return None

class AutoProviderPluginMangaBuddy(AutoProviderPlugin):
    def __init__(self, title, chapter, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.mangabuddy.com", logo_path="./data/MangaBuddyLogo.png")
        self._download_logo_image('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAABYlBMVEUAAIAAAKkAAKsAAKoAAKsAAKodHbSmpuHU1PEzM7u1tebm5vdCQsAICKxsbM7a2vPGxuwPD68CAqpfX8nMzO47O70BAapcXMnPz+9SUsU2Nrz19fv////b2/P9/f7q6vjj4/aRkdqhod/f3/THx+z5+f0yMrqLi9ikpOCDg9b6+v19fdO3t+cREbDz8/uCgtWuruSNjdlERMBzc9CqquItLbkHB6zw8Prl5fbY2PLZ2fIqKriTk9s/P7+IiNcfH7SFhdbLy+0lJbZ0dNB3d9KQkNr7+/739/xZWccDA6vR0fDx8fpkZMssLLhISMKYmNwgILTa2vJ/f9RBQcDQ0O8LC64hIbVGRsHm5vY4OLze3vQoKLe/v+mXl9zc3POJidcUFLA8PL74+P3p6fdoaMwEBKt7e9PNze5BQb8cHLPp6fjy8vugoN8+Pr5UVMZWVsYFBaspKbgODq41NbseHrQJCa3K28caAAAABnRSTlMCfOb/fOfvJMB8AAABEElEQVR4AbzKU4IDUQAF0U5uzDFrbPXYtm3vfxWx8fov9VvHslxu1c3tSn0Z81heM/BacqhhwOcP+IKhcCQaizc1q6W1rb2js6u7CHp6oa8fBgaBIQ3DyCiMjReAJmByahpmZmFEczb98wuwWARLsKwVWF1bZ0PaZEvbsFMEu2mwlwLqyoP9anCQBod5cOQEjuHEAMKnZ+cXMgCA0KUJXF3DTTW4zYM+3cG9AWzpwQnsm8FjNXhKg+cUsNf0gv36Vgbe4eMzBb6+D+FHvxD/I/BeBP9sPCWXkJiUnJKaJpOewZyZJZOdk4uUYPJi8guAVGERkCgWAhIl4aUoKUpsYFM14azHQijzMjCy4tHPwgAAoVBHJ6Y0EhcAAAAASUVORK5CYII=', "MangaBuddyLogo", img_format='png')
        
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
        url = self._get_url(f'https://{self.specific_provider_website}/{"-".join(self.title.lower().split())}/chapter-{self.chapter}/', f'chapter {self.chapter} {self.title}')
        if url:
            print("Found URL:" + url) # Concatenate (add-->+) string, to avoid breaking timestamps
            return url
        return None

class AutoProviderPluginS2Manga(AutoProviderPlugin):
    def __init__(self, title, chapter, data_folder, cache_folder, provider):
        super().__init__(title=title, chapter=chapter, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.s2manga.com", logo_path="./data/S2MangaLogo.png")
        self._download_logo_image('https://s2manga.com/wp-content/uploads/2017/10/cooltext-357206071789.png', "S2MangaLogo", img_format='png')
        
    def _direct_provider(self):
        url = self._get_url(f'https://{self.specific_provider_website}/manga/{"-".join(self.title.lower().split())}/chapter-{self.chapter}/', f'chapter {self.chapter} {self.title}')
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
    def __init__(self, title, chapter, data_folder, cache_folder, provider):
        self.logo_path = './data/logo3.png'
        return
        super().__init__(title=title, chapter=chapter, data_folder=data_folder, cache_folder=cache_folder, provider=provider, specific_provider_website="www.novelcool.com", logo_path="./data/NovelCoolLogo.png")
        self._download_logo_image('https://www.novelcool.com/files/images/logo/logo_word.svg', "NovelCoolLogo", img_format='png') # https://www.novelcool.com/files/images/logo/logo.svg
        
    def _direct_provider(self):
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
