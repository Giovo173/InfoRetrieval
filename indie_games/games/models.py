from django.db import models

class Game(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.CharField(max_length=255, blank=True, null=True)
    download_count = models.IntegerField(default=0)
    tokenized_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

