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
import random


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from app.services.files.actions import LogMessage


def ExtractDataPageTiktok(driver: webdriver.Firefox):
    iteration_count = 0
    data = {}
    previous_wait_time = None
    tolerance = 0.01
    last_valid_data = None
    attempts = 0 
    exit_process = False

    try:
        metadata = extract_metadata(driver)
        while True:
            try:
                for _ in range(6):
                    if _check_captcha_exists(driver):
                        print('Captcha detected. Please close the captcha window manually.')
                        input('Press Enter after you have closed the captcha window to continue...')
                        while _check_captcha_exists(driver):
                            print('Captcha still present. Please close it.')
                            input('Press Enter after you have closed the captcha window to continue...')

                    if _check_login(driver):
                        input('Press Enter after you have closed the login window to continue...')
                        while _check_login(driver):
                            print('Login still present. Please close it.')
                            input('Press Enter after you have closed the login window to continue...')
                        if _check_main_page(driver):
                            driver.back()
                            time.sleep(4)
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(1)

                    if _check_main_page(driver):
                        driver.back()
                        time.sleep(4)
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)

                    if _check_without_login(driver):
                        time.sleep(1)
                        try:
                            xpath = '//div[@data-e2e="channel-item"]'
                            driver.find_element(By.XPATH, xpath).click()
                        except:
                            pass
                    driver.execute_script("window.scrollBy(0, 420);")
                    time.sleep(.3)

                new_wait_time = random.uniform(1.5, 2)
                while previous_wait_time is not None and abs(new_wait_time - previous_wait_time) < tolerance:
                    new_wait_time = random.uniform(2, 3)
                LogMessage("INFO", f'Waiting for {new_wait_time:.2f} seconds before the next iteration.')
                time.sleep(new_wait_time)

                previous_wait_time = new_wait_time
                iteration_count += 1

                if iteration_count >= 1:
                    LogMessage("INFO", "Data extraction in progress, please wait...")
                    try:
                        if _check_main_page(driver):
                            driver.back()
                            driver.execute_script("window.scrollBy(0, 420);")
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(1)
                        else: 
                            try:
                                data = extract_all_data(driver)
                            except:
                                LogMessage("WARNING", "StaleElementReferenceException caught. Trying to refresh the page.")
                                driver.back()
                                time.sleep(4)
                                driver.execute_script("window.scrollBy(0, 420);")
                                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                time.sleep(1)
                                continue  # Repetir el ciclo para intentar nuevamente

                            username = len(data['data'].get('usernames', []))
                            comments = len(data['data'].get('comments_and_emojis', []))
                            n_likes = len(data['data'].get('n_likes', []))

                            LogMessage("INFO", f'Size of "usernames": {username}')
                            LogMessage("INFO", f'Size of "comments_and_emojis": {comments}')
                            LogMessage("INFO", f'Size of "n_likes": {n_likes}')

                            # Verificar si todos los conteos son iguales
                            if username == comments == n_likes:
                                LogMessage("INFO", "All counts are equal, continuing the process.")

                                # Verificar si las longitudes de `data` son iguales a `last_valid_data`
                                if last_valid_data and _compare_data_lengths(data, last_valid_data):
                                    attempts += 1
                                    LogMessage("INFO", f'Data is the same as last_valid_data in terms of length. Attempts: {attempts}')
                                    if attempts >= 3:
                                        LogMessage("INFO", "Data lengths have been identical for 3 consecutive iterations. Stopping the process.")
                                        break
                                else:
                                    attempts = 0  # Reiniciar intentos si hay cambios
                                
                                # Lógica para preguntar al usuario si continuar
                                if username > (200 * ((username // 200) + 1)):
                                    response = input(f"Current count is {username}. Enter 'y' to continue or 'n' to break: ")
                                    if response.lower() == 'y':
                                        LogMessage("INFO", f"Continuing the process with count: {username}")
                                    else:
                                        exit_process = True  # Establecer la variable de control para salir
                                        break  # Salir del bucle si el usuario elige no continuar

                                if exit_process:  # Verificar si se debe salir del proceso completo
                                    LogMessage("INFO", "Exiting the entire process as requested by the user.")
                                    break  # Salir del bucle principal y detener el scrolling

                                last_valid_data = data
                                continue  # Si todo coincide, continuar
                            else:
                                LogMessage("INFO", "Data inconsistency detected! The counts are not equal:")
                                LogMessage("INFO", f"Usernames: {username}, Comments: {comments}, Likes: {n_likes}")
                                if last_valid_data:
                                    LogMessage("INFO", "Using the last valid data.")
                                    data = last_valid_data
                                break
                    except Exception as error:
                        LogMessage("WARNING", f"An error occurred: {str(error)}")
                        continue

            except Exception as error:
                print(f'An error occurred: {error}')
                metadata.update(data)
                return metadata
            finally:
                LogMessage("INFO", "Scroll operation reset.")
    finally:
        LogMessage("INFO", "Scroll operation finished.")
        LogMessage("INFO", f'Size of "usernames": {len(data.get("data", {}).get("usernames", []))}')
        LogMessage("INFO", f'Size of "comments_and_emojis": {len(data.get("data", {}).get("comments_and_emojis", []))}')
        LogMessage("INFO", f'Size of "n_likes": {len(data.get("data", {}).get("n_likes", []))}')
        metadata.update(data)
        return metadata


def _compare_data_lengths(data, last_valid_data):
    keys_to_compare = ['usernames', 'comments_and_emojis', 'n_likes', 'n_response', 'date']
    for key in keys_to_compare:
        if len(data['data'].get(key, [])) != len(last_valid_data['data'].get(key, [])):
            return False
    return True


def extract_all_data(driver) -> dict:
    """
    Extracts data from a TikTok video page using the specified WebDriver instance.

    This function retrieves various details about the video. The extracted
    data is returned as a dictionary.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the Instagram page.

    Returns:
        dict: A dictionary containing extracted data, including:
        - data (dict): Dictionary containing details about comments, including:
            - usernames (list of str): Usernames of commenters.
            - comments_and_emojis (list of list): Comment and emojis used in comments.
            - n_likes (list of str): Number of likes on each comment.
            - n_response (list of str): Number of responses to each comment.
            - date (list of str): Dates of each comment.
    """
    try:
        data = {
            "data": {
                "usernames": _extract_usernames(driver),
                "comments_and_emojis": _extract_comments(driver),
                "n_likes": _extract_n_likes(driver),
                # "n_response": _extract_n_responses(driver),
                # "date": _extract_dates(driver)
            }
        }
        return data
    except:
        raise


def extract_metadata(driver) -> dict:
    """
    Extracts data from a TikTok video page using the specified WebDriver instance.

    This function retrieves various details about the video. The extracted
    data is returned as a dictionary.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the TikTok page.

    Returns:
        dict: A dictionary containing extracted data, including:
            - date_scraping (str): Timestamp of when the data was scraped.
            - url_post (str): The URL of the post.
            - description (str): Description of the video.
            - upload (str): Upload date of the video.
            - count_likes (str): Number of likes for the video.
            - count_comments (str): Number of comments on the video.
            - count_saved (str): Number of saved for the video.
            - count_share (str): Number of share for the video.
    """
    metadata = {
        "date_scraping": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url_post": _extract_url_post(driver),
        'description': _extract_description(driver),
        "upload": _extract_upload(driver),
        "count_likes": _extract_count_likes(driver),
        "count_comments": _extract_count_comments(driver),
        "count_saved": _extract_count_saved(driver),
        "count_share": _extract_count_share(driver),
    }
    return metadata


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


def _extract_description(driver: webdriver.Firefox) -> str:
    """
    Extracts the description from the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        str: The description of the video.
    """
    xpath = '//span[@class="css-j2a19r-SpanText efbd9f0"]'
    try:
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath '_extract_description' not found.")
        return 'None'
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_description'. Error: {str(error)}")
        raise


def _extract_upload(driver: webdriver.Firefox) -> str:
    """
    Extracts the upload date of the video from the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        str: The upload date, or 'None' if unable to extract.
    """
    xpath = '//span[@class="css-5set0y-SpanOtherInfos evv7pft3"]//span[last()]'
    try:
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath in '_extract_upload' not found.")
        return 'None'
    except Exception as error:
        print("WARNING", f"An error occurred in function '_extract_upload'. Error: {str(error)}")
        raise


def _extract_count_likes(driver: webdriver.Firefox) -> str:
    """
    Extracts the number of likes for the video from the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        str: The number of likes.
    """
    try:
        xpath = '//strong[@data-e2e="like-count"]'
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        print("WARNING", f"Element with XPath in '_extract_count_likes' not found.")
        return 'None'
    except Exception as error:
        print("WARNING", f"An error occurred in function '_extract_count_likes'. Error: {str(error)}")
        raise


def _extract_count_comments(driver: webdriver.Firefox) -> str:
    """
    Extracts the number of comments on the video from the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        str: The number of comments.
    """
    try:
        xpath = '//strong[@data-e2e="comment-count"]'
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        print("WARNING", f"Element with XPath in '_extract_count_likes' not found.")
        return 'None'
    except Exception as error:
        print("WARNING", f"An error occurred in function '_extract_count_likes'. Error: {str(error)}")
        raise


def _extract_count_saved(driver: webdriver.Firefox) -> str:
    """
    Extracts the number of saved on the video from the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        str: The number of saved.
    """
    try:
        xpath = '//strong[@data-e2e="undefined-count"]'
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        print("WARNING", f"Element with XPath in '_extract_count_saved' not found.")
        return 'None'
    except Exception as error:
        print("WARNING", f"An error occurred in function '_extract_count_saved'. Error: {str(error)}")
        return 'None'


def _extract_count_share(driver: webdriver.Firefox) -> str:
    """
    Extracts the number of share on the video from the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        str: The number of saved.
    """
    try:
        xpath = '//strong[@data-e2e="share-count"]'
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        print("WARNING", f"Element with XPath in '_extract_count_share' not found.")
        return 'None'
    except Exception as error:
        print("WARNING", f"An error occurred in function '_extract_count_share'. Error: {str(error)}")
        return 'None'


def _extract_n_likes(driver: webdriver.Firefox) -> list:
    """
    Extracts the number of likes from the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        list: A list of like counts.
    """
    try:
        elements = []
        xpath = '//div[@class="css-13wx63w-DivCommentObjectWrapper ezgpko42"]'
        for element in driver.find_elements(By.XPATH, xpath):
            xpath1 = './/div[@class="css-1nd5cw-DivLikeContainer edeod5e0"]'
            item = element.find_element(By.XPATH, xpath1)
            value = item.text or item.get_attribute('aria-label')
            elements.append(value)
        return elements
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath '_extract_n_likes' not found.")
        return elements
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_n_likes'. Error: {str(error)}")
        raise


def _extract_usernames(driver: webdriver.Firefox) -> list:
    """
    Extracts usernames from comments on the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        list: A list of usernames.
    """
    try:
        elements = []
        xpath = '//div[@class="css-13wx63w-DivCommentObjectWrapper ezgpko42"]'
        header_elements = driver.find_elements(By.XPATH, xpath)
        for element in header_elements:
            xpath = './/a'
            item = element.find_element(By.XPATH, xpath)
            value = item.get_attribute('href')
            elements.append(value)
        return elements
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath '_extract_usernames' not found.")
        return elements
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_usernames'.Error: {str(error)}")
        raise


def _extract_comments(driver: webdriver.Firefox) -> list:
    """
    Extracts comments from the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        list: A list of comments.
    """
    try:
        elements = []
        xpath = '//div[@class="css-13wx63w-DivCommentObjectWrapper ezgpko42"]'
        for element in driver.find_elements(By.XPATH, xpath):
            xpath1 = './/span//span'
            value = element.find_element(By.XPATH, xpath1)
            elements.append(value.text)
        return elements
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath '_extract_comments' not found.")
        return elements
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_comments'. Error: {str(error)}")
        raise


def _extract_dates(driver: webdriver.Firefox) -> list:
    """
    Extracts dates from the comments on the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        list: A list of dates.
    """
    try:
        elements = []
        xpath = '//div[@class="css-13wx63w-DivCommentObjectWrapper ezgpko42"]//div[@class="css-2c97me-DivCommentSubContentWrapper e1970p9w6"]'
        header_elements = driver.find_elements(By.XPATH, xpath)
        for element in header_elements:
            xpath = './/span'
            item = element.find_element(By.XPATH, xpath)
            value = item.text
            elements.append(value)
        return elements
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath '_extract_dates' not found.")
        return elements
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_dates'. Error: {str(error)}")
        raise


def _extract_n_responses(driver) -> list:
    """
    Extracts the number of responses from comments on the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        list: A list of response counts or zeros.
    """
    try:
        elements = []
        xpath = '//div[@class="css-13wx63w-DivCommentObjectWrapper ezgpko42"]'
        header_elements = driver.find_elements(By.XPATH, xpath)
        for element in header_elements:
            try:
                xpath = './/div[@class="css-1idgi02-DivViewRepliesContainer ezgpko45"]//span'
                item = element.find_element(By.XPATH, xpath)
                value = item.text
                elements.append(value)
            except NoSuchElementException:
                elements.append(0)
        return elements
    except NoSuchElementException:
        LogMessage("WARNING", f"Element with XPath '_extract_dates' not found.")
        return elements
    except Exception as error:
        LogMessage("WARNING", f"An error occurred in function '_extract_dates'. Error: {str(error)}")
        return elements


def _check_captcha_exists(driver: webdriver.Firefox) -> bool:
    """
    Checks if a captcha is present on the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        bool: True if captcha exists, otherwise False.
    """
    try:
        xpath = '//span[@class="cap-flex cap-items-center "]'
        driver.find_element(By.XPATH, xpath)
        return True
    except NoSuchElementException:
        try:
            xpath = driver.find_element(By.XPATH, '//button[contains(@class,"captcha_verify_container")]')
            driver.find_element(By.XPATH, xpath)
            return True
        except NoSuchElementException:
            return False


def _check_login(driver: webdriver.Firefox) -> bool:
    """
    Checks if a login form is present on the TikTok post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        bool: True if login form exists, otherwise False.
    """
    try:
        xpath = '//a[@id="loginContainer"]'
        driver.find_element(By.XPATH, xpath)
        return True
    except NoSuchElementException:
        return False


def _check_main_page(driver: webdriver.Firefox) -> bool:
    """
    Checks if the main page content is present.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        bool: True if main page content exists, otherwise False.
    """
    try:
        xpath = '//div[@id="main-content-others_homepage"]'
        driver.find_element(By.XPATH, xpath)
        return True
    except NoSuchElementException:
        return False


def _check_without_login(driver: webdriver.Firefox) -> bool:
    """
    Checks if the login container is not present on the page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the page.

    Returns:
        bool: True if login container does not exist, otherwise False.
    """
    try:
        xpath = '//div[@id="loginContainer"]'
        driver.find_element(By.XPATH, xpath)
        return True
    except NoSuchElementException:
        return False
