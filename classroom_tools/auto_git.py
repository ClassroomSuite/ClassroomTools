import argparse
import os
import threading
import time

import git

parser = argparse.ArgumentParser()
parser.add_argument(
    '--filename',
    required=True,
    help='File that will be automatically be added, committed and pushed'
)

if __name__ == '__main__':
    args = parser.parse_args()
    try:
        print('Enter CRTL+C to exit process')
        repo_dir = os.path.realpath(os.curdir)
        filename = os.path.join(repo_dir, args.filename)
        r = git.Repo.init(repo_dir)
        timeout = threading.Event()
        timeout.clear()
        t = threading.Timer(3600 * 3, function=timeout.set)
        t.start()
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
                time.sleep(60)
    except KeyboardInterrupt:
        t.cancel()
        print('\nExiting...\n')
