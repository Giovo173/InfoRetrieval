from django.shortcuts import render
from games.models import Game
from django.db.models import Q
from mapreduce import search_games
from .models import ClusteredGame

def search_games_view(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        db_paths = ['db1.sqlite3', 'db2.sqlite3', 'db3.sqlite3']
        results = search_games(query, db_paths)

    return render(request, 'index.html', {'query': query, 'results': results})

def clustered_games_view(request):
    selected_cluster = request.GET.get('cluster')
    clusters = ClusteredGame.objects.values('cluster', 'cluster_label').distinct()
    games = ClusteredGame.objects.filter(cluster=selected_cluster) if selected_cluster else ClusteredGame.objects.all()
    context = {'clusters': clusters, 'games': games, 'selected_cluster': selected_cluster}
    return render(request, 'clustered_games.html', context)
