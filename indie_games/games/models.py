from django.db import models

class Itch(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.CharField(max_length=255, blank=True, null=True)
    download_count = models.IntegerField(default=0)
    tokenized_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class Indie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.CharField(max_length=255, blank=True, null=True)
    download_count = models.IntegerField(default=0)
    tokenized_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class GOG(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.CharField(max_length=255, blank=True, null=True)
    download_count = models.IntegerField(default=0)
    tokenized_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    


