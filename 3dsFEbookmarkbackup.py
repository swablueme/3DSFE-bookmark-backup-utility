import asyncio
import hashlib
import os
import datetime as dt
import configparser
from shutil import copyfile
import time
import msvcrt
import threading

"""
Fire Emblem Awakening and Fire Emblem Fates
disable the ability to make Battle Saves when
the difficulty is Hard or greater but does
generate Bookmarks which are deleted after
reloading the game

These scripts aim to enable a user
to (Thread 1)asynchronously backup (automatically) and
(Thread 2)asynchronously restore bookmarks (upon pressing 'c')
deleted by the game from a seperate directory.

The script watches the directories for
each of these two games defined in 'config.ini'
in the same folder as the script.

The script is intended to be used with Citra.
"""

class decorators:
    """creates async wrappers"""
    @staticmethod
    def runwrapper(func):
        def asyncrun(*args, **kwargs):
            return asyncio.run(func(*args, **kwargs))
        return asyncrun

    @staticmethod
    def runasync(func):
        @decorators.runwrapper
        async def awaitwrapper(*args, **kwargs):
            return await asyncio.gather(func(*args, **kwargs))
        return awaitwrapper


class utility:
    @decorators.runasync
    async def check_sha5(self, bookmark):
        """retrieves the sha5 of a bookmark filename using hashlib"""
        with open(bookmark,"rb") as file:
            data=file.read()
            sha = hashlib.sha256(data).hexdigest()
        return sha

    @decorators.runasync   
    async def get_bookmark_time(self, bookmark):
        """obtains the time at which a bookmark was last modified"""
        timestamp=os.path.getmtime(bookmark)
        actual_date=dt.datetime.fromtimestamp(timestamp)
        actual_date=actual_date.strftime("%d-%m %H-%M-%S")
        return actual_date
    
    @decorators.runasync 
    async def get_time_from_filename(self, filename):
        """returns the filename (which has the date and time in it)
        as a date object for comparison"""
        filename=filename.split(".")[0]
        actual_date=dt.datetime.strptime(filename,"%d-%m %H-%M-%S")
        return actual_date
        
    def is_sha5_same(self, filename1, filename2):
        """returns True if the sha5s of two files are the same and False otherwise"""
        return self.check_sha5(filename1)[0] == self.check_sha5(filename2)[0]

    def is_time_same(self, filename1, filename2):
        """returns True if the modified times of two files are the same and False otherwise"""
        return self.get_bookmark_time(filename1)[0] == self.get_bookmark_time(filename2)[0]

    def is_too_old(self, filename1):
        """returns True if the file is older than a day"""
        return (dt.datetime.now()-self.get_time_from_filename(filename1)[0]).days>1

class backupfile:
    def __init__(self):
        """Reads config.ini settings with configparser and prints out the relevant detail
        also creates a backup folder if it does not exist"""
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.game = config["Settings"]["game"]
        self.path = config[self.game]["path"]
        print("Game:", self.game)
        if self.game == "Awakening":
            self.bookmarks_folder = os.path.join(os.path.dirname(self.path), "bookmarks_backup")
            self.bookmarks = [os.path.join(self.path, "Temporary")]
        else:
            self.bookmarks_folder=os.path.join(self.path,"bookmarks_backup")
            self.bookmarks = [os.path.join(self.path, "Temporary.bak"), os.path.join(self.path, "Temporary.bak^")]
            
        print("Your bookmark path is:", self.bookmarks_folder)
        print("Your monitored directory is:", self.path)
        
        if not os.path.exists(self.bookmarks_folder):
            os.mkdir(self.bookmarks_folder)
        
    def getlastfiles(self):
        """Gets the most recently backed up bookmark/s for the game"""
        return [os.path.join(self.bookmarks_folder, file) for file in os.listdir(self.bookmarks_folder)[-len(self.bookmarks):]]
        
    def backup_automatically(self):
        """Copies files to the backups folder if the sha5 is not identical"""
        u = utility()
        while True:
            time.sleep(1)
            lastfiles = self.getlastfiles()
            if not lastfiles:
                [copyfile(file,os.path.join(self.bookmarks_folder,os.path.basename(file))) for file in self.bookmarks]
                [copyfile(file,os.path.join(self.bookmarks_folder,u.get_bookmark_time(file)[0])) for file in self.bookmarks]
            for idx, file in enumerate(lastfiles):
                try:
                    if not u.is_sha5_same(file, self.bookmarks[idx]):
                        copyfile(self.bookmarks[idx], os.path.join(self.bookmarks_folder,os.path.basename(file)))
                        copyfile(self.bookmarks[idx], os.path.join(self.bookmarks_folder,u.get_bookmark_time(file)[0]))
                except:
                    pass
        
    def getinput(self):
        """If a keypress of 'c' is detected in the terminal window, restore the most recently backed up file"""
        while True:
            if msvcrt.kbhit() and msvcrt.getch() == b'c':
                lastfiles = self.getlastfiles()
                if lastfiles and not os.path.exists(self.bookmarks[0]):
                    for idx, file in enumerate(lastfiles):
                        copyfile(file, self.bookmarks[idx])
                        
                        
if __name__ == '__main__': 
    b=backupfile()
    """Backup thread"""
    thread = threading.Thread(target=b.backup_automatically)
    thread.setDaemon(True)
    thread.start()
    """Thread that receives user input"""
    thread2 = threading.Thread(target=b.getinput)
    thread2.start()
