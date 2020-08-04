import github
from colorama import Fore, Style


def verify_token(token):
    try:
        g = github.Github(login_or_token=token)
        print(
            f'Authenticated user rate limiting:\n'
            f'\t{g.rate_limiting[0]} remaining / {g.rate_limiting[1]} requests per hour'
        )
        print('Permissions (oauth scopes):\n\t' + '\n\t'.join(g.oauth_scopes))
    except github.BadCredentialsException as e:
        print(f'{Fore.RED}Token expired or not provided')
        print(Style.RESET_ALL)
        raise e


def delete_file(repo, path):
    try:
        contents = repo.get_contents(path=path)
        repo.delete_file(
            path=path,
            message='Deleted file',
            sha=contents.sha,
            branch='master',
        )
        print(f'Deleted: {path}\n from: {repo.full_name}')
    except github.UnknownObjectException:
        print(f'File doesn\'t exist: {path}')


def copy_file_to_repo(file, repo, message='Auto sync with template repo'):
    try:
        old_file = repo.get_contents(path=file.path)
        if file.sha != old_file.sha:
            repo.update_file(
                path=old_file.path,
                message=message,
                content=file.decoded_content,
                sha=old_file.sha,
                branch='master'
            )
    except github.UnknownObjectException:
        repo.create_file(
            path=file.path,
            message=message,
            content=file.decoded_content,
            branch='master'
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
    try:
        g = github.Github(login_or_token=token)
        org = g.get_organization(login=org_name)
        org_repos = org.get_repos()
        student_repos = list(
            filter(
                lambda repo: repo_filter in repo.name,
                org_repos
            )
        )
        if len(student_repos) == 0:
            print(f'No repositories matched: {repo_filter}')
            print(f'Repositories in org: {org_name}')
            print('\n\t'.join(org_repos))
        return student_repos
    except Exception as e:
        print(e)
        raise Exception(f'Couldn\'t get organization: {org_name}')


def delete_workflow(repo, path):
    print(f'\t\tRemoving: {path}')
    contents = repo.get_contents(path=path)
    repo.delete_file(
        path=path,
        message='Auto deleted workflow',
        sha=contents.sha,
        branch='master',
    )


def delete_all_workflows(repo):
    try:
        contents = repo.get_contents(path='.github/workflows/')
        for content_file in contents:
            delete_workflow(repo, path=content_file.path)
    except github.UnknownObjectException:
        pass


def add_workflow(repo, path, content):
    print(f'\t\tAdding: {path}')
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
