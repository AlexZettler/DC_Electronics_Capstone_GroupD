import data_handling.data_retrieval as dr
import os.path

def test_log_dirs():
    # Confirm that the base path for the logs is a directory
    assert os.path.isdir(dr.base_log_directory)

    # Confirm that all sublog directories are full directories
    for dir in dr.iget_log_dirs():
        assert os.path.isdir(dir)

        # Confirm csv files in directory are files
        for f in dr.iget_files_in_directory(dir,"csv"):
            assert os.path.isfile(f)
