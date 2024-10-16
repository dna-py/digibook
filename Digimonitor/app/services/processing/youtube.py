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


import re


class YouTubeDataFormatter:
    def __init__(self, data: dict):
        """
        Initializes the YouTubeDataFormatter with the path to the JSON file.

        Args:
            file_path (str): The path to the JSON file.
        """
        self.data = data
        return self.format_data() 


    def _formatter_count_subscribers(self):
        """
        Processes a string containing a numeric value followed by a common unit of measure 
        (such as 'M' for millions or 'K' for thousands) and removes irrelevant words 
        'subscribers', 'suscriptores', etc.

        Args:
            value (str): The string containing the number and units or irrelevant words.

        Returns:
            float: The transformed numeric value or 0 if the input is not a valid number.
        """
        value = self.data.get('count_subscribers', '')
        value = value.replace(',', '.').strip().lower()

        for word in ['subscribers', 'suscriptores', 'de']:
            value = value.replace(word, '').strip()
        if 'm' in value:
            value = value.replace('m', '').strip()
            self.data['count_subscribers'] = float(value) * 1_000_000
        elif 'k' in value:
            value = value.replace('k', '').strip()
            self.data['count_subscribers'] = float(value) * 1_000
        else:
            try:
                self.data['count_subscribers'] = float(value)
            except ValueError:
                self.data['count_subscribers'] = 0


    def _formatter_count_likes(self):
        """
        Extracts the numerical count of likes from the loaded data.

        Returns:
            int: The extracted count of likes as an integer, or 0 if no valid number is found.
        """
        if 'count_likes' in self.data:
            text = self.data['count_likes']
            match = re.search(r'(\d{1,3}(?:,\d{3})*)', text)
            if match:
                self.data['count_likes'] = float(match.group(0).replace(',', ''))
            else:
                self.data['count_likes'] = 0
        else:
            self.data['count_likes'] = 0


    def _formatter_count_comment(self):
        """
        Extracts the numerical count of comments from the loaded data.

        Returns:
            int: The extracted count of comments as an integer, or 0 if no valid number is found.
        """
        if 'count_comments' in self.data:
            text = self.data['count_comments']
            match = re.search(r'(\d+)', text)
            if match:
                self.data['count_comments'] = float(match.group(0))
            else:
                self.data['count_comments'] = 0
        else:
            self.data['count_comments'] = 0


    def _formatter_views(self):
        """
        Extracts the numerical count of views from the loaded data.

        Returns:
            int: The extracted count of views as an integer, or 0 if no valid number is found.
        """
        if 'count_views' in self.data:
            text = self.data['count_views']
            match = re.search(r'(\d{1,3}(?:,\d{3})*)', text)
            if match:
                self.data['count_views'] = float(match.group(0).replace(',', ''))
            else:
                self.data['count_views'] = 0
        else:
            self.data['count_views'] = 0


    def _formatter_emojis_list(self):
        pattern = re.compile(r'emoji_u([0-9a-fA-F_]+)\.png')
        def unicode_to_emoji(unicode_code):
            try:
                # Convierte el código Unicode con múltiples partes a un emoji
                code_point = int(unicode_code, 16)
                return chr(code_point)
            except (ValueError, OverflowError):
                # Si ocurre un error, omitir el código
                return None
        def extract_emoji_codes(data):
            codes = []
            for comment, emojis in data["comments_and_emojis"]:
                for emoji_url in emojis:
                    match = pattern.search(emoji_url)
                    if match:
                        # Cambiar los guiones bajos por el formato adecuado
                        code = match.group(1).replace('_', '')
                        codes.append(code)
            return codes

        # Extraer y convertir códigos de emoji
        emoji_codes = extract_emoji_codes(self.data["data"])

        # Mapear códigos de emoji a emojis
        emoji_map = {code: unicode_to_emoji(code) for code in emoji_codes}

        # Actualizar las URLs en el JSON con emojis
        updated_comment_and_emojis = []
        for comment, emojis in self.data["data"]["comments_and_emojis"]:
            updated_emojis = []
            for url in emojis:
                match = pattern.search(url)
                if match:
                    code = match.group(1).replace('_', '')
                    emoji = emoji_map.get(code)
                    if emoji is not None:
                        updated_emojis.append(emoji)
                # Si url no se puede mapear, omitirlo en la lista de emojis
            updated_comment_and_emojis.append([comment, updated_emojis])
        
        self.data["data"]["comments_and_emojis"] = updated_comment_and_emojis


    def _formatter_comments(self):
        self.data['data']['comments'] = [item[0] for item in self.data["data"]["comments_and_emojis"]]


    def _formatter_emojis(self):
        self.data['data']['emojis'] = [item[1] for item in self.data["data"]["comments_and_emojis"]]


    def format_data(self):
        """
        Calls all formatter methods to process the data and update the values in the data dictionary.
        """
        self._formatter_count_subscribers()
        self._formatter_count_likes()
        self._formatter_count_comment()
        self._formatter_views()
        self._formatter_emojis_list()
        self._formatter_comments()
        self._formatter_emojis()
