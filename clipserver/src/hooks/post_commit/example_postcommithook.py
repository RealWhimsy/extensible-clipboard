from hooks.post_commit.basepostcommithook import BasePostCommitHook


class ExamplePostCommitHook(BasePostCommitHook):

    def do_work(self, data):
        print(data)
        """
        This is the base hook for pre-commit hooks. A pre-commit hook is called right before the clipboard request is persisted
        and may modify the request or deny further processing (this may allow for implementing auth-mechanisms)
        """
        return data
