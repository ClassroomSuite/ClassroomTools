import argparse
import os
import threading
import time

import git

DELAY = 30

parser = argparse.ArgumentParser()
parser.add_argument(
    '--filename',
    required=True,
    help='File that will automatically be added, committed and pushed'
)

if __name__ == '__main__':
    args = parser.parse_args()
    try:
        print(f'Syncing every {DELAY} seconds')
        print('Enter CRTL+C to exit process')
        repo_dir = os.path.realpath(os.curdir)
        filename = os.path.join(repo_dir, args.filename)
        r = git.Repo.init(repo_dir)
        timeout = threading.Event()
        timeout.clear()
        timer = threading.Timer(3600 * 3, function=timeout.set)
        timer.start()
        while not timeout.is_set():
            try:
                r.index.add([filename])
                r.index.commit("Auto commit")
                r.git.stash('save')
                fetch_info = r.remote('origin').pull()
                r.remote('origin').push()
                r.heads.master.log()
            except Exception as e:
                print(e)
            finally:
                time.sleep(DELAY)
    except KeyboardInterrupt:
        timer.cancel()
        print('\nExiting...\n')
