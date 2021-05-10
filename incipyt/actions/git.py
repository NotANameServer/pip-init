from incipyt import hooks
from incipyt._internal import utils
from incipyt._internal.dumpers import Requirement


class Git:
    """Action to add Git to :class:`incipyt.system.Hierarchy`."""

    def __init__(self):
        hooks.VCSIgnore.register(self._hook)

    def add_to(self, hierarchy):
        """Add git configuration to `hierarchy`, do nothing.

        :param hierarchy: The actual hierarchy to update with git configuration.
        :type hierarchy: :class:`incipyt.system.Hierarchy`
        """

    def _hook(self, hierarchy, value):
        gitignore = hierarchy.get_configuration(Requirement.make(".gitignore"))
        if None not in gitignore:
            gitignore[None] = []

        gitignore[None].append(value)

    def __str__(self):
        return "git"

    def pre(self, workon, environment):
        """Run `git init`.

        :param workon: Work-on folder.
        :type workon: :class:`pathlib.Path`
        :param environment: Environment used to do pre-action
        :type environment: :class:`incipyt.system.Environment`
        """
        environment.run(
            [
                "git",
                "init",
                str(workon),
            ]
        )

    def post(self, workon, environment):
        """Post-action for git, do nothing.

        :param workon: Work-on folder.
        :type workon: :class:`pathlib.Path`
        :param environment: Environment used to do post-action
        :type environment: :class:`incipyt.system.Environment`
        """
        environment.run(
            [
                "git",
                "-C",
                str(workon),
                "add",
                "--all",
            ]
        )
        environment.run(
            [
                "git",
                "-C",
                str(workon),
                "commit",
                "--message",
                utils.Requires(
                    "'feat: project {NAME} bootstrap by incipyt'",
                    sanitizer=utils.sanitizer_project,
                ),
            ]
        )