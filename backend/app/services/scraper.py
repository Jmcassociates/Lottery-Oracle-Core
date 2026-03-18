import requests
from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)

class JackpotScraper:
    """
    JMc - Scrapes valottery.com to get the live jackpot amounts and next draw dates.
    Using specific CSS classes derived from the live HTML structure.
    """
    
    @staticmethod
    def get_live_data():
        games = {
            "Powerball": {
                "url": "https://www.valottery.com/data/draw-games/powerball",
                "game_id": "game-20",
                "type": "scrape"
            },
            "MegaMillions": {
                "url": "https://www.valottery.com/data/draw-games/megamillions",
                "game_id": "game-15",
                "type": "scrape"
            },
            "Cash4Life": {
                "type": "fixed",
                "jackpot": "$1,000/Day",
                "next_draw": "Draws Daily 9:00 PM"
            },
            "Cash5": {
                "url": "https://www.valottery.com/data/draw-games/cash5",
                "game_id": "game-1030",
                "type": "scrape_amount_only",
                "next_draw": "Draws Daily 11:00 PM"
            },
            "Pick5": {
                "type": "fixed",
                "jackpot": "$50,000 Top Prize",
                "next_draw": "Draws Daily 1:59 PM & 11:00 PM"
            },
            "Pick4": {
                "type": "fixed",
                "jackpot": "$5,000 Top Prize",
                "next_draw": "Draws Daily 1:59 PM & 11:00 PM"
            },
            "Pick3": {
                "type": "fixed",
                "jackpot": "$500 Top Prize",
                "next_draw": "Draws Daily 1:59 PM & 11:00 PM"
            }
        }
        
        results = {}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        for game, config in games.items():
            if config.get("type") == "fixed":
                results[game] = {
                    "jackpot": config["jackpot"],
                    "next_draw": config["next_draw"]
                }
                continue

            try:
                res = requests.get(config["url"], headers=headers, timeout=10)
                res.raise_for_status()
                soup = BeautifulSoup(res.text, 'html.parser')
                
                jackpot_str = "Unknown"
                date_str = config.get("next_draw", "Unknown")
                
                # Find the specific game card wrapper
                game_card = soup.find('a', id=config["game_id"])
                
                if game_card:
                    amount_elem = game_card.find('p', class_='amount')
                    if amount_elem:
                        jackpot_str = amount_elem.get_text(strip=True)
                        
                    if config.get("type") == "scrape":
                        date_elem = game_card.find('span', class_='est-val-next-draw-latest-draw')
                        if date_elem:
                            text = date_elem.get_text(strip=True)
                            if 'Next Drawing:' in text or 'Next Draw:' in text:
                                date_str = text.replace('Next Drawing:', '').replace('Next Draw:', '').strip()
                
                results[game] = {
                    "jackpot": jackpot_str,
                    "next_draw": date_str
                }
            except Exception as e:
                logger.error(f"Failed to scrape {game} jackpot: {e}")
                results[game] = {
                    "jackpot": "Error fetching",
                    "next_draw": "Error fetching"
                }
                
        return results
