
__version__ = 1.0
__auther__ = "Shishere"

import PySimpleGUI as sg
import pandas as pd
from pathlib import Path
from threading import Thread
from typing import List

KEY_INPUT_CSV_FILENAME = "-INPUT CSV-"
KEY_OUTPUT_FOLDER = "-OUTPUT FOLDER-"

KEY_CSV_ROW_COUNT = "-CSV OR ROW COUNT-"
KEY_SPLIT = "-SPLIT-"
KEY_SPLIT_TYPE_N_CSV = "-N CSVs-"
KEY_SPLIT_TYPE_N_ROW_CSV = "-CSV WITH N ROWS-"
KEY_COUNT_TEXT = "-KEY COUNT TEXT-"
KEY_LOG = "-LOG-"
TEXT_WIDTH = 13
GROUP_ID_SPLIT_TYPE = "-SPLIT TYPE-"

KEY_VIEW_DETAILS = "-VIEW DETAILS-"

GROUP_ID_SPLIT_ADVANCED = "-ADVANCED SPLIT-"
KEY_APPLY_CHANGES = "-APPLY CHANGES-"
KEY_COLUMNS_LIST = '-COLUMNS LIST-'
KEY_ALL_COLUMNS = "-ALL COLUMNS-"
KEY_SELECTED_COLUMNS = "-SELECTED COLUMNS-"

KEY_CSV_DETAILS = "-CSV DETAILS-"

CSV_DETAILS_TEMPLATE = '''
Filename\t\t:   {}
Column Count\t:   {}
Row Count\t:   {}
'''

DELETE_KEY = "Delete:46"

sg.ChangeLookAndFeel("Dark2")

