import requests
from django.core.management.base import BaseCommand
from games.models import Game
from nltk.tokenize import word_tokenize

class Command(BaseCommand):
    help = 'Fetch data from itch.io'

    def handle(self, *args, **kwargs):
        response = requests.get('YOUR_ITCH_IO_API_ENDPOINT')
        games_data = response.json()
        
        for game in games_data:
            tokens = word_tokenize(game['description'])
            Game.objects.create(
                title=game['title'],
                description=game['description'],
                tags=",".join(game.get('tags', [])),
                download_count=game.get('downloads', 0),
                tokenized_description=" ".join(tokens)
            )
        self.stdout.write(self.style.SUCCESS('Data fetched and stored successfully!'))
