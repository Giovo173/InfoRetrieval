from itch_scraper import main
from steam_scraper import main_steam
from GOG_scraper import scrape

def scrape_all():
    main(20) #change the number to have more games
    main_steam(25) #change the number to have more games
    scrape(20) #change the number to have more games