import z_text_preprocess
import z_ocr_fun
import xlsxwriter


def personal_info(y):
    try:
        row = z_ocr_fun.extraction(y)
        text_data = z_text_preprocess.llm_text(text=row, y =y)
        personal_data = z_text_preprocess.preprocess(y)


        data_list = [personal_data]

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
            worksheet.write(row, 0, i, cell_format)
            worksheet.write(row, 1, record.get('name', '').strip(), cell_format)
            worksheet.write(row, 2, str(record.get('phone', '')).strip(), cell_format)
            worksheet.write(row, 3, record.get('email', '').strip(), cell_format)
            worksheet.write(row, 4, record.get('location', '').strip(), cell_format)

        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 22)
        worksheet.set_column('C:C', 16)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 18)

        workbook.close()
        print("Done!!!!")

    except Exception as e:
        print(e) 

if __name__ == "__main__":
    personal_info("y_Associate Data Scientist Induwara Dilshan.pdf")