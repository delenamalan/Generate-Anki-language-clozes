"""
Modified from https://sookocheff.com/post/language/bulk-generating-cloze-deletions-for-learning-a-language-with-anki/
"""
import csv
import random
import string

def find_cloze(sentence, frequency_list):
    """
    Return the least frequently used word in the sentence by.
    If no word is found in the frequency list, return a random word.
    If no acceptable word is available (even random), return None
    """
    # Remove punctuation
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    sentence = sentence.translate(translator)

    max_frequency = 50001  # Frequency list has 50,000 entries
    min_frequency = max_frequency

    min_word = None
    valid_words = []
    for word in sentence.split():
        if word.isupper() or word.istitle():
            continue  # Skip proper nouns
        if len(word) <= 2:
            continue  # Skip tiny words

        valid_words.append(word)

        word_frequency = int(frequency_list.get(word.lower(), max_frequency))
        if word_frequency < min_frequency:
            min_word = word
            min_frequency = word_frequency

    if min_word:
        return min_word
    else:
        if valid_words:
            return random.choice(valid_words)
        else:
            return None

def make_index(path, delimiter, value=1):
    """
    Given a CSV reader, return a map between the first column and the
    column specified by value.
    """
    d = dict()
    with open(path, newline='') as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            d[row[0]] = row[value]
    return d


def generate(french_sentence_file,
             english_sentence_file,
             links_file,
             frequency_list_file,
             out_file):
    # Make index between sentence number and rest of csv
    print("Making indexes ...")

    french = make_index(french_sentence_file, '\t', value=2)
    english = make_index(english_sentence_file, '\t', value=2)
    links = make_index(links_file, '\t')

    # Make index between word and usage frequency
    frequency = make_index(frequency_list_file, ' ')

    print("Generating clozes ...")
    with open(out_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

        eng_already_used = {}

        # For each French sentence
        for fra_number, fra_sentence in french.items():
            # Lookup English translation
            eng_number = links.get(fra_number)
            if not eng_number:
                continue  # If no English translation, skip

            if eng_number in eng_already_used:
                continue # Skip if English sentence already used
            eng_already_used[eng_number] = True

            eng_sentence = english.get(eng_number)
            if not eng_sentence:
                continue  # If no English translation, skip

            # Find the cloze word
            fra_cloze_word = find_cloze(fra_sentence, frequency)
            if not fra_cloze_word:
                continue  # If no cloze word, skip

            clozed = fra_sentence.replace(fra_cloze_word,
                                          '{{{{c1::{}}}}}'.format(fra_cloze_word))

            # # Generate audio
            # audio_filename = 'fra-{}-audio.mp3'.format(fra_number)
            # if not os.path.isfile(audio_filename):
            #     synthesize_speech(fra_sentence, audio_filename)
            # audio_filename = ''

            writer.writerow([fra_number,
                             clozed,
                             eng_number,
                             eng_sentence,
                             # '[sound:{}]'.format(audio_filename),
                             ])

    print("Done.")

generate('deu_sentences.tsv',
             'eng_sentences.tsv',
             'links.csv',
             'de_full.txt',
             'german.csv'
             )
