from data_handling.data_retrieval import iget_log_dirs, iget_files_in_directory


# Index files created for fast searching of sensor readings.
# With this measurements can be binary searched for time filters in the range.


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
        f.write(",\n".join(indexes))


def index_all_logs() -> None:
    """
    Index all csv files in the log folders
    """
    for dir in iget_log_dirs():
        for file in iget_files_in_directory(dir, "csv"):
            index_character_in_file(file, char="\n")


if __name__ == '__main__':
    index_all_logs()
