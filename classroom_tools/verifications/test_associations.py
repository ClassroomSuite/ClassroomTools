import argparse
import runpy

import classroom_tools.grading.create_grades

parser = argparse.ArgumentParser('Validate test_files and test_associations.json')
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo permissions'
)
parser.add_argument(
    '--template_repo_fullname',
    required=True,
    help='Template repo used to create student repositories in format: OrgName/RepoName'
)
parser.add_argument(
    '--test_file_path',
    required=True,
    help='Path to test file'
)
parser.add_argument(
    '--test_associations_path',
    required=True,
    default='settings/test_associations.json',
    help='Path to test_associations.json'
)


def main(args):
    print('\n\n' + 'Verifying test file and test_associations.json'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    print(f'\nCreating logs/tests_results.txt by running test file: {args.test_file_path}')
    runpy.run_path(
        path_name=args.test_file_path,
        run_name='__main__',
        alter_sys=True
    )
    print('\nCreating logs/grades.json module: classroom_tools.grading.create_grades')
    classroom_tools.grading.create_grades.main(['--test_associations_path', args.test_associations_path])


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
