import csv

# Path to the CSV file
csv_file_path = 'local_files/username.csv'

# Function to count the number of rows
def count_rows(file_path):
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        row_count = sum(1 for row in reader) - 1  # Subtract 1 for the header row
    return row_count

if __name__ == '__main__':
    row_count = count_rows(csv_file_path)
    print(row_count)