import datetime
import os.path

from data_handling.data_retrieval import iget_log_dirs, iget_files_in_directory
from system.system_constants import csv_formatter, log_directories


# Index files created for fast searching of sensor readings.
# With this measurements can be binary searched for time filters in the range.
# I will come back to this if it is needed.


def index_character_in_file(file_path, char="\n") -> None:
    """
    Get all byte indexes of a character in a file and write these to a file
    """

    character_locations = []
    with open(file_path, newline=char) as file:
        # for l in file:
        line = file.readline()
        while line:
            character_locations.append(str(file.tell()))
            line = file.readline()

    create_index_file(file_path, character_locations)


# Create a CSV .index file
def create_index_file(file_path, indexes) -> None:
    with open(f"{file_path}.index", "w") as f:
        f.write("\n".join(indexes))


def index_all_logs() -> None:
    """
    Index all csv files in the log folders
    """
    for dir in iget_log_dirs():
        for file in iget_files_in_directory(dir, "csv"):
            index_character_in_file(file, char="\n")


def search_file_for_timestamp_boundry(file_path, time_boundry: datetime.datetime):
    """

    :param file_path: The file path to search through
    :return:
    """
    index_file = f"{file_path}.index"
    char_indexes = None

    with open(index_file) as f:
        char_indexes = [int(l) for l in f.readlines()]

    # if char_indexes is None:
    #    index_character_in_file(file_path)

    with open(file_path) as f:

        boundary_found = False

        index_upper_limit = len(char_indexes) - 1
        upper_check = index_upper_limit
        lower_check = 0

        while not boundary_found:
            if upper_check == lower_check + 1:
                boundary_found = True
                break

            # Declare the index to be found
            index_to_find = int((upper_check + lower_check) / 2) - 1

            char_limits = char_indexes[index_to_find:index_to_find + 2]
            lower_char_limit, upper_char_lim = char_limits
            chars_to_read = upper_char_lim - lower_char_limit - 2

            f.seek(lower_char_limit)
            line = f.read(chars_to_read)

            time_str = line.split(",")[0]
            time_line = datetime.datetime.strptime(time_str, csv_formatter.datefmt)

            if time_line > time_boundry:
                pass


            elif time_line < time_boundry:
                pass


            else:
                pass




if __name__ == '__main__':
    print("Indexing started")
    index_all_logs()
    print("Indexing completed")
    search_file_for_timestamp_boundry(os.path.join(log_directories["measurements"], "dummy_id.csv"),
                                      datetime.datetime.now())
