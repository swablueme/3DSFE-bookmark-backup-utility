# 3DSFE-bookmark-backup-utilty
Fire Emblem Awakening and Fire Emblem Fates disable the ability to make Battle Saves when the difficulty is Hard or greater but does generate Bookmarks which are deleted after reloading the game

These scripts aim to enable a user to (Thread 1) asynchronously backup (automatically) and (Thread 2)asynchronously restore bookmarks (upon pressing 'c') deleted by the game from a seperate directory.

The script watches the directories for each of these two games defined in 'config.ini' in the same folder as the script.

The script is intended to be used with Citra.

## Getting Started

1. Create a config.ini file in the script folder 
2. Type ```python 3dsFEbookmarkbackup.py``` to run
3. Script requires python 3.7 or more and needs to be run in cli rather than an IDE. It has been tested on windows

### config.ini template
```
[Settings]
;game is Awakening or Fates
game = 

[Fates]
;in citra-qt.exe, right click the game and select Open Save Data Location to obtain the correct path
path= 

[Awakening]
path =
```
