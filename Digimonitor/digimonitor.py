# Digimonitor is part of the DIGIBOOK collection.
# DIGIBOOK Copyright (C) 2024 Daniel Alcalá.
# Contact: daniel.alcala.py@gmail.com
# Public Copyright Registration Number (INDAUTOR): 03-2024-080111090400-14

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License and the GNU Affero General 
# Public Licenseas published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License and the GNU Affero General Public License
# for more details.

# You should have received a copy of the GNU General Public License and the GNU
# Affero General Public License along with this program. If not, see 
# <https://www.gnu.org/licenses/>.


import argparse
import datetime

from selenium.common.exceptions import WebDriverException
from app.services.selenium.driver.actions import FirefoxWebDriver
from app.services.utils.detected import DetectPlatform
from app.services.files.actions import DictionarySaveJSON, LogMessage
from app.services.processing.youtube import YouTubeDataFormatter
from app.services.processing.instagram import InstagramDataFormatter
from app.services.processing.tiktok import TiktokDataFormatter
from app.services.models.language import LanguageDetected
from app.services.models.sentiment import SentimentAnalyzer


def read_urls_from_file(file_path: str) -> list:
    """
    Reads URLs from a .txt file and returns a list of URLs.
    
    Parameters:
    file_path (str): Path to the .txt file containing URLs.
    
    Returns:
    list: A list of URLs read from the file.
    """
    with open(file_path, 'r') as file:
        urls = file.read().splitlines()
    return urls


def main(url: str, root_path: str = None, platform: str = 'youtube'):
    driver = None
    try:
        # Validar la plataforma
        if platform not in ['youtube', 'tiktok', 'instagram']:
            raise ValueError(f"Unsupported platform specified: '{platform}'.")

        if platform == 'instagram' and root_path is None:
            raise ValueError("The '--root' argument is required for Instagram.")

        # Inicializar el driver del navegador
        driver = FirefoxWebDriver(root_path)
        driver.StartDriver()

        # Leer URLs
        if url.endswith('.txt'):
            url_list = read_urls_from_file(url)
        else:
            url_list = [url]
        lang = LanguageDetected()
        sentiment = SentimentAnalyzer()
        # Procesar cada URL
        for current_url in url_list:
            platform_detected = DetectPlatform(current_url)
            if platform_detected == platform:
                driver.OpenPage(current_url)

                if platform == 'youtube':
                    driver.ScrollDownPageYT()
                    data = driver.ExtractDataPageYT()
                    DictionarySaveJSON(
                        data,
                        name_folder='data/youtube',
                        name_file=f'{datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}_extract_{platform}_.json'
                    )
                    formatter_data = YouTubeDataFormatter(data)
                    formatter_data = lang.format_data(formatter_data.data)
                    formatter_data = sentiment.format_data(formatter_data)
                    DictionarySaveJSON(
                        formatter_data,
                        name_folder='data/youtube',
                        name_file=f'{datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}_extract_{platform}_formatter.json'
                    )

                elif platform == 'tiktok':
                    data = driver.ExtractDataPageTK()
                    DictionarySaveJSON(
                        data,
                        name_folder='data/tiktok',
                        name_file=f'{datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}_extract_{platform}_.json'
                    )
                    formatter_data = TiktokDataFormatter(data)
                    formatter_data = lang.format_data(formatter_data.data)
                    formatter_data = sentiment.format_data(formatter_data)
                    DictionarySaveJSON(
                        formatter_data,
                        name_folder='data/tiktok',
                        name_file=f'{datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}_extract_{platform}_formatter.json'
                    )

                elif platform == 'instagram':
                    data = driver.ExtractDataPageIG()
                    DictionarySaveJSON(
                        data,
                        name_folder='data/instagram',
                        name_file=f'{datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}_extract_{platform}_.json'
                    )
                    formatter_data = InstagramDataFormatter(data)
                    formatter_data = lang.format_data(formatter_data.data)
                    formatter_data = sentiment.format_data(formatter_data)
                    DictionarySaveJSON(
                        formatter_data,
                        name_folder='data/instagram',
                        name_file=f'{datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}_extract_{platform}_formatter.json'
                    )
            else:
                LogMessage("WARNING", f'URL: {current_url} not valid for the {platform} platform')

    except ValueError as error:
        LogMessage("ERROR", str(error))
    except WebDriverException as error:
        LogMessage("WARNING", "A WebDriverException occurred: " + str(error))
    except KeyboardInterrupt:
        LogMessage("WARNING", "Program interrupted by the user.")
    finally:
        if driver:
            driver.StopDriver()
        LogMessage("OK", 'Ciao')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web data extraction tool.')
    parser.add_argument('url', help='A single URL or a .txt file with URLs (mandatory)')
    parser.add_argument('-r', '--root', default=None, help='Path to Firefox profile (optional, but required for Instagram)')
    parser.add_argument('-p', '--platform', choices=['youtube', 'tiktok', 'instagram'], required=True, help='Platform to process (mandatory)')

    args = parser.parse_args()

    main(args.url, args.root, args.platform)
