
__version__ = 1.0
__auther__ = "Shishere"

import PySimpleGUI as sg
import pandas as pd
from pathlib import Path
from time import sleep
from threading import Thread


KEY_INPUT_CSV_FILENAME = "-INPUT CSV-"

KEY_OUTPUT_FOLDER = "-OUTPUT FOLDER-"

KEY_CSV_ROW_COUNT = "-CSV OR ROW COUNT-"

KEY_SPLIT = "-SPLIT-"

KEY_SPLIT_TYPE = "-SPLIT_TYPE-"

KEY_COUNT_TEXT = "-KEY COUNT TEXT-"

KEY_LOG = "-LOG-"

sg.ChangeLookAndFeel("Dark2")

class CSV_Utility:
    def __init__(self) -> None:
        # SPLIT CSV
        self.__log = []
        self.__split_types = [
            "Split into N CSVs",
            "Split into CSVs with N Rows each"
        ]
        inner_frame = [
            [sg.Text(text="Split Type"), sg.Combo(values=self.__split_types, key=KEY_SPLIT_TYPE, default_value=self.__split_types[0], readonly=True)],
            [sg.Text(text="Count", key=KEY_COUNT_TEXT), sg.Input(key=KEY_CSV_ROW_COUNT), sg.Button(button_text="Split", key=KEY_SPLIT)],
            [sg.Listbox(values=self.__log, size=(60,30), key=KEY_LOG)]
        ]

        layout_csv_split = [
            [sg.Text("Split large CSV into muiltiple CSVs",)],
            [sg.Text("Input CSV File"), sg.Input(), sg.FileBrowse(key=KEY_INPUT_CSV_FILENAME)],
            [sg.Text("Output Folder"), sg.Input(), sg.FolderBrowse(key=KEY_OUTPUT_FOLDER)],
            [sg.Frame(title="SPLIT", layout=inner_frame)]
        ]


        # MAIN LAYOUT
        layout = [[
            sg.TabGroup([[
                sg.Tab(title="Split CSV", layout=layout_csv_split, ),
            ]])
        ]]

        # MAIN WINDOW
        self.__window = sg.Window(
            title="CSV Utility",
            layout=layout,
            size=(1000, 600)
        )

    def __convert(self, split_type: str, count: int):
        
        def log(text: str) -> None:
            self.__log.append(text)
            self.__window.Element(KEY_LOG).update(values=self.__log)
            
        def type_1()  -> None:
            self.__window.Element(KEY_SPLIT).update(disabled=True)
            self.__window.Element(KEY_SPLIT).update(disabled=False)

        def type_2()  -> None:
            self.__window.Element(KEY_SPLIT).update(disabled=True)
            self.__window.Element(KEY_SPLIT).update(disabled=False)
        
        if split_type == self.__split_types[0]:
            thread = Thread(target=type_1)
        else:
            thread = Thread(target=type_2)

        thread.start()

    def main_loop(self, ) -> None:
        while True:
            event, values = self.__window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == KEY_SPLIT:
                split_type = values[KEY_SPLIT_TYPE]
                count = values[KEY_CSV_ROW_COUNT]
                if not count:
                    sg.popup("Missing Count Value",)
                    continue
                if not count.isnumeric():
                    sg.popup("Invalid Count Value",)
                    continue

                self.__convert(split_type=split_type, count=count)


if __name__ == "__main__":
    CSV_Utility().main_loop()

