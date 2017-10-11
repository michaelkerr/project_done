# -*- coding: utf-8 -*-
import smartsheet
import logging
import yaml


### CONFIGURATION ###
config_file = path.join(path.dirname(path.realpath(__file__)), 'config/config.yml')
if path.exists(config_file):
    config = yaml.load(open(config_file, 'r'))
else:
    print config_file + ' not found'
    exit()

sheetid = '7046951653926788'

# Helper function to find cell in a row
def get_cell_by_column_name(row, column_ame):
    column_id = column_map[column_ame]
    return row.get_column(column_id)


def evaluate_row_and_build_updates(source_row):
    # TODO Update Estimate
    # TODO Update Target date
    # TODO IF JIRA STATUS "In Progress" set "Start Date" to =today()



    # Find the cell and value we want to evaluate
    status_cell = get_cell_by_column_name(source_row, "Status")
    status_value = status_cell.display_value
    if (status_value == "Complete"):
        remaining_cell = get_cell_by_column_name(source_row, "Remaining")
        if (remaining_cell.display_value != "0"):                           # Skip if already 0
            print("Need to update row #" + str(source_row.row_number))

            # Build new cell value
            newCell = ss.models.Cell()
            newCell.column_id = column_map["Remaining"]
            newCell.value = 0

            # Build the row to update
            newRow = ss.models.Row()
            newRow.id = source_row.id
            newRow.cells.append(newCell)

            return newRow

    return None


if __name__ == '__main__':
    column_map = {}

    # Initialize client
    ss = smartsheet.Smartsheet(access_token)

    # Make sure we don't miss any error
    ss.errors_as_exceptions(True)
    logging.basicConfig(filename='mylog.log', level=logging.INFO)

    # Load entire sheet
    sheet = ss.Sheets.get_sheet(sheet_id)

    print ("Loaded " + str(len(sheet.rows)) + " rows from sheet: " + sheet.name)

    # Build column map for later reference - translates column names to column id
    for column in sheet.columns:
        column_map[column.title] = column.id

    # Accumulate rows needing update here
    rowsToUpdate = []

    for row in sheet.rows:
    rowToUpdate = evaluate_row_and_build_updates(row)
    if (rowToUpdate != None):
        rowsToUpdate.append(rowToUpdate)

    # Finally, write updated cells back to Smartsheet
    print("Writing " + str(len(rowsToUpdate)) + " rows back to sheet id " + str(sheet.id))
    result = ss.Sheets.update_rows(sheet_id, rowsToUpdate)
    print ("Done")
