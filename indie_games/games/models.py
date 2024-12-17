from django.db import models


class ClusteredGame(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.TextField()
    price = models.FloatField()
    image_path = models.CharField(max_length=255)
    rating = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    cluster = models.IntegerField()
    cluster_label = models.CharField(max_length=255)

    class Meta:
        app_label = 'clustered_games'
        managed = False  # Since the table is already created
        db_table = 'games_with_clusters'
