class EmptyToken(Exception):
    def __init__(self, permissions):
        super().__init__(
            f'Verify that the repository has access to the personal access and has permissions: {permissions}')
