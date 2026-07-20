import json
import logging
import os
import xlsxwriter

logger = logging.getLogger(__name__)


def personal_info(input_json="personal details\\full_personal_data.json", output_path=None):
    if output_path is None:
        output_path = os.path.join(os.path.dirname(input_json) or ".", "testing1.xlsx")

    with open(input_json, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    data_list = [{**(info or {}), "id": id} for id, info in dataset.items()]

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet("Contacts")

    header_format = workbook.add_format({"bold": True, "bg_color": "#4472C4", "font_color": "white", "border": 1})
    cell_format = workbook.add_format({"border": 1})

    headers = ["Number", "Name", "Phone", "Email", "Location"]
    for col, h in enumerate(headers):
        worksheet.write(0, col, h, header_format)

    for i, record in enumerate(data_list, start=1):
        worksheet.write(i, 0, i, cell_format)
        worksheet.write(i, 1, str(record.get("name", "")).strip(), cell_format)
        worksheet.write(i, 2, str(record.get("phone", "")).strip(), cell_format)
        worksheet.write(i, 3, str(record.get("email", "")).strip(), cell_format)
        worksheet.write(i, 4, str(record.get("location", "")).strip(), cell_format)

    worksheet.set_column("A:A", 8)
    worksheet.set_column("B:B", 22)
    worksheet.set_column("C:C", 16)
    worksheet.set_column("D:D", 30)
    worksheet.set_column("E:E", 30)

    workbook.close()
    return output_path


if __name__ == "__main__":
    print(personal_info())