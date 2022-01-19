import os
import pathlib
import shutil
#import oschmod

dir_path = os.path.dirname(os.path.realpath(__file__))

def unzip(zip_name, modpack_name):

    extract_dir = os.path.join(dir_path, modpack_name.replace(":", "_").replace(" ", "_").replace(",", ""))
    my_zip = os.path.join(dir_path, zip_name)
    shutil.unpack_archive(my_zip, extract_dir)
    print("Extraction Done, deleting zip")
    os.remove(my_zip)
    #oschmod.set_mode_recursive(extract_dir, "777")
    path = pathlib.PurePath(extract_dir)
    return path.name