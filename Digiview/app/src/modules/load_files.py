# Digiview is part of the DIGIBOOK collection.
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


import os
import json


import pandas as pd
import streamlit as st


def select_json(output_folder):
    json_files = [f for f in os.listdir(output_folder) if f.endswith(".json")]
    selected_file = st.selectbox("Select a JSON file:", 
                            json_files
                            )
    with open(os.path.join(output_folder, selected_file), "r", encoding='utf-8') as document:
        data = json.load(document)
    return data


def select_df(json_data):
    data = {
        'usernames': json_data["data"]["usernames"],
        'comments': json_data["data"]["comments"],
        'emojis': json_data["data"]["emojis"],
    }
    if 'n_likes' in json_data["data"]:
        data['n_likes'] = json_data["data"]["n_likes"]
    if 'n_responses' in json_data["data"]:
        data['n_responses'] = json_data["data"]["n_responses"]
    if 'date' in json_data["data"]:
        data['date'] = json_data["data"]["date"]
    if 'langs' in json_data["data"]:
        data['langs'] = json_data["data"]["langs"]
    if 'sentiments' in json_data["data"]:
        data['sentiments'] = json_data["data"]["sentiments"]
    if 'score_sentiments' in json_data["data"]:
        data['score_sentiments'] = json_data["data"]["score_sentiments"]

    df = pd.DataFrame(data)
    return df
