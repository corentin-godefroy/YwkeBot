import json
import math
import os
import re
from collections import Counter
from xxlimited_35 import error

letter_frequency_deviation_limit = 3
probability_frequency_deviation_bound = 3

frequencies = {
    'A': 8.2,
    'B': 1.5,
    'C': 2.8,
    'D': 4.3,
    'E': 12.7,
    'F': 2.2,
    'G': 2.0,
    'H': 6.1,
    'I': 7.0,
    'J': 0.15,
    'K': 0.77,
    'L': 4.0,
    'M': 2.4,
    'N': 6.7,
    'O': 7.5,
    'P': 1.9,
    'Q': 0.095,
    'R': 6.0,
    'S': 6.3,
    'T': 9.1,
    'U': 2.8,
    'V': 0.98,
    'W': 2.4,
    'X': 0.15,
    'Y': 2.0,
    'Z': 0.074
}

def shannon_entropy(cypher: str):
    """
    Calculate the Shannon entropy index of the cyphered input text. Must be between 3.5 and 5.
    :param cypher: str contaning the cyphered text
    :return: number representing the
    """

    # Calculate frequency of each character
    freq = Counter(cypher)

    # Total number of characters
    total_chars = len(cypher)

    # Calculate the probability of each character
    probabilities = [freq[char] / total_chars for char in freq]

    # Calculate entropy
    entropy = -sum(p * math.log2(p) for p in probabilities)

    return entropy

def letters_frequency(cypher):
    # Calculate frequency of each character

    freq = Counter(cypher.upper())

    # Total number of characters
    total_chars = len(cypher)

    # Calculate the probability of each character and keep the letter as key
    probabilities = {char: freq[char] * 100 / total_chars for char in freq}
    difference = {char: probabilities.get(char, 0) - frequencies.get(char, 0) for char in
                  set(frequencies) | set(probabilities)}
    return difference

def common_dictionary_analysis(cypher):
    with open(os.path.join(os.getcwd(), "dictionary.json"), "r") as dictionary:
        dict = json.load(dictionary)

        frequency = letters_frequency(cypher)
        splited_cypher = re.sub('[^A-Za-z0-9]+', ' ', cypher.lower()).strip().split(' ')

        recognised = 0
        unrecognised = 0

        unrecognised_words = []

        if len(splited_cypher) > 1:
            for word in splited_cypher:
                try:
                    dict[word]
                except Exception:
                    unrecognised = unrecognised + 1
                    if unrecognised_words.count(word) == 0:
                        unrecognised_words.append(word)
                else:
                    recognised = recognised + 1

        print(unrecognised_words)

        return recognised, unrecognised



def custom_dictionary_analysis(cypher):
    pass

def evaluate_shannon(value: float):
    if value < 5 and value > 3.5:
        return True
    return False

def evaluate_letters_frequency(text_frequency: dict):
    deviation = 0
    for char in text_frequency:
        if char.isalpha():
            if text_frequency[char] < -probability_frequency_deviation_bound or text_frequency[char] > probability_frequency_deviation_bound:
                deviation = deviation + 1

    return False if deviation > letter_frequency_deviation_limit else True