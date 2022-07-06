# Starbound Mod Name Cleaner

This application is meant to automate the cleaning required to make
managing the Starbound mods for a dedicated server easier.

When downloading mods from the the Steamworkshop, it will save in your /steamapps/workshop/content/
folder as the workshop IDs.

This application will search for those workshop IDs and rename the folders to their slugified
names.

```
MOD_FOLDER = "<path to starbound mod folder>"
OUTPUT_FOLDER = "<path to output of renamed folders>"
```

## Usage

`python main2.py`
