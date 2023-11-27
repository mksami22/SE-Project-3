# MIT License
# 
# Copyright 2023 auto_anki
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the “Software”), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.


import genanki
import os
import requests
import json
import urllib.request


def get_model():
    """
    Define an Anki flashcard model with fields for questions and answers suitable for use in the Anki flashcard application 
    """
    my_model = genanki.Model(
        1607392319,
        'Anki Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ])
    return my_model


def get_deck(deck_name):
    """
    Define and initialize an anki deck, where we can add cards.

    Returns
    ------
    anki deck 
    """

    my_deck = genanki.Deck(
        2059400110,
        deck_name)
    return my_deck


def add_question(question, answer, curr_model):
    """
    Create a card for a question, answer pair.

    Returns
    ------
    anki card 
    """

    my_note = genanki.Note(
        model=curr_model,
        fields=[question, answer])
    return my_note


def add_package(deck, output_fname):
    """
    Create a package for a deck

    Returns
    ------
    None
    """
    relative_output_dir = '../output'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.path.join(dir_path, relative_output_dir)
    genanki.Package(deck).write_to_file(f'{dir_path}/{output_fname}.apkg')
    add_flashcards(deck, output_fname)
    # print("printing result : ", result)
    # deck_names_result = get_deck_names()
    # print("Deck Names Result:", deck_names_result)
    # new_deck_result = create_deck("TestDeck")
    # print("Create Deck Result:", new_deck_result)
    # note_result = add_note("TestDeck", "Test Question", "Test Answer")
    # print("Add Note Result:", note_result)

    # deck_name = "TestDeck"
    # result = invoke('createDeck', deck=deck_name)
    # print('result invoke ', result)

    # my_note = {
    #     "deckName": deck_name,
    #     "modelName": "Basic",
    #     "fields": {
    #         "Front": "front content",
    #         "Back": "back content",
    #     },
    #     "options": {
    #         "allowDuplicate": False
    #     },
    #     "tags": ['tester']
    # }

    # result = invoke('addNote', note=my_note)
    # print('result invoke addnote', result)
    

def add_flashcards(deck, output_fname):
    
    deck_name = deck.name
    result = invoke('createDeck', deck=deck_name)
    print('result invoke deck name ', result)
    deck_notes = deck.notes
    notes_data_ll = [note.fields for note in deck_notes]
    print(notes_data_ll)
    notes_data = [{"Front": note[0], "Back": note[1]} for note in notes_data_ll]
    print(notes_data)
    for note in notes_data_ll:
        print('note 0 ', str(note[0]))
        print('note 1 ', str(note[1]))
        my_note = {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {
                "Front": str(note[0]),
                "Back": str(note[1]),
            },
            "options": {
                "allowDuplicate": False
            },
            "tags": ['tester']
        }
        result = invoke('addNote', note=my_note)
        print('result invoke addnote', result)

    

# Example usage:
# result = add_flashcards(deck.notes, "output_deck")
# print("printing result:", result)


def get_deck_names():
    anki_url = "http://localhost:8765"
    endpoint = "/invoke"
    action = "deckNames"

    data = {
        "action": action,
        "version": 6,
    }

    response = requests.post(anki_url + endpoint, json=data)
    result = response.json()

    return result


def create_deck(deck_name):
    anki_url = "http://localhost:8765"
    endpoint = "/invoke"
    action = "createDeck"

    data = {
        "action": action,
        "version": 6,
        "params": {
            "deck": deck_name,
        },
    }

    response = requests.post(anki_url + endpoint, json=data)
    result = response.json()

    return result


def add_note(deck_name, question, answer):
    anki_url = "http://localhost:8765"
    endpoint = "/invoke"
    action = "addNote"

    # Convert Deck notes to a list of dictionaries
    notes_data = [{"deckName": deck_name, "modelName": "Basic", "fields": {"Front": question, "Back": answer}}]

    data = {
        "action": action,
        "version": 6,
        "params": {
            "notes": notes_data,
        },
    }

    response = requests.post(anki_url + endpoint, json=data)
    result = response.json()

    return result


def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error']) # *Line 18*
    return response
