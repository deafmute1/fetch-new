# std 
from pathlib import Path
import os
import logging
import time
import signal
import sys
import shutil
import pprint
from typing import Union
# internal
import config 
# 3rd party 
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent, EVENT_TYPE_MOVED, EVENT_TYPE_CREATED

def main(): 
    logging.basicConfig(level=config.LOG_LEVEL, format='%(asctime)s - %(message)s')
    for value in config.VALID_CONFIG_VALUES: 
        logging.info('{}: {}'.format(value, pprint.pformat(getattr(config, value))))
    app = Main()
    app.run()

def wait_on_file_transfer(file: Path) -> bool:
    size2 = -1
    logging.debug("IMPORT: Waiting on {} to finish transfering".format(file))
    time_start = time.time()
    while file.is_file():
        if (time.time() > time_start + 60 * config.TRANSFER_TIMEOUT): 
            logging.info("IMPORT: Timeout reached whilst waiting for {} to transfer".format(file))
            return False 
        try:
            size1 = file.stat().st_size
            if size1 == size2:
                break
            time.sleep(2)
            size2 = file.stat().st_size 
        except FileNotFoundError: 
            # avoid exceptions when calling stat() on a temp file (such as created by wget, rsync etc)
            continue
    if file.is_file():
        logging.info("IMPORT: Transfer for file {} finished".format(file))
        return True 
    else:
        logging.info("IMPORT: File {} deleted while waiting for transfer".format(file))
        return False # inform caller if file was deleted during transfer (likely to be a temp file)

def copy_file(source: Path, dest: Path) -> None: 
    if not dest.is_dir(): 
        logging.critical("Destination {} is not a directory".format(dest))
    if not source.is_file(): 
        logging.critical("Source {} is not a file".format(source))
    copied = Path(shutil.copy2(source, dest)).resolve()
    if config.CHMOD is not None: 
        copied.chmod(config.CHMOD)
    os.chown(copied, config.UID, config.GID)
    logging.info("COPY: Copied file {} to {}".format(source, copied))

def recursive_copy(source: Path, dest: Path) -> None:
    for dirpath, _, fnames in os.walk(str(source)): 
        for f in fnames:
            copy_file(Path(dirpath).joinpath(f), dest)

class NewFileEventHandler(FileSystemEventHandler):
    def __init__(self, dest: str) -> None: 
        self.dest = Path(dest)

    def on_any_event(self, event: FileSystemEvent) -> None:
        logging.info('IMPORT: New file event {} of type {}'.format(event.src_path, event.event_type))
        if (
            event.event_type in (EVENT_TYPE_CREATED, EVENT_TYPE_MOVED) and 
            not event.is_directory  
        ):
            logging.info('IMPORT: Handling event {} of type {}'.format(event.src_path, event.event_type))
            if event.event_type == EVENT_TYPE_MOVED: 
                path = Path(event.dest_path)
            else: 
                path = Path(event.src_path)

            if (wait_on_file_transfer(path)): 
                copy_file(path, self.dest)

class Main(): 
    def __init__(self): 
        self.observer = Observer()
        signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)        

    def run(self): 
        if (config.MODE.casefold() == "ONESHOT".casefold()):
            self.start_oneshot()
            sys.exit(0)
        elif (config.MODE.casefold() == "NEW".casefold()):
            self.start_watchdog()
            self.enter_watchdog_thread()
        elif (config.MODE.casefold() == "BOTH".casefold()): 
            self.start_oneshot()
            self.start_watchdog()
            self.enter_watchdog_thread()
        else: 
            logging.critical("MAIN: Failed to start Main; is IMPORT_MODE valid?")

    def start_oneshot(self):
        logging.info("MAIN: Starting ONESHOT mode")
        recursive_copy(config.SOURCE, config.DESINATION)
        logging.info("MAIN: Finished ONESHOT mode")

    def start_watchdog(self):
        logging.info("MAIN: Starting NEW mode")
        self.observer.schedule(NewFileEventHandler(config.DESTINATION), config.SOURCE, recursive=True)

    def enter_watchdog_thread(self):
        self.observer.start()
        self.observer.join()
        logging.critical("MAIN: Observer thread terminated - exiting")
        sys.exit()

    def _signal_handler(self, *args) -> None:
        logging.critical('MAIN: Recieved SIGHUP or SIGTERM')
        sys.exit("MAIN: Exiting due to SIGHUP/SIGTERM")

if __name__ == "__main__":
    main()