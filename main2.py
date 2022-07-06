import os
import json
import shutil

from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from slugify import slugify
from bs4 import BeautifulSoup

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

MOD_FOLDER = "/mnt/g/Steam/steamapps/workshop/content/211820/"
OUTPUT_FOLDER = os.path.join(THIS_DIR, 'output')

STEAM_WORKSHOP_URL = "https://steamcommunity.com/sharedfiles/filedetails/"


IGNORED_MOD_IDS = [
    '1264107917',
    '1362924773',
    '1430852353',
    '1430853241',
    '1681880007',
    '2494854936',
    '2681858844',
    '729426797',
    '729524482',
    '729726478',
]


def _create_mapping(mod_title, mod_id, mod_path, mod_contents=[]):
    """
    Helper function for creating dict objects for the mod_map
    """
    return {
        'mod_title': mod_title,
        'mod_id': mod_id,
        'mod_path': mod_path,
        'mod_contents': mod_contents
    }


def _get_mod_title(mod_id):
    # determine if there are pak files in the dir
    mod_workshop_url = f"{STEAM_WORKSHOP_URL}?id={mod_id}"

    r = requests.get(mod_workshop_url)

    # Get the title from Steam Workshop
    soup = BeautifulSoup(r.content, 'html.parser')
    mod_title = (soup.find("div", class_="workshopItemTitle").get_text())
    mod_title = slugify(mod_title)
    return mod_title


def _thread_function(mod_id, mod_path, mod_contents=[]):
    """
    To throw into the executor
    """
    mod_title = _get_mod_title(mod_id)
    return _create_mapping(mod_title, mod_id, mod_path, mod_contents=mod_contents)


def _copy_mods(mod_map, output_folder):
    """
    Copy the mods using the mod_map to the output_folderr
    """
    for map_ in mod_map:
        source_file = os.path.join(map_['mod_path'], 'contents.pak')
        target = os.path.join(output_folder, f"{map_['mod_title']}.pak")

        # Copy the file and rename
        shutil.copy(source_file, target)


def main(mod_folder=None, output_folder=None):
    # Define the mod folder and output folder
    mod_folder = mod_folder or MOD_FOLDER
    output_folder = output_folder or OUTPUT_FOLDER

    # Assume the list of dir names are the list of mod_ids to fetch
    mod_ids = os.listdir(mod_folder)

    # clean the mod_ids
    def _filter(mod_id):
        if mod_id in IGNORED_MOD_IDS:
            return False
        return True
    mod_ids = filter(_filter, mod_ids)

    # Start the threads
    processes = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        for mod_id in mod_ids:
            mod_path = os.path.join(mod_folder, mod_id)
            mod_contents = os.listdir(mod_path)
            if 'contents.pak' in mod_contents is False:
                continue
            processes.append(executor.submit(_thread_function, mod_id, mod_path, mod_contents))

    mod_map = []
    for task in as_completed(processes):
        mod_map.append(task.result())

    # Remove the folder if it already exists
    shutil.rmtree(output_folder)

    # Create the folder
    if os.path.exists(output_folder) is False:
        os.mkdir(output_folder)

    # Copy the mods
    _copy_mods(mod_map, output_folder=output_folder)

if __name__ == '__main__':
    main()
