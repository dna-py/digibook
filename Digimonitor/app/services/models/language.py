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


# @misc{ercdidip2022,
#   title={langdetect (Revision 0215f72)},
#   author={Kovács, Tamás, Atzenhofer-Baumgartner, Florian, Aoun, Sandy, Nicolaou, Anguelos, Luger, Daniel, Decker, Franziska, Lamminger, Florian and Vogeler, Georg},
#   year         = { 2022 },
#   url          = { https://huggingface.co/ERCDiDip/langdetect },
#   doi          = { 10.57967/hf/0135 },
#   publisher    = { Hugging Face }
# }


import re
from transformers import pipeline


class LanguageDetected:
    def __init__(self):
        """
        Initializes the InstagramDataFormatter with the path to the JSON file.
        """
        self.classificator = pipeline("text-classification", model="ERCDiDip/langdetect") # classificator lang


    def _get_lang_comments(self, data: dict):
        patron_letras = re.compile(r'[a-zA-Z]+')

        # Función lambda para clasificar el idioma del comentario
        classify_lang = lambda comment: (
            "en" if patron_letras.search(comment) and self.classificator(comment)[0]['label'] == "en"
            else ("es" if patron_letras.search(comment) else "emoji")
        )

        # Aplicar la clasificación de forma más eficiente usando map
        langs = list(map(classify_lang, data['data']['comments']))
        data['data']['langs'] = langs
        return data


    def format_data(self, data):
        """
        Calls all formatter methods to process the data and update the values in the data dictionary.
        """
        return self._get_lang_comments(data)
