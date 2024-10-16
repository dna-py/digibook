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


import datetime
import time


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from app.services.files.actions import LogMessage


def ExtractDataPageInstagram(driver: webdriver.Firefox) -> dict:
    """
    Extracts data from a Instagram post using the specified WebDriver instance.

    This function retrieves various details about the post. The extracted
    data is returned as a dictionary.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the Instagram page.

    Returns:
        dict: A dictionary containing extracted data, including:
            - date_scraping (str): Timestamp of when the data was scraped.
            - url_post (str): The URL of the post.
            - id_channel (str): Unique ID of the channel (URL).
            - description (str): Description of the post.
            - count_comments (str): Number of comments on the video.
            - count_likes (str): Number of likes for the post.
            - upload (str): Upload date of the video.
            - data (dict): Dictionary containing details about comments, including:
                - usernames (list of str): Usernames of commenters.
                - comments_and_emojis (list of list): Comment and emojis used in comments.
    """
    _scroll_down_page(driver)
    data = {
        "date_scraping": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url_post": _extract_url_post(driver),
        "id_channel": _extract_id_channel(driver),
        'description': _extract_description(driver),
        "count_comments": _extract_count_comments(driver),
        "count_likes": _extract_count_likes(driver),
        "upload": _extract_upload(driver),
        "data": {
            "usernames": _extract_usernames(driver),
            "comments_and_emojis": _extract_comments(driver),
        }
    }
    # Print sizes of extracted data for verification
    username = len(data['data'].get('usernames', []))
    comments_and_emojis = len(data['data'].get('comments_and_emojis', []))
    LogMessage("INFO", f'Size of "username": {username}')
    LogMessage("INFO", f'Size of "comments_and_emojis": {comments_and_emojis}')
    return data


def _scroll_down_page(driver):
    print("Scrolling down the page to load comments")
    try:
        xpath = '//div[@class="x5yr21d xw2csxc x1odjw0f x1n2onr6"]'
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        prev_scroll_top = -1
        attempts = 0

        while attempts < 3:
            script = """
            var elem = arguments[0];
            return {
                scrollTop: elem.scrollTop
            };
            """
            heights = driver.execute_script(script, element)
            scroll_top = heights['scrollTop']
            LogMessage("INFO", f"scrollTop: {scroll_top}")

            # Check if scrolling stops
            if scroll_top == prev_scroll_top:
                attempts += 1
                LogMessage("INFO", f"The div size is no longer growing, attempt {attempts} of 3.")
                if attempts == 3:
                    LogMessage("INFO", "No more content to load after 3 attempts.")
                    break
            else:
                attempts = 0  # Reset the counter if there is a scroll change

            prev_scroll_top = scroll_top

            # Perform the scroll
            driver.execute_script("arguments[0].scrollTop += arguments[0].clientHeight;", element)
            time.sleep(1)
        LogMessage("INFO", "Scrolling complete or no more content to load.")
    except:
        LogMessage("WARNING", f"Not scrolling available")


def _extract_url_post(driver: webdriver.Firefox) -> str:
    """
    Extracts the current URL of the post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        str: The current URL of the post.
    """
    try:
        return driver.current_url
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_url_post'. Error: {str(error)}")
        return 'None'


def _extract_id_channel(driver: webdriver.Firefox) -> str:
    """
    Extracts the ID of the channel from the Instagram page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        str: The ID of the channel.
    """
    try:
        item = driver.find_element(By.CSS_SELECTOR, 'link[rel="canonical"]')
        text = item.get_attribute('href')
        return text
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath '_extract_id_channel' not found.")
        return 'None'
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_id_channel'. Error: {str(error)}")
        return 'None'


def _extract_description(driver: webdriver.Firefox) -> list:
    """
    Extracts the description from the Instagram post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        str: Containing the text of the description.
    """
    try:
        xpath = '//span[contains(@class, "x1lliihq x1plvlek xryxfnj")]//span[contains(@class, "x193iq5w xeuugli x1fj9vlw")]'
        elements = driver.find_elements(By.XPATH, xpath)
        descriptions = [element.text for element in elements]
        return descriptions[-2]
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath '_extract_description' not found.")
        return []
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_description'. Error: {str(error)}")
        return []


def _extract_upload(driver: webdriver.Firefox) -> str:
    """
    Extracts the upload date of the video from the Instagram post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        str: The upload date, or 'None' if unable to extract.
    """
    try:
        xpath = '//time[contains(@class, "x1p4m5qa")]'
        item =  driver.find_element(By.XPATH, xpath)
        text = item.get_attribute('datetime')
        return text
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath in '_extract_upload' not found.")
        return 'None'
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_upload'. Error: {str(error)}")
        return 'None'


def _extract_count_comments(driver: webdriver.Firefox) -> str:
    """
    Extracts the number of comments on the video from the Intsgaram post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        str: The number of comments.
    """
    try:
        item = driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
        text = item.get_attribute('content')
        return text
    except NoSuchElementException:
        print("WARNING", f"Element with XPath '_extract_count_comments' not found.")
        return 'None'
    except Exception as error:
        print("WARNING", f"An error occurred in function '_extract_count_comments'. Error: {str(error)}")
        return 'None'


def _extract_count_likes(driver: webdriver.Firefox) -> str:
    """
    Extracts the number of likes for the video from the Instagram post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        str: The number of likes.
    """
    try:
        xpath = '//span[contains(@class, "html-span xdj266r x11i5rnm")]'
        element = driver.find_element(By.XPATH, xpath)
        text = element.text
        return text
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath in '_extract_count_likes' not found.")
        return 'None'
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_count_likes'. Error: {str(error)}")
        return 'None'


def _extract_usernames(driver: webdriver.Firefox):
    """
    Extracts the usernames of commenters from the Instagram post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        list of str: List of usernames.
    """
    try:
        elements = []
        xpath = '//div[contains(@class, "x9f619 xjbqb8w x78zum5")]//div[@class=""]//span[@class="xt0psk2"]//a[contains(@class, "x1a2a7pz notranslate _a6hd")]'
        items = driver.find_elements(By.XPATH, xpath)
        for i in items:
            text = i.get_attribute('href')
            elements.append(text)
        return elements
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath in '_extract_usernames' not found.")
        return 'None'
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_usernames'. Error: {str(error)}")
        return 'None'


def _extract_comments(driver: webdriver.Firefox) -> list:
    """
    Extracts comments from the Instagram post

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        list: A list of comments.
    """
    try:
        elements = []
        xpath = '//div[contains(@class, "x9f619 xjbqb8w x78zum5")]//div[@class=""]//div//div[2]'
        for element in driver.find_elements(By.XPATH, xpath):
            xpath1 = './/span[contains(@style, "base-line-clamp")]'
            try:
                item = element.find_element(By.XPATH, xpath1)
                text = item.text
                elements.append(text)
            except NoSuchElementException:
                elements.append('None')

        # Delete the last (n) items from the list
        if len(elements) >= 3:
            del elements[-3:]

        return elements
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath in '_extract_comments' not found.")
        return 'None'
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_comments'. Error: {str(error)}")
        return 'None'
