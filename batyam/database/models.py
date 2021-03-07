from django.db import models


class Contributor(models.Model):
    name = models.CharField(max_length=100)
    github_id = models.CharField(max_length=20, default=None, blank=True, null=True)
    gitlab_id = models.CharField(max_length=20, default=None, blank=True, null=True)
    gerrit_id = models.CharField(max_length=20, default=None, blank=True, null=True)


class Project(models.Model):
    name = models.CharField(max_length=255)


class CodeContribution(models.Model):
    STATE_CHOICES = (
        ('OP', 'Open'),
        ('CD', 'Closed')
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE)
    last_updated = models.CharField(max_length=255)
    url = models.URLField(max_length=255, null=False, blank=True)
    title = models.CharField(max_length=255)
    state = models.CharField(choices=STATE_CHOICES , max_length=2)
    vendor = models.CharField(max_length=8)
    team = models.CharField(max_length=50)
