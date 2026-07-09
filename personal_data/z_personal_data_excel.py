import json
import logging
import xlsxwriter

logger = logging.getLogger(__name__)

def personal_info():
    try:
        with open("personal details\\full_personal_data.json","r",encoding="utf-8") as f:
            dataset = json.load(f)
    except Exception as e:
        logger.exception(f"PERSONAL DETAILS JSON FILE IS NOT FOUND! {e}")

    try:
        data_list = [{**info, 'id': id} for id, info in dataset.items()]

        OUTPUT_PATH = 'C:\\Users\\User\\Documents\\AI Screening Project\\Code files\\extraction\\personal details\\testing1.xlsx'

        workbook = xlsxwriter.Workbook(OUTPUT_PATH)
        worksheet = workbook.add_worksheet('Contacts')

        header_format = workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white', 'border': 1})
        cell_format = workbook.add_format({'border': 1})

        headers = ['Number', 'Name', 'Phone', 'Email', 'Location']
        for col, h in enumerate(headers):
            worksheet.write(0, col, h, header_format)

        for i, record in enumerate(data_list, start=1):
            row = i
            worksheet.write(row, 0, int(record['id']), cell_format)
            worksheet.write(row, 1, str(record.get('name', '')).strip(), cell_format)
            worksheet.write(row, 2, str(record.get('phone', '')).strip(), cell_format)
            worksheet.write(row, 3, str(record.get('email', '')).strip(), cell_format)
            worksheet.write(row, 4, str(record.get('location', '')).strip(), cell_format)

        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 22)
        worksheet.set_column('C:C', 16)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 30)

        workbook.close()
        print("DONE!!!!")

    except Exception as e:
        logger.exception(f"EXCEL SHEET CREATION IS FAILED! : {e}") 

personal_info()