import github
from colorama import Fore, Style


def verify_token(token):
    try:
        g = github.Github(login_or_token=token)
        print(
            f'Personal access token rate limiting:\n'
            f'\t{g.rate_limiting[0]} remaining / {g.rate_limiting[1]} requests per hour'
        )
        print('Personal access token permissions (oauth scopes):\n\t' + '\n\t'.join(g.oauth_scopes) + '\n')
    except github.BadCredentialsException as e:
        raise Exception(f'{Fore.RED}Token expired or not provided{Style.RESET_ALL}')


def delete_file(repo, path, branch='master', message='Deleted file'):
    try:
        contents = repo.get_contents(path=path, ref=branch)
        repo.delete_file(
            path=path,
            message=message,
            sha=contents.sha,
            branch=branch
        )
        print(f'Deleted: {path}\n from: {repo.full_name}')
    except github.UnknownObjectException:
        print(f'File doesn\'t exist: {path}')


def copy_file_to_repo(file, repo, branch='master', message='Auto sync with template repo'):
    try:
        print(file.path)
        old_file = repo.get_contents(path=file.path, ref=branch)
        print(old_file.path)
        if file.sha != old_file.sha:
            repo.update_file(
                path=old_file.path,
                message=message,
                content=file.decoded_content,
                sha=old_file.sha,
                branch=branch
            )
    except github.UnknownObjectException:
        repo.create_file(
            path=file.path,
            message=message,
            content=file.decoded_content,
            branch=branch
        )


def get_files_from_repo(repo, path):
    contents = repo.get_contents(path=path)
    for content in contents:
        if content.type == 'dir':
            for _content in get_files_from_repo(repo, content.path):
                yield _content
        else:
            yield content


def get_repo(fullname, token=''):
    try:
        g = github.Github(login_or_token=token)
        return g.get_repo(full_name_or_id=fullname)
    except Exception as e:
        print(e)
        raise Exception(f'Couldn\'t get repo: {fullname}')


def get_students_repositories(token, org_name, repo_filter):
    repo_filter = repo_filter.replace(' ', '')
    if repo_filter == '':
        raise Exception(f'{Fore.RED}repo_filter in settings/variables.txt can\'t be empty')
    try:
        g = github.Github(login_or_token=token)
        org = g.get_organization(login=org_name)
    except github.GithubException as e:
        print(f'{Fore.RED}Couldn\'t get organization: {org_name}')
        raise e
    org_repos = list(org.get_repos())
    student_repos = list(
        filter(
            lambda repo: repo_filter in repo.name,
            org_repos
        )
    )
    if len(org_repos) == 0:
        raise Exception(f'{Fore.RED}Org has no repositories: {org_name}')
    elif len(student_repos) == 0:
        print(f'{Fore.YELLOW}Here are the repositories in org: {org_name}')
        for repo in org_repos:
            print(f'{Fore.YELLOW}\t{repo.name}')
        raise Exception(f'{Fore.RED}No repositories matched: {repo_filter}')
    return student_repos


def delete_all_workflows(repo, branch='master'):
    deleted = set()
    try:
        contents = repo.get_contents(path='.github/workflows', ref=branch)
        for content_file in contents:
            repo.delete_file(
                path=content_file.path,
                message='Auto deleted workflow',
                sha=content_file.sha,
                branch=branch
            )
            deleted.add(content_file.path)
    except github.UnknownObjectException:
        pass
    return deleted


def add_workflow(repo, path, content):
    try:
        old_file = repo.get_contents(path=path)
        repo.update_file(
            path=path,
            message='Auto added workflow',
            content=content,
            sha=old_file.sha,
            branch='master'
        )
    except github.UnknownObjectException:
        repo.create_file(
            path=path,
            message='Auto added workflow',
            content=content,
            branch='master'
        )
