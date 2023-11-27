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

import os
from PIL import ImageTk
from user_cli import *
from tkinter import filedialog
from tkinter import *
import sys
import gpt_prompting as gp
import concurrent.futures

sys.path.append('/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages')


def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def fullscreen_window(window):
    window.attributes('-fullscreen', True)
    center_window(window)


def process_(file):
    lect_name = file.split("/")[-1].split(".")[0]

    if file.split("/")[-1].split(".")[1] == "pdf":
        pass
    elif file.split("/")[-1].split(".")[1] == "docx":
        template = f"soffice --headless --convert-to pdf {file}"
        os.system(template)
        file = file[:-5] + ".pdf"

    raw_data = extract_words(file)
    raw_data = text_to_groupings(raw_data)
    keyword_data = wp.extract_noun_chunks(raw_data)
    keyword_data = wp.merge_slide_with_same_headers(keyword_data)

    keyword_data = wp.duplicate_word_removal(keyword_data)
    search_query = wp.construct_search_query(keyword_data)

    if source_choice.get() == "Google":
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(get_people_also_ask_links, search_query[:3])
    elif source_choice.get() == "GPT":
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = gp.get_gpt_answers(search_query[:3])

    auto_anki_model = get_model()
    deck = get_deck(deck_name=lect_name)
    for result in results:
        try:
            question = result["Question"]
            answer = result["Answer"]
            qa = add_question(
                question=f'{question}', answer=f'{answer}', curr_model=auto_anki_model)
            deck.add_note(qa)
        except KeyError as e:
            # Handle the case where "Question" or "Answer" keys are missing in a dictionary
            print(f"KeyError: {e}")
            continue
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
            continue


    add_package(deck, lect_name)

# Function for opening the file explorer window


def browseFiles():
    file = filedialog.askopenfilename(parent=window, title="Choose a file", filetypes=[
                                      ("Doc file", "*.docx"), ("Pdf file", "*.pdf")])

    text_box = Text(window, height=10, width=50, padx=15, pady=15, font=("Futura", 25))
    text_box.insert(1.0, file)
    text_box.tag_configure("center", justify="center")
    text_box.tag_add("center", 1.0, "end")
    text_box.pack(expand=True, fill='both')
    process_(file)


window = Tk()
window.title('Auto-Anki')
fullscreen_window(window)


background_image = PhotoImage(file='code/anki_back.png') 
background_label = Label(window, image=background_image,borderwidth=0)
background_label.place(relwidth=1, relheight=1)

logo = ImageTk.PhotoImage(file='code/logo.png')
logo_label = Label(window, image=logo, borderwidth=0)
logo_label.image = logo
logo_label.pack(expand=True)

instructions = Label(
    window, text="Select a PDF file on your computer", font=("Futura", 20), fg="black" , bg="#9FB4FF")
instructions.pack(expand=True)

button_explore = Button(window,
                        text="Browse Files",
                        command=browseFiles,
                        font=("Futura", 15),
                        bg="#4CAF50",
                        fg="black",
                        borderwidth=0,
                        padx=20,
                        pady=10)
button_explore.pack(expand=True)

source_choice = StringVar(window)
sources = ["Google", "GPT"]
source_choice.set(sources[0])

source_dropdown = OptionMenu(window, source_choice, *sources)
source_dropdown_label = Label(
    window, text="Choose an API source:", font=("Futura", 20),fg="black", bg="#9FB4FF")
source_dropdown_label.pack(expand=True)
source_dropdown.pack(expand=True)

button_exit = Button(window,
                     text="Exit",
                     command=exit,
                     font=("Futura", 15),
                     bg="#FF5733",
                     fg="black",
                     borderwidth=0,
                     padx=20,
                     pady=10)
button_exit.pack(expand=True)

window.mainloop()
