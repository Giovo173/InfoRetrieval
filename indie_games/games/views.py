from django.shortcuts import render
from django.db.models import Q
from games.mapreduce import search_games
from .models import ClusteredGame
import re

from django.shortcuts import render
from django.db.models import Q
from games.mapreduce import search_games
from .models import ClusteredGame
import re

def parse_price(price):
    """Extract numeric price from a string containing currency."""
    match = re.search(r'[\d.]+', price)
    return float(match.group()) if match else None

def filter_results(results, price_range):
    """Filter results by price range."""
    filtered_results = []
    for r in results:
        raw_price = r.get('price')
        numeric_price = parse_price(raw_price) if raw_price else None

        # Price filter conditionplatform
        price_condition = (
            (price_range == "free" and (numeric_price == 0 or raw_price.lower() == "free")) or
            (price_range == "low" and numeric_price is not None and numeric_price < 10) or
            (price_range == "mid" and numeric_price is not None and 10 <= numeric_price <= 50) or
            (price_range == "high" and numeric_price is not None and numeric_price > 50) or
            not price_range  # No filter applied
        )

        if price_condition:
            filtered_results.append(r)

    return filtered_results

def search_games_view(request):
    query = request.GET.get('q', '')
    price_range = request.GET.get('price_range', '')
    results = []

    db_table_map = [
        ('./steam.db', 'steam'),
        ('./itchio.db', 'itchio'),
        ('./gog.db', 'gog')
    ]

    if query:
        results = search_games(query, db_table_map)

    if results:
        results = filter_results(results, price_range)

    return render(request, 'index.html', {
        'query': query,
        'results': results,
        'price_range': price_range,
    })

def browse_games_view(request):
    price_range = request.GET.get('price_range', '')
    db_table_map = [
        ('./steam.db', 'steam'),
        ('./itchio.db', 'itchio'),
        ('./gog.db', 'gog')
    ]
    results = search_games("", db_table_map)

    if results:
        results = filter_results(results, price_range)

    return render(request, 'index.html', {
        'results': results,
        'price_range': price_range,
    })

    

def clustered_games_view(request):
    selected_cluster = request.GET.get('cluster')
    clusters = ClusteredGame.objects.values('cluster', 'cluster_label').distinct()
    games = ClusteredGame.objects.filter(cluster=selected_cluster) if selected_cluster else ClusteredGame.objects.all()
    context = {'clusters': clusters, 'games': games, 'selected_cluster': selected_cluster}
    return render(request, 'clustered_games.html', context)
