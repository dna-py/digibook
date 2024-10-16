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


class InstagramDataFormatter:
    def __init__(self, data: dict):
        """
        Initializes the InstagramDataFormatter with the path to the JSON file.

        Args:
            file_path (str): The path to the JSON file.
        """
        self.data = data
        return self.format_data()


    def _formatter_comments(self):
        # Definir una función para eliminar emojis y dejar solo texto
        def remove_emojis(comment):
            # Utilizar una expresión regular para eliminar emojis
            return re.sub(r'[^\w\s,.!?-]', '', comment)  # Mantiene letras, números, espacios y algunos signos de puntuación
        # Aplicar la función a cada comentario en la lista
        self.data['data']['comments'] = [remove_emojis(comment) for comment in self.data['data']['comments_and_emojis']]


    def _formatter_emojis(self):
        # Expresión regular para eliminar letras, símbolos, espacios en blanco, y caracteres no deseados como "@", "_", y "️"
        emoji_pattern = re.compile(r'[^ \W_@]+', flags=re.UNICODE)
        # Recorrer los comentarios y eliminar todo lo que no sea emojis o símbolos
        self.data['data']['emojis'] = [list(emoji_pattern.sub('', comment).replace(' ', '')) for comment in self.data['data']['comments_and_emojis']]
        # Filtrar caracteres no deseados, incluyendo "️"
        self.data['data']['emojis'] = [[emoji for emoji in emojis if emoji not in ['️', '@', '_', ',', '?', "🏽", "…", "“", "!", ".", "(", ")", "\"", "'", "’", "‍"]] for emojis in self.data['data']['emojis']]


    def format_data(self):
        """
        Calls all formatter methods to process the data and update the values in the data dictionary.
        """
        self._formatter_comments()
        self._formatter_emojis()
