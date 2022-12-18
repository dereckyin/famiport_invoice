import os
import xlrd
import xlwt
from xlwt import Workbook
from xlutils.copy import copy

class ExcelUtils:
    excel_file_path = ''
    workbook = None

    def __init__(self, file_path = None):
        if file_path is not None:
            self.excel_file_path = file_path
            self.workbook = xlrd.open_workbook(self.excel_file_path)

    def create_new_workbook(self, file_path):
        self.excel_file_path = file_path
        wb = Workbook()
        sheet = wb.add_sheet('0')
        wb.save(self.excel_file_path)

        self.workbook = xlrd.open_workbook(self.excel_file_path)

    def write_to_workbook(self, sheet_index, row, col, data):
        wb = copy(self.workbook)
        # os.remove(self.excel_file_path)
        sheet = wb.get_sheet(sheet_index)
        sheet.write(row, col, data)
        wb.save('C:\\Users\\user\\Desktop\\' + str(row) + '.xls')

    def set_workbook(self, file_path):
        self.excel_file_path = file_path
        self.workbook = xlrd.open_workbook(self.excel_file_path)

    # Get the name of all sheets in the excel file
    def get_sheet_names(self):
        return self.workbook.sheet_names() 

    # Get the total number of sheets in the file
    def get_sheet_count(self):
        return self.workbook.nsheets

    # Print all data of the specified index into a dictionary
    # based on each column's title
    def get_data_by_sheet_index(self, sheet_index):
        sheet = self.workbook.sheet_by_index(sheet_index)
        data = self.get_sheet_dictionary(sheet_index)

        total_rows = sheet.nrows
        total_cols = sheet.ncols

        for x in range(1, total_rows):
            for y in range(0, total_cols):
                data[sheet.cell(0, y).value].append(sheet.cell(x, y).value)

        return data

    # Create and return a dictionary with keys set as each column's title
    def get_sheet_dictionary(self, sheet_index):
        sheet = self.workbook.sheet_by_index(sheet_index)

        data = {}
        for x in range(0, sheet.ncols):
            data[sheet.cell(0, x).value] = []

        return data

    # Return the columns' header of the respective index
    def get_sheet_headers(self, sheet_index):
        sheet = self.workbook.sheet_by_index(sheet_index)

        headers = []
        for x in range(0, sheet.ncols):
            headers.extend([sheet.cell(0, x).value])

        return headers

    # Return the total count of rows in the respective sheet
    def get_row_count_by_sheet_index(self, sheet_index):
        return self.workbook.sheet_by_index(sheet_index).nrows

    # Return the total count of columns in the respective sheet
    def get_col_count_by_sheet_index(self, sheet_index):
        return self.workbook.sheet_by_index(sheet_index).ncols