class CSV_Utility:
    def __init__(self) -> None:
        # SPLIT CSV

        self.view_details_clicked = False
        self.log_data = []
        self.split_types = [
            "Split into N CSVs",
            "Split into CSVs with N Rows each"
        ]

        self.columns_original = []
        self.columns_using = []
        self.columns_selected = []

        inner_frame_1 = [
            [sg.Text("Input CSV File", size=(TEXT_WIDTH,)), sg.Input(readonly=True, size=(55,)), sg.FileBrowse(key=KEY_INPUT_CSV_FILENAME)],
            [sg.Text("Output Folder", size=(TEXT_WIDTH,)), sg.Input(readonly=True, size=(55,)), sg.FolderBrowse(key=KEY_OUTPUT_FOLDER)],
        ]

        inner_frame_2 = [
            [sg.Button(button_text="View Details", key=KEY_VIEW_DETAILS), sg.Text(text=CSV_DETAILS_TEMPLATE, visible=False, key=KEY_CSV_DETAILS)],
        ]

        inner_frame_3 = [
            [sg.Radio(text="Split into N CSVs", group_id=GROUP_ID_SPLIT_TYPE, default=True, key=KEY_SPLIT_TYPE_N_CSV), sg.Radio(text="Split into CSVs with N Rows each", group_id=GROUP_ID_SPLIT_TYPE, key=KEY_SPLIT_TYPE_N_ROW_CSV),],
            [sg.Text(text="Count", key=KEY_COUNT_TEXT, size=(TEXT_WIDTH-1,)), sg.Input(key=KEY_CSV_ROW_COUNT, size=(52,)), sg.Button(button_text="Split CSV", key=KEY_SPLIT, size=(10,))],
            [sg.Listbox(values=self.log_data, size=(80,30), key=KEY_LOG)]
        ]

        inner_frame_4 = [
            [sg.Radio(text="All columns", group_id=GROUP_ID_SPLIT_ADVANCED, default=True, key=KEY_ALL_COLUMNS), sg.Radio(text="Few Columns Only", group_id=GROUP_ID_SPLIT_ADVANCED, key=KEY_SELECTED_COLUMNS), sg.Button(button_text="Apply Changes", key=KEY_APPLY_CHANGES, size=(15,))],
            [sg.Text(text="COLUMNS (Select column names dont need, and use Delete key to remove them)")],
            [sg.Listbox(values=self.columns_using, size=(80,30), key=KEY_COLUMNS_LIST, select_mode=sg.SELECT_MODE_MULTIPLE,)]
        ]
        
        layout_csv_split_tab = [
            [sg.Text("Split large CSV into muiltiple CSVs",)],
            [sg.Column(layout=inner_frame_1), sg.VerticalSeparator(), sg.Column(layout=inner_frame_2)],
            [sg.Frame(title="SPLIT", layout=inner_frame_3, size=(300,300)), sg.Frame(title="Advanced", layout=inner_frame_4, size=(300,300))],
        ]


        # MAIN LAYOUT
        layout = [[
            sg.TabGroup([[
                sg.Tab(title="Split CSV", layout=layout_csv_split_tab,),
            ]])
        ]]

        # MAIN WINDOW
        self.window = sg.Window(
            title="CSV Utility",
            layout=layout,
            size=(1300, 800),
            return_keyboard_events=True
        )

    def log(self, text: str) -> None:
        self.log_data.append(text)
        self.window.Element(KEY_LOG).update(values=self.log_data)

    def write_csv(self, filename: str, data_list: List[dict], keys: list) -> None:
        try:
            df_temp = [[item.get(key, '') for key in keys] for item in data_list]

            df = pd.DataFrame(df_temp, columns=keys)
            df.to_csv(filename, index=False)
            self.log(f"{len(data_list)} rows written to {Path(filename).name}")
        except Exception as e:
            self.log(e)

    def split_csv_button_clicked(self,) -> None:
        
        def make_three_digit(number: int) -> str:
            num = str(number)
            if len(num) == 3:
                return num
            elif len(num) == 2:
                return f"0{num}"
            elif len(num) == 1:
                return f"00{num}"
        
        def split_csv_of_m_rows(filename: str, row_count: int, output_folder: str) -> None:
            self.log("Splitting started")
            chunk_size = row_count
            __file = Path(filename).name
            __filename_template = f"{output_folder}/" + ".".join(__file.split('.')[:-1]) + "_{}.csv"
            file_count = 0
            with pd.read_csv(filename, chunksize=chunk_size) as reader:
                for chunk in reader:
                    file_count += 1
                    data_list = chunk.to_dict(orient='records')
                    new_filename = __filename_template.format(make_three_digit(number=file_count))
                    self.write_csv(filename=new_filename, data_list=data_list, keys=self.columns_selected)
            self.log(f"{__file} splitted into {file_count} CSVs")
            self.log("Splitting Successful")
        
        def split_into_n_csv(filename: str, csv_count: int, output_folder: str) -> None:
            row_count = self.row_count
            
            chunk_size = row_count // csv_count
            chunk_size = chunk_size if chunk_size else 1
            self.log(f"1 CSV will contain maximum of {chunk_size} rows")
            split_csv_of_m_rows(filename=filename, row_count=chunk_size, output_folder=output_folder)
        
        def type_1() -> None:
            self.window.Element(KEY_SPLIT).update(disabled=True)
            split_into_n_csv(
                filename=filename,
                csv_count=count,
                output_folder=output_folder
            )
            self.window.Element(KEY_SPLIT).update(disabled=False)

        def type_2() -> None:
            self.window.Element(KEY_SPLIT).update(disabled=True)
            split_csv_of_m_rows(
                filename=filename,
                row_count=count,
                output_folder=output_folder
            )
            self.window.Element(KEY_SPLIT).update(disabled=False)
        
        status, filename, output_folder = self.is_csv_data_provided()

        if not status:
            return

        if not self.view_details_clicked:
            self.view_details_button_clicked()

        count = self.values[KEY_CSV_ROW_COUNT]

        if not count:
            sg.popup("Missing Count Value",)
            return
        elif not count.isnumeric():
            sg.popup("Invalid Count Value",)
            return
        
        count = int(count)

        if self.values[KEY_SPLIT_TYPE_N_CSV]:
            thread = Thread(target=type_1)
        elif self.values[KEY_SPLIT_TYPE_N_ROW_CSV]:
            thread = Thread(target=type_2)

        thread.start()

    def update_columns_list_box(self, ) -> None:
        self.window.Element(KEY_COLUMNS_LIST).update(self.columns_using)
        self.log(f"Column List Updated")
    
    def is_csv_data_provided(self, ) -> list:
        filename = self.values[KEY_INPUT_CSV_FILENAME]
        output_folder = self.values[KEY_OUTPUT_FOLDER]
        
        status = True
        if not filename:
            sg.popup("No input file selected",)
            status = False
        elif not filename.endswith('.csv'):
            sg.popup("Select a CSV File",)
            status = False
        elif not output_folder:
            sg.popup("Select a output Folder",)
            status = False

        return status, filename, output_folder

    def remove_columns_list_box(self, ) -> None:
        if self.values[KEY_SELECTED_COLUMNS]:
            [
                self.columns_using.remove(item)
                for item in self.values[KEY_COLUMNS_LIST]
            ]
            self.update_columns_list_box()
    
    def apply_button_clicked(self, ) -> None:
        if self.values[KEY_ALL_COLUMNS]:
            self.columns_using = self.columns_original.copy()
            self.columns_selected = self.columns_using.copy()
            self.update_columns_list_box()
        elif self.values[KEY_SELECTED_COLUMNS]:
            self.columns_selected = self.columns_using.copy()
        self.log(f"{len(self.columns_selected)} columns selected")
    
    def view_details_button_clicked(self, ) -> None:
        status, filename, _ = self.is_csv_data_provided()
        if not status:
            return

        row_count = 0
        with pd.read_csv(filename, chunksize=200) as reader:
            for chunk in reader:
                row_count += len(chunk.index)
        

        __data = chunk.to_dict(orient='records')
        if not __data:
            sg.popup("No Data found in CSV")
            return

        self.row_count = row_count
        self.columns_original = list(__data[0].keys())
        self.columns_using = self.columns_original.copy()
        self.columns_selected = self.columns_original.copy()

        self.window.Element(KEY_CSV_DETAILS).update(CSV_DETAILS_TEMPLATE.format(Path(filename).name, len(self.columns_original), self.row_count))
        self.window.Element(KEY_CSV_DETAILS).update(visible=True)
        self.window.Element(KEY_COLUMNS_LIST).update(self.columns_using)

        self.view_details_clicked = True

    def main_loop(self, ) -> None:
        while True:
            event, self.values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == KEY_VIEW_DETAILS:
                self.view_details_button_clicked()
            elif event == KEY_APPLY_CHANGES:
                self.apply_button_clicked()
            elif event == DELETE_KEY :
                self.remove_columns_list_box()
            elif event == KEY_SPLIT:
                self.split_csv_button_clicked()
            elif event == "deleteKey":
                self.remove_columns_list_box()

        self.window.close()


if __name__ == "__main__":
    CSV_Utility().main_loop()
