import os
import pathlib
import shutil

def unzip(zip_name, modpack_name, file_ext, this_dir, output=False):

    if output:
        extract_dir = os.path.join(this_dir, output)
    else:
        extract_dir = os.path.join(this_dir, modpack_name.replace(":", "_").replace(" ", "_").replace(",", ""))
    my_zip = os.path.join(this_dir, zip_name)
    shutil.unpack_archive(my_zip, extract_dir)
    print("Extraction Done, deleting zip")
    os.remove(my_zip)
    #oschmod.set_mode_recursive(extract_dir, "777")
    path = pathlib.PurePath(extract_dir)
    return path.name