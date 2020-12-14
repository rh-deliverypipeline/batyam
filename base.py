from abc import ABCMeta, abstractmethod
from github import Github
import gitlab
import github
import os
import ssl
import json
from subprocess import check_output
from datetime import datetime
from time import time
from app import logging


class Server(metaclass=ABCMeta):
    """Abstract class for the different git servers."""

    def __init__(self, name, host):
        self.name = name
        self.host = host
        self.namespaces = {}
        self.users = {}

    @abstractmethod
    def _connect(self):
        """Establish a connection to the server, in case one is required."""
        pass

    @abstractmethod
    def _set_namespaces(self, namespaces):
        """Sets the requested server's namespaces to work with."""
        pass

    @abstractmethod
    def get_ccs(self):
        """Pulls and yield CC from the requested server's namespaces."""
        pass

    @abstractmethod
    def cc_to_dict(self, cc):
        """Converts a CC to a specific dictionary structure"""
        pass

    @staticmethod
    def convert_timestamp_to_time_passed(time_var):
        """Converts an epoch (Unix time) timestamp to a 'X hours/days ago' string"""
        epoch_time_passed = time() - time_var
        days_passed = epoch_time_passed // 86400
        if days_passed == 0.0:
            return 'today'
        else:
            return f'{int(days_passed)} days ago'


class Gitlab(Server):
    def __init__(self, host, namespaces, users, repos):
        super().__init__('GitLab', host)
        self.gl = self._connect()
        self._set_namespaces(namespaces)
        self._set_personal_users(users)
        self.repos = repos

    def _connect(self):
        try:
            gl = gitlab.Gitlab(
                self.host,
                private_token=os.getenv("GITLAB_TOKEN"),
                ssl_verify=False
            )
            return gl
        except gitlab.exceptions.GitlabAuthenticationError:
            logging.error('Gitlab Authentication Failed.')

    def _set_namespaces(self, groups):
        """Search and set the requested GitLab namespaces (groups) to work with.
        In case the namespace code is not found within GitLab, an alert will be outputted.
        """

        if groups:
            for group_id in groups:
                try:
                    self.namespaces[group_id] = self.gl.groups.get(group_id)
                except gitlab.exceptions.GitlabGetError:
                    logging.warning(f"GitLab group '{group_id}' not found.")

    def _set_personal_users(self, users):
        """Search and set the requested GitLab users to work with their personal repos.
        In case the username is not found within GitLab, an alert will be outputted.
        """

        if users:
            for username in users:
                try:
                    self.users[username] = self.gl.users.list(username=username)[0]
                except IndexError:
                    logging.warning(f"GitLab user '{username}' not found.")

    def get_ccs(self, state='opened', order='updated_at'):
        for group in self.namespaces:
            for project in self.gl.groups.get(group).projects.list(all=True):
                if project.attributes['name'] in self.repos or self.repos == ['*']:
                    for mr in self.gl.projects.get(project.id).mergerequests.list(state=state, order_by=order):
                        yield mr
        for user in self.users.values():
            for project in user.projects.list():
                if project.attributes['name'] in self.repos or self.repos == ['*']:
                    for mr in self.gl.projects.get(project.id).mergerequests.list(state=state, order_by=order):
                        yield mr

    def cc_to_dict(self, mr):
        project = self.gl.projects.get(mr.attributes['project_id'])
        return {
            'project': project.attributes['name'],
            'last updated': self.convert_timestamp_to_time_passed(
                datetime.strptime(mr.attributes['updated_at'], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()),
            'contributor': mr.attributes['author']['name'],
            'state': 'open' if mr.attributes['state'] == 'opened' else mr.attributes['state'],
            'title': mr.attributes['title'],
            'web_url': mr.attributes['web_url'],
        }


class GitHub(Server):
    def __init__(self, host, namespaces, repos):
        super().__init__('GitHub', host)
        self.gh = self._connect()
        if self.gh:
            self._set_namespaces(namespaces)
            self.repos = repos

    def _connect(self):
        gh = Github(os.getenv("GITHUB_TOKEN"))
        try:
            gh.get_user().login
        except github.GithubException as e:
            logging.warning(f'No valid GitHub token entered, authentication failed: {e}.')
            return
        except github.BadCredentialsException as e:
            logging.warning(f'GitHub User authentication failed: {e}.')
            return
        return gh

    def _set_namespaces(self, namespaces):
        """Search and set the requested Github namespaces (orgs) to work with.
        In case the namespace name is not found within Github, an alert will be outputted.
        """

        if namespaces:
            for org_name in namespaces:
                try:
                    self.namespaces[org_name] = self.gh.get_organization(org_name)
                except github.UnknownObjectException:
                    logging.warning(f"Github org '{org_name}' not found.")

    def get_ccs(self, state='open', sort='updated_at', base='master'):
        for org in self.namespaces:
            for repo in self.namespaces[org].get_repos():
                if repo.name in self.repos or self.repos == ['*']:
                    for pr in repo.get_pulls(state, sort, base):
                        yield pr

    def cc_to_dict(self, pr):
        return {
            'project': pr.base.repo.name,
            'last updated': self.convert_timestamp_to_time_passed(pr.updated_at.timestamp()),
            'contributor': self.gh.get_user(pr.user.login).name or self.gh.get_user(pr.user.login).login,
            'state': pr.state,
            'title': pr.title,
            'web_url': pr.html_url,
        }


class Gerrit(Server):
    def __init__(self, host, bot_users, namespaces):
        super().__init__('Gerrit', host)
        self.query_limit = 50
        self._connect()
        self._set_namespaces(namespaces)
        self._set_bot_users(bot_users)

    def _connect(self):
        pass

    def _set_bot_users(self, bot_users):
        self.bot_users = []
        if bot_users:
            for bot in bot_users:
                self.bot_users.append(bot)

    def _set_namespaces(self, projects):
        self.namespaces = projects

    def get_ccs(self, status='open'):
        """Pulls and yield CC from the requested Gerrit's namespaces using an SSH command.

              skip: Number of changes to skip.
              result_cnt: Keeping count of the number of results left to return.
              cc_content: Outputted JSON of CC from the ssh command.
              lines: Line-separated JSON copy of cc_content.
              patch: One gerrit CC.
        """

        for project in self.namespaces:
            skip = 0
            results_cnt = self.query_limit
            while results_cnt >= self.query_limit:
                cc_content = check_output([
                    'ssh', self.host, '-p', '29418', 'gerrit', 'query',
                    '--comments', '--all-approvals', '--format=JSON',
                    '--start', str(skip), 'limit:' + str(self.query_limit),
                                          'project:' + project, 'status:' + status,
                ])
                lines = cc_content.splitlines()
                for line in lines:
                    patch = json.loads(line)
                    if patch.get('type') == 'stats' or patch.get('owner').get('name') in self.bot_users:
                        continue  # ignore output stats query
                    yield patch
                results_cnt = len(lines) - 1
                skip += results_cnt

    def cc_to_dict(self, patch):
        return {
            'project': patch.get('project'),
            'last updated': self.convert_timestamp_to_time_passed(patch.get('lastUpdated', 0)),
            'contributor': patch.get('owner').get('name'),
            'state': 'open' if patch.get('status') == 'NEW' else patch.get('status'),
            'title': patch.get('subject'),
            'web_url': patch.get('url'),
        }
