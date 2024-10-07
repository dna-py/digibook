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
        'usernames': json_data["data"]["username"],
        'comments': [item[0] for item in json_data["data"]["comment_and_emojis"]],
        'emojis': [item[1] for item in json_data["data"]["comment_and_emojis"]],
        'date_comment': json_data["data"]["date"],
        'likes_comment': json_data["data"]["n_like"]
    }
    if 'n_response' in json_data["data"]:
        data['n_response'] = json_data["data"]["n_response"]
    if 'lang' in json_data["data"]:
        data['lang'] = json_data["data"]["lang"]
    if 'emotion_comment' in json_data["data"]:
        data['emotion_comment'] = json_data["data"]["emotion_comment"]
    if 'score_emotion' in json_data["data"]:
        data['score_emotion'] = json_data["data"]["score_emotion"]

    df = pd.DataFrame(data)
    df['emojis'] = df['emojis'].apply(lambda x: ''.join(x))
    df["likes_comment"] = df["likes_comment"].replace('', "0")
    return df
