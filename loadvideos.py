#  module to deal with loading videos
#  from csv, excel, pdf files

import pdb
import csv
from openpyxl import load_workbook


class BaseExtractor(object):
    #  headers for operation on video
    #  these headers are present in some
    #  excel, csv or pdf file
    headers = ['video_id', 'cut', 'convert']

    def __init__(self, base_file):
        self.base_file = base_file
        op_data = self.load_data_from_base_file()
        # pdb.set_trace()
        self.data = self.generate_operations_list(op_data)

    def generate_operation_dict(self, row):
        operation_dict = {}
        for idx, el in enumerate(row):
            operation_dict[self.headers[idx]] = el

        return operation_dict

    def generate_operations_list(self, rows):
        # generates operations for each
        # video in the file
        operations_list = []
        for row in rows:
            o_row = self.generate_operation_dict(row)
            operations_list.append(o_row)

        return operations_list

    def load_data_from_base_file(self):
        """
        opens and reads data from a file,
        to be overriden in a subclass
        :return:
        """
        pass


class OperationXLSXExtractor(BaseExtractor):
    #  extracts operations on video from
    #  .xlsx files and stores them in a
    #  a list

    def load_data_from_base_file(self):
        all_rows = []
        #  load workbook and get first sheet
        wb = load_workbook(filename=self.base_file,
                           read_only=True)
        ws = wb['Sheet1']
        for row in ws.rows:
            all_rows.append([cell.value for cell in row])

        return all_rows


class OperationCSVExtractor(BaseExtractor):
    #  gets operations from csv files
    #  and stores them in a list
    def load_data_from_base_file(self):
        all_rows = []
        with open(self.base_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                all_rows.append(row)
        # pdb.set_trace()
        return all_rows


class VideoCSVPrepare(object):
    def __init__(self, csv_file):
        self.csv_file = csv_file


class VideoXLSXPrepare(object):
    def __init__(self, xlsx_file):
        self.xlsx_file = xlsx_file


class VideoPDFPrepare(object):
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
