import argparse
import datetime
import glob
import os
from typing import Iterable

import git
import github
import mosspy

from classroom_tools import github_utils

parser = argparse.ArgumentParser()
parser.add_argument(
    '--user_id',
    help='Obtain a moss userid by following instructions from http://theory.stanford.edu/~aiken/moss/'
)
parser.add_argument(
    '--report_name',
    default='report',
    help='Obtain a moss userid by following instructions from http://theory.stanford.edu/~aiken/moss/'
)
parser.add_argument(
    '--token',
    help='GitHub personal access token with repo permissions'
)
parser.add_argument(
    '--org_name',
    help='GitHub organization with student repositories (for multiples student repositories)'
)
parser.add_argument(
    '--repo_filter',
    help='Prefix to filter repositories for as given assignment or exercise (for multiples student repositories)'
)
parser.add_argument(
    '--base_files_repo_fullname',
    help='Repo containing base files in format: "Owner/RepoName".'
         'All paths specified with --paths will be used as base files paths.'
)
parser.add_argument(
    '--paths',
    default=[],
    nargs='*',
    help='Paths to files (or directories with option -d) located in student repositories.'
         'Files will be subjected to Moss.'
)
parser.add_argument(
    '-l',
    default='python',
    choices=mosspy.Moss.languages,
    help='The -l option specifies the source language of the tested programs'
)
parser.add_argument(
    '-d',
    default=False,
    action='store_true',
    help=
    """
    The -d option specifies that submissions are by directory, not by file.
    That is, files in a directory are taken to be part of the same program,
    and reported matches are organized accordingly by directory.
    
    Example: Compare the programs foo and bar, which consist of .c and .h
    files in the directories foo and bar respectively.
        moss -d foo/*.c foo/*.h bar/*.c bar/*.h
    
    Example: Each program consists of the *.c and *.h files in a directory under
    the directory "assignment1."
        moss -d assignment1/*/*.h assignment1/*/*.c
    """
)
parser.add_argument(
    '-m',
    default=10,
    type=int,
    help=
    """
    The -m option sets the maximum number of times a given passage may appear
    before it is ignored.  A passage of code that appears in many programs
    is probably legitimate sharing and not the result of plagiarism.  With -m N,
    any passage appearing in more than N programs is treated as if it appeared in 
    a base file (i.e., it is never reported).  Option -m can be used to control
    moss' sensitivity.  With -m 2, moss reports only passages that appear
    in exactly two programs.  If one expects many very similar solutions
    (e.g., the short first assignments typical of introductory programming
    courses) then using -m 3 or -m 4 is a good way to eliminate all but
    truly unusual matches between programs while still being able to detect
    3-way or 4-way plagiarism.  With -m 1000000 (or any very 
    large number), moss reports all matches, no matter how often they appear.  
    The -m setting is most useful for large assignments where one also a base file 
    expected to hold all legitimately shared code.  The default for -m is 10.
    
    Examples:
        moss -l pascal -m 2 *.pascal 
        moss -l cc -m 1000000 -b mycode.cc asn1/*.cc
    """
)
parser.add_argument(
    '-c',
    default="",
    help=
    """
    The -c option supplies a comment string that is attached to the generated
    report.  This option facilitates matching queries submitted with replies
    received, especially when several queries are submitted at once.
    
    Example:
        moss -l scheme -c "Scheme programs" *.sch
    """
)
parser.add_argument(
    '-n',
    default=250,
    type=int,
    help=
    """
    The -n option determines the number of matching files to show in the results.
    The default is 250.
    
    Example:
        moss -c java -n 200 *.java
    """
)
parser.add_argument(
    '-x',
    default=False,
    action='store_true',
    help=
    """
    The -x option sends queries to the current experimental version of the server.
    The experimental server has the most recent Moss features and is also usually
    less stable (read: may have more bugs).
    
    Example:
        moss -x -l ml *.ml
    """
)


def add_base_files(moss: mosspy.Moss, base_files: Iterable, repo: github.Repository.Repository):
    print(f'Adding base files from repo: {repo.full_name}')
    for path in base_files:
        print(f'\t{path}')
        content_file = repo.get_contents(path=path)
        head, tail = os.path.split(path)
        file_path = f'{repo.name}_{tail}'
        with open(file_path, 'wb') as f:
            f.write(content_file.decoded_content)
        moss.addBaseFile(file_path=file_path, display_name=file_path)


def add_paths(moss: mosspy.Moss, paths: Iterable, repositories: Iterable):
    print('Adding student files:')
    for path in paths:
        if '*' in path:
            for repo in repositories:
                print(f'\t{repo.name}')
                content_files = github_utils.get_files_from_repo(repo=repo, path='')
                for content_file in content_files:
                    with open(content_file.path, 'wb') as f:
                        f.write(content_file.decoded_content)
                for file_path in glob.glob(path):
                    head, tail = os.path.split(file_path)
                    new_file_path = f'{head}{repo.name}_{tail}'
                    os.rename(file_path, new_file_path)
                    moss.addFile(file_path=new_file_path, display_name=f'{repo.name}_{tail}')
                    print(f'\t\t{tail}')
        else:
            for path in paths:
                for repo in repositories:
                    print(f'\t{repo.name}')
                    content_file = repo.get_contents(path=path)
                    head, tail = os.path.split(path)
                    file_path = f'{repo.name}_{tail}'
                    with open(file_path, 'wb') as f:
                        f.write(content_file.decoded_content)
                    moss.addFile(file_path=file_path, display_name=file_path)
                    print(f'\t\t{tail}')


def save_report(moss, report_name, report_url):
    time_str = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    report_path = f'moss_reports/{report_name}_{time_str}.html'
    head, tail = os.path.split(report_path)
    if not os.path.exists(os.path.abspath(head)): os.makedirs(head)
    moss.saveWebPage(url=report_url, path=report_path)
    root, ext = os.path.splitext(report_path)
    new_report_path = root + '.md'
    os.rename(report_path, new_report_path)
    git_repo = git.repo.Repo()
    git_repo.index.add([new_report_path])
    git_repo.index.commit(f'Moss report: {report_name}')
    fetch_info = git_repo.remote('origin').pull()
    git_repo.remote('origin').push()
    print(f'Report copy located at: {new_report_path}')


def main(args):
    print('\n\n' + 'Submitting files to Moss'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    github_utils.verify_token(args.token)
    moss = mosspy.Moss(args.user_id, language=args.l)
    moss.setIgnoreLimit(args.m)
    moss.setCommentString(args.c)
    moss.setNumberOfMatchingFiles(args.n)
    moss.setExperimentalServer(opt=int(args.x))
    moss.setDirectoryMode(mode=int(args.d))
    repositories = github_utils.get_students_repositories(
        token=args.token,
        org_name=args.org_name,
        repo_filter=args.repo_filter
    )
    if args.base_files_repo_fullname != '':
        repo = github_utils.get_repo(fullname=args.base_files_repo_fullname, token=args.token)
        add_base_files(moss=moss, base_files=args.paths, repo=repo)

    print(f'Org: {args.org_name}')
    add_paths(moss=moss, paths=args.paths, repositories=repositories)
    report_url = moss.send()
    print(f'Report url: {report_url}')
    save_report(moss=moss, report_name=args.report_name, report_url=report_url)


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
