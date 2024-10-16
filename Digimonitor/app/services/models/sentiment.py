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


# @misc{perez2021pysentimiento,
#       title={pysentimiento: A Python Toolkit for Opinion Mining and Social NLP tasks}, 
#       author={Juan Manuel Pérez and Mariela Rajngewerc and Juan Carlos Giudici and Damián A. Furman and Franco Luque and Laura Alonso Alemany and María Vanina Martínez},
#       year={2023},
#       eprint={2106.09462},
#       archivePrefix={arXiv},
#       primaryClass={cs.CL}
# }


from pysentimiento import create_analyzer


class SentimentAnalyzer:
    def __init__(self):
        """
        Initializes the SentimentAnalyzer with the sentiment analysis models for Spanish and English.
        """
        self.analyzer_es = create_analyzer(task="sentiment", lang="es")
        self.analyzer_en = create_analyzer(task="sentiment", lang="en")


    def get_sentiment_scores(self, data: dict):
        """
        Analyzes the comments and calculates the sentiment scores based on the detected language.

        Args:
            data (dict): A dictionary containing comments in 'data['comments']' and detected languages in 'data['lang']'.

        Returns:
            dict: Updated dictionary with sentiment scores added under 'data['score_sentiments']'.
        """
        # Define a function that chooses the correct analyzer based on the language
        def analyze_and_score(comment_lang):
            comment, lang = comment_lang
            if lang == 'es':
                return self._calculate_score(self.analyzer_es.predict(comment))
            elif lang == 'en':
                return self._calculate_score(self.analyzer_en.predict(comment))
            else:
                return 'EMOJI'  # No sentiment analysis for emojis

        # Use map to apply the function across comments and languages
        scores = list(map(analyze_and_score, zip(data['data']['comments'], data['data']['langs'])))
        data['data']['score_sentiments'] = scores
        return data


    def get_emotion_output(self, data: dict):
        """
        Analyzes the comments to extract the emotion output based on the detected language.

        Args:
            data (dict): A dictionary containing comments in 'data['comments']' and detected languages in 'data['lang']'.

        Returns:
            dict: Updated dictionary with emotions added under 'data['sentiments']'.
        """
        # Define a function that predicts the emotion and returns the output
        def analyze_emotion(comment_lang):
            comment, lang = comment_lang
            if lang == 'es':
                return self.analyzer_es.predict(comment).output
            elif lang == 'en':
                return self.analyzer_en.predict(comment).output
            else:
                return 'EMOJI'  # No emotion analysis for emojis

        # Use map to apply the function across comments and languages
        emotions = list(map(analyze_emotion, zip(data['data']['comments'], data['data']['langs'])))
        data['data']['sentiments'] = emotions
        return data


    def _calculate_score(self, emotion):
        """
        Calculates a score based on the emotion probabilities.

        Args:
            emotion: The result from the emotion analyzer with probability scores.

        Returns:
            float: The calculated score.
        """
        probas = emotion.probas
        pos = probas.get('POS', 0)
        neg = probas.get('NEG', 0)
        neu = probas.get('NEU', 0)

        # Composite score formula considering positive, negative, and neutral emotions
        score = (pos - neg) * (1 - neu)
        return score


    def format_data(self, data: dict):
        """
        Calls all sentiment analysis methods to process the data and update the values in the data dictionary.

        Args:
            data (dict): A dictionary containing comments in 'data['comments']' and languages in 'data['lang']'.

        Returns:
            dict: Updated dictionary with sentiment scores and emotions added.
        """
        self.get_emotion_output(data)
        return self.get_sentiment_scores(data)
