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


import streamlit as st


from app.src.modules import *


def body():

    with st.sidebar:
        output_folder = './data'
        json_file = select_json(output_folder)

    tab1, tab2 = st.tabs(["Comments", "Report"])
    with tab1:

        st.json(json_file, expanded=False)
        st.write('---')

        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                df = select_df(json_file)
                if 'emotion_comment' in df.columns:
                    emotion_filter = filter_emotion()
                    filter_df_emotion = df['emotion_comment'].isin(emotion_filter)
                    df_filter = df[filter_df_emotion]
                else:
                    df_filter = df
                words_filter = filter_words()
                filter_df_words = df_filter['comments'].str.contains('|'.join(words_filter), case=False)
                df_filter = df_filter[filter_df_words]
            with col2:
                st.dataframe(df_filter)

        if 'emotion_comment' in df.columns:
            with st.expander("Análisis de sentimiento en comentarios", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    pie_chart_emotions(df_filter)
                with col2:
                    box_plot_emotions(df_filter)

        with st.expander("Comentarios", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                bar_chart_top_words(df_filter)
            with col2:
                wordcloud_words(df_filter)

        if not df_filter['emojis'].str.contains('https', na=False).any():
            with st.expander("Emojis", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    bar_chart_top_emoji(df_filter)
                with col2:
                    wordcloud_emojis(df_filter)

    with tab2:

        pass
