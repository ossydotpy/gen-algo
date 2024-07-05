def create_directory_if_not_exists(directory):
    import os

    if not os.path.exists(directory):
        os.makedirs(directory)
