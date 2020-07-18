import github


def get_files_from_repo(repo, path):
    contents = repo.get_contents(path=path)
    for content in contents:
        if content.type == 'dir':
            for _content in get_files_from_repo(repo, content.path):
                yield _content
        else:
            yield content


def get_repo(fullname, g: github.Github):
    try:
        return g.get_repo(full_name_or_id=fullname)
    except Exception as e:
        print(e)
        raise Exception(f'Couldn\'t get repo: {fullname}')


def get_students_repositories(g: github.Github, org_name, repo_filter):
    try:
        org = g.get_organization(login=org_name)
        student_repos = list(
            filter(
                lambda repo: repo_filter in repo.name,
                org.get_repos()
            )
        )
        return student_repos
    except Exception as e:
        print(e)
        raise Exception(f'Couldn\'t get organization: {org_name}')
