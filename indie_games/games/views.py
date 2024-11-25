from django.shortcuts import render
from games.models import Game
from django.db.models import Q

def search_games(request):
    query = request.GET.get('q', '')
    results = Game.objects.filter(
        Q(title__icontains=query) | Q(tokenized_description__icontains=query)
    ) if query else Game.objects.all()

    return render(request, 'games/search.html', {'games': results, 'query': query})
