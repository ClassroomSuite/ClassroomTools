import argparse
import os
import threading
import time

import git

PULL_DELAY = 10
PUSH_DELAY = 30

parser = argparse.ArgumentParser()
parser.add_argument(
    '--filename',
    required=True,
    help='File that will automatically be added, committed and pushed'
)

if __name__ == '__main__':
    args = parser.parse_args()
    try:
        print(f'Pulling every {PULL_DELAY} seconds')
        print(f'Pushing every {PUSH_DELAY} seconds')
        print('Enter CRTL+C to exit process')
        repo_dir = os.path.realpath(os.curdir)
        filename = os.path.join(repo_dir, args.filename)
        git_ = git.Repo(repo_dir).git
        timeout = threading.Event()
        timeout.clear()
        timer = threading.Timer(3600 * 3, function=timeout.set)
        timer.start()
        while not timeout.is_set():
            try:
                for _ in range(max(PUSH_DELAY // PULL_DELAY, 1)):
                    try:
                        git_.add(filename)
                        git_.commit(m='Auto commit')
                    except git.GitCommandError:
                        pass
                    git_.stash('push')
                    git_.pull(rebase=True)
                    time.sleep(PULL_DELAY)
                git_.push()
            except:
                pass
    except KeyboardInterrupt:
        timer.cancel()
        print('\nExiting...\n')
