import csv
import logging
from datetime import datetime
import requests
from sqlalchemy.orm import Session
from app.core.models import DrawRecord

logger = logging.getLogger(__name__)

class LotteryFetcher:
    """
    JMc - [2026-03-16] - Base class for all data ingestion. Defines the contract.
    All fetchers must implement fetch_data() and inherit sync_to_db().
    """
    game_name = "Base"
    state_code = "VA"
    
    def fetch_data(self) -> list[dict]:
        """
        JMc - [2026-03-16] - Must return a list of dicts: 
        [{'date': datetime, 'white_balls': [int], 'special_ball': int, 'multiplier': int}]
        """
        raise NotImplementedError
        
    def sync_to_db(self, db: Session):
        """
        JMc - [2026-03-16] - Standardized method to sync fetched data into the universal SQLite table.
        It strictly enforces the unique constraint (state_code, game_name, draw_date) to prevent duplicates.
        """
        try:
            raw_draws = self.fetch_data()
        except Exception as e:
            logger.error(f"Failed to fetch data for {self.game_name}: {e}")
            return False
            
        new_records = 0
        for draw in raw_draws:
            # Check if record exists
            exists = db.query(DrawRecord).filter(
                DrawRecord.state_code == self.state_code,
                DrawRecord.game_name == self.game_name,
                DrawRecord.draw_date == draw['date'].date()
            ).first()
            
            if not exists:
                # JMc - [2026-03-16] - For Combinatorial games, order doesn't matter, so we sort the balls
                # to ensure consistent hashing for the 'Never Picked Before' collision logic.
                sorted_whites = sorted(draw['white_balls'])
                white_str = ",".join(str(x) for x in sorted_whites)
                
                record = DrawRecord(
                    state_code=self.state_code,
                    game_name=self.game_name,
                    draw_date=draw['date'].date(),
                    white_balls=white_str,
                    special_ball=draw['special_ball'],
                    multiplier=draw.get('multiplier')
                )
                db.add(record)
                new_records += 1
                
        db.commit()
        logger.info(f"[{self.game_name}] Sync complete. Added {new_records} new draws.")
        return new_records


class VirginiaPowerballFetcher(LotteryFetcher):
    """
    JMc - [2026-03-16] - Fetches Powerball from the Virginia Lottery JSON API (CSV-like format).
    """
    game_name = "VirginiaPowerball"
    url = "https://www.valottery.com/api/v1/downloadall?gameId=20"

    def fetch_data(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()

        draws = []
        lines = response.text.splitlines()

        for line in lines:
            line = line.strip()
            if not line or 'All information' in line or 'Therefore' in line or 'Results for' in line:
                continue

            try:
                # Format: "3/4/2026; 7,14,42,47,56; Powerball: 6"
                parts = line.split(';')
                if len(parts) >= 3:
                    date_str = parts[0].strip()
                    date_parts = date_str.split('/')

                    if len(date_parts) == 3:
                        # M/D/YYYY format
                        month, day, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                        draw_date = datetime(year, month, day)

                        # JMc - [2026-03-16] - Current matrix format (2015-present).
                        # We aggressively drop legacy data that poisons the Markov models.
                        if draw_date >= datetime(2015, 10, 4):
                            numbers_str = parts[1].strip()
                            white_balls = [int(x.strip()) for x in numbers_str.split(',')]

                            ball_str = parts[2].strip()
                            if 'Powerball:' in ball_str:
                                powerball = int(ball_str.split('Powerball:')[1].strip())
                            else:
                                continue

                            draws.append({
                                'date': draw_date,
                                'white_balls': white_balls,
                                'special_ball': powerball,
                                'multiplier': None # VA API usually doesn't include PowerPlay in this string format
                            })
            except Exception as e:
                # Silently dropping rows is bad practice. We only catch ValueError/IndexError.
                continue
        return draws


class VirginiaMegaMillionsFetcher(LotteryFetcher):
    """
    JMc - [2026-03-16] - Fetches MegaMillions from the Virginia Lottery JSON API.
    """
    game_name = "VirginiaMegaMillions"
    url = "https://www.valottery.com/api/v1/downloadall?gameId=15"
    
    def fetch_data(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        
        draws = []
        lines = response.text.splitlines()
        
        for line in lines:
            line = line.strip()
            if not line or 'All information' in line or 'Therefore' in line or 'Results for' in line:
                continue
                
            try:
                # Format: "3/6/2026; 8,19,26,38,42; Mega Ball: 24"
                parts = line.split(';')
                if len(parts) >= 3:
                    date_str = parts[0].strip()
                    date_parts = date_str.split('/')
                    
                    if len(date_parts) == 3:
                        # M/D/YYYY format
                        month, day, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                        draw_date = datetime(year, month, day)
                        
                        # JMc - [2026-03-16] - The Matrix changed on April 8, 2025. 
                        # Mega Ball pool went from 25 to 24. Any data before this poisons the Markov models.
                        if draw_date >= datetime(2025, 4, 8):
                            numbers_str = parts[1].strip()
                            white_balls = [int(x.strip()) for x in numbers_str.split(',')]
                            
                            ball_str = parts[2].strip()
                            if 'Mega Ball:' in ball_str:
                                mega_ball = int(ball_str.split('Mega Ball:')[1].strip())
                            elif 'Money Ball:' in ball_str:
                                mega_ball = int(ball_str.split('Money Ball:')[1].strip())
                            else:
                                continue
                                
                            draws.append({
                                'date': draw_date,
                                'white_balls': white_balls,
                                'special_ball': mega_ball,
                                'multiplier': None # VA API usually doesn't include Megaplier in this string format
                            })

            except Exception:
                continue
        return draws

class VirginiaCash4LifeFetcher(LotteryFetcher):
    """
    JMc - [2026-03-16] - Fetches Cash4Life from the Virginia Lottery JSON API.
    """
    game_name = "VirginiaCash4Life"
    url = "https://www.valottery.com/api/v1/downloadall?gameId=1065"

    def fetch_data(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()

        draws = []
        lines = response.text.splitlines()

        for line in lines:
            line = line.strip()
            if not line or 'All information' in line or 'Therefore' in line or 'Results for' in line:
                continue

            try:
                # Format: "2/21/2026; 20,25,30,52,55; Cash Ball: 4"
                parts = line.split(';')
                if len(parts) >= 3:
                    date_str = parts[0].strip()
                    date_parts = date_str.split('/')

                    if len(date_parts) == 3:
                        month, day, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                        draw_date = datetime(year, month, day)

                        numbers_str = parts[1].strip()
                        white_balls = [int(x.strip()) for x in numbers_str.split(',')]

                        ball_str = parts[2].strip()
                        if 'Cash Ball:' in ball_str:
                            cash_ball = int(ball_str.split('Cash Ball:')[1].strip())
                        else:
                            continue

                        draws.append({
                            'date': draw_date,
                            'white_balls': white_balls,
                            'special_ball': cash_ball,
                            'multiplier': None
                        })
            except Exception:
                continue
        return draws

class VirginiaCash5Fetcher(LotteryFetcher):
    """
    JMc - [2026-03-16] - Fetches Cash 5 from the Virginia Lottery JSON API.
    This game has no special ball.
    """
    game_name = "VirginiaCash5"
    url = "https://www.valottery.com/api/v1/downloadall?gameId=1030"

    def fetch_data(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()

        draws = []
        lines = response.text.splitlines()

        for line in lines:
            line = line.strip()
            if not line or 'All information' in line or 'Therefore' in line or 'Results for' in line:
                continue

            try:
                # Format: "3/16/2026; 18,23,29,33,35"
                parts = line.split(';')
                if len(parts) >= 2:
                    date_str = parts[0].strip()
                    date_parts = date_str.split('/')

                    if len(date_parts) == 3:
                        month, day, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                        draw_date = datetime(year, month, day)

                        numbers_str = parts[1].strip()
                        white_balls = [int(x.strip()) for x in numbers_str.split(',')]

                        draws.append({
                            'date': draw_date,
                            'white_balls': white_balls,
                            'special_ball': None,
                            'multiplier': None
                        })
            except Exception:
                continue
        return draws

class BasePickFetcher(LotteryFetcher):
    """
    JMc - [2026-03-16] - Base class for Pick 3, Pick 4, and Pick 5 since they share a format.
    These are permutation games, so order matters. We override sync_to_db to preserve order.
    """
    
    def fetch_data(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()

        draws = []
        lines = response.text.splitlines()

        for line in lines:
            line = line.strip()
            if not line or 'All information' in line or 'Therefore' in line or 'Results for' in line:
                continue

            try:
                # Format: "3/16/2026; Day: 4,4,0; Fireball: 4; Night: 9,6,1; Fireball: 3"
                parts = line.split(';')
                if len(parts) >= 3:
                    date_str = parts[0].strip()
                    date_parts = date_str.split('/')

                    if len(date_parts) == 3:
                        month, day, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                        draw_date = datetime(year, month, day)

                        # Day draw
                        day_str = parts[1].strip()
                        if day_str.startswith('Day:'):
                            day_nums = [int(x.strip()) for x in day_str.replace('Day:', '').split(',')]
                            # Fireball for Day is in parts[2]
                            fb_day = None
                            if len(parts) > 2 and 'Fireball:' in parts[2]:
                                fb_day = int(parts[2].split('Fireball:')[1].strip())
                            
                            # JMc - [2026-03-16] - Append Day draw
                            # Hack: Use a temporary game_name modifier so the db constraint passes. 
                            # We'll set self.game_name appropriately in the subclass.
                            draws.append({
                                'date': draw_date,
                                'white_balls': day_nums,
                                'special_ball': fb_day,
                                'multiplier': None,
                                'game_name': f"{self.game_name} Day"
                            })

                        # Night draw (might be parts[3] and [4])
                        if len(parts) >= 4:
                            night_str = parts[3].strip()
                            if night_str.startswith('Night:'):
                                night_nums = [int(x.strip()) for x in night_str.replace('Night:', '').split(',')]
                                fb_night = None
                                if len(parts) > 4 and 'Fireball:' in parts[4]:
                                    fb_night = int(parts[4].split('Fireball:')[1].strip())
                                
                                draws.append({
                                    'date': draw_date,
                                    'white_balls': night_nums,
                                    'special_ball': fb_night,
                                    'multiplier': None,
                                    'game_name': f"{self.game_name} Night"
                                })
            except Exception:
                continue
        return draws

    def sync_to_db(self, db: Session):
        """
        JMc - [2026-03-16] - Override sync_to_db to handle dynamic game_names from fetch_data.
        Crucially, we DO NOT sort the white balls here, because for Pick games, order matters.
        """
        try:
            raw_draws = self.fetch_data()
        except Exception as e:
            logger.error(f"Failed to fetch data for {self.game_name}: {e}")
            return False
            
        new_records = 0
        for draw in raw_draws:
            actual_game_name = draw.get('game_name', self.game_name)
            
            exists = db.query(DrawRecord).filter(
                DrawRecord.state_code == "VA",
                DrawRecord.game_name == actual_game_name,
                DrawRecord.draw_date == draw['date'].date()
            ).first()
            
            if not exists:
                # JMc - [2026-03-16] - IMPORTANT: For Pick games, order matters! So we DO NOT sort here.
                # We need to store them in the exact order drawn for the Permutation Engine.
                white_str = ",".join(str(x) for x in draw['white_balls'])
                
                record = DrawRecord(
                    state_code="VA",
                    game_name=actual_game_name,
                    draw_date=draw['date'].date(),
                    white_balls=white_str,
                    special_ball=draw['special_ball'],
                    multiplier=draw.get('multiplier')
                )
                db.add(record)
                new_records += 1
                
        db.commit()
        logger.info(f"[{self.game_name}] Sync complete. Added {new_records} new draws.")
        return new_records

class VirginiaPick5Fetcher(BasePickFetcher):
    """
    JMc - [2026-03-16] - Fetches Pick 5 from the Virginia Lottery JSON API.
    """
    game_name = "VirginiaPick5"
    url = "https://www.valottery.com/api/v1/downloadall?gameId=1035"

class VirginiaPick4Fetcher(BasePickFetcher):
    """
    JMc - [2026-03-16] - Fetches Pick 4 from the Virginia Lottery JSON API.
    """
    game_name = "VirginiaPick4"
    url = "https://www.valottery.com/api/v1/downloadall?gameId=1040"

class VirginiaPick3Fetcher(BasePickFetcher):
    """
    JMc - [2026-03-16] - Fetches Pick 3 from the Virginia Lottery JSON API.
    """
    game_name = "VirginiaPick3"
    url = "https://www.valottery.com/api/v1/downloadall?gameId=1050"


class TexasCashFiveFetcher(LotteryFetcher):
    """
    JMc - [2026-03-18] - Fetches Cash Five from Texas Lottery CSV.
    """
    game_name = "TexasCashFive"
    state_code = "TX"
    url = "https://www.texaslottery.com/export/sites/lottery/Games/Cash_Five/Winning_Numbers/cashfive.csv"

    def fetch_data(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()

        draws = []
        lines = response.text.splitlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('Cash Five,Month'):
                continue

            try:
                # Format: Cash Five,10,13,1995,26,1,22,23,35
                parts = line.split(',')
                if len(parts) >= 9:
                    month, day, year = int(parts[1]), int(parts[2]), int(parts[3])
                    draw_date = datetime(year, month, day)
                    
                    # JMc - [2026-03-18] - The Texas Cash Five matrix changed to 5/35 on Sept 23, 2018.
                    # We strictly drop any data before this date to prevent poisoning the predictive models
                    # with legacy bounds that triggered combinatorial engines.
                    if draw_date >= datetime(2018, 9, 23):
                        white_balls = [int(x) for x in parts[4:9]]
    
                        draws.append({
                            'date': draw_date,
                            'white_balls': white_balls,
                            'special_ball': None,
                            'multiplier': None,
                            'game_name': self.game_name
                        })
            except Exception:
                continue
        return draws

class BaseTexasPickFetcher(LotteryFetcher):
    """
    JMc - [2026-03-18] - Base class for Texas Pick 3 and Daily 4.
    Fetches from 4 separate CSV endpoints and combines them.
    """
    state_code = "TX"
    
    def fetch_data(self):
        draws = []
        for period, url in self.urls.items():
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                lines = response.text.splitlines()

                for line in lines:
                    line = line.strip()
                    if not line or 'Month' in line:
                        continue

                    try:
                        # Format: Pick 3 Night,3,17,2026,7,3,3,,5
                        # or Pick 3 Night,10,25,1993,3,2,9,,
                        parts = line.split(',')
                        if len(parts) >= 4 + self.num_balls:
                            month, day, year = int(parts[1]), int(parts[2]), int(parts[3])
                            draw_date = datetime(year, month, day)
                            
                            white_balls = [int(parts[4+i]) for i in range(self.num_balls)]
                            
                            # Check for Fireball if columns exist
                            fireball = None
                            if len(parts) > 4 + self.num_balls + 1 and parts[-1].strip():
                                fireball = int(parts[-1].strip())
                            
                            draws.append({
                                'date': draw_date,
                                'white_balls': white_balls,
                                'special_ball': fireball,
                                'multiplier': None,
                                'game_name': f"{self.game_name} {period}"
                            })
                    except Exception:
                        continue
            except Exception as e:
                logger.error(f"Failed to fetch {self.game_name} {period}: {e}")
        return draws
        
    def sync_to_db(self, db: Session):
        """
        JMc - [2026-03-18] - Override sync_to_db for Texas Pick games (order matters).
        Includes batch commits to prevent OOM kills on 100k+ row CSVs.
        """
        try:
            raw_draws = self.fetch_data()
        except Exception as e:
            logger.error(f"Failed to fetch data for {self.game_name}: {e}")
            return False
            
        new_records = 0
        batch_size = 2000
        
        for draw in raw_draws:
            actual_game_name = draw.get('game_name', self.game_name)
            
            exists = db.query(DrawRecord).filter(
                DrawRecord.state_code == "TX",
                DrawRecord.game_name == actual_game_name,
                DrawRecord.draw_date == draw['date'].date()
            ).first()
            
            if not exists:
                white_str = ",".join(str(x) for x in draw['white_balls'])
                record = DrawRecord(
                    state_code="TX",
                    game_name=actual_game_name,
                    draw_date=draw['date'].date(),
                    white_balls=white_str,
                    special_ball=draw['special_ball'],
                    multiplier=draw.get('multiplier')
                )
                db.add(record)
                new_records += 1
                
                if new_records % batch_size == 0:
                    db.commit()
                
        db.commit()
        logger.info(f"[{self.game_name}] Sync complete. Added {new_records} new draws.")
        return new_records

class TexasPick3Fetcher(BaseTexasPickFetcher):
    """
    JMc - [2026-03-18] - Fetches Texas Pick 3.
    """
    game_name = "TexasPick3"
    num_balls = 3
    urls = {
        "Morning": "https://www.texaslottery.com/export/sites/lottery/Games/Pick_3/Winning_Numbers/pick3morning.csv",
        "Day": "https://www.texaslottery.com/export/sites/lottery/Games/Pick_3/Winning_Numbers/pick3day.csv",
        "Evening": "https://www.texaslottery.com/export/sites/lottery/Games/Pick_3/Winning_Numbers/pick3evening.csv",
        "Night": "https://www.texaslottery.com/export/sites/lottery/Games/Pick_3/Winning_Numbers/pick3night.csv"
    }

class TexasDaily4Fetcher(BaseTexasPickFetcher):
    """
    JMc - [2026-03-18] - Fetches Texas Daily 4.
    """
    game_name = "TexasDaily4"
    num_balls = 4
    urls = {
        "Morning": "https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/Winning_Numbers/daily4morning.csv",
        "Day": "https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/Winning_Numbers/daily4day.csv",
        "Evening": "https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/Winning_Numbers/daily4evening.csv",
        "Night": "https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/Winning_Numbers/daily4night.csv"
    }

class NewYorkLottoFetcher(LotteryFetcher):
    """
    JMc - [2026-03-18] - Fetches NY Lotto from Socrata (6/59).
    """
    game_name = "NewYorkLotto"
    state_code = "NY"
    url = "https://data.ny.gov/resource/6nbc-h7bj.json"

    def fetch_data(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        draws = []
        for item in data:
            try:
                # Socrata date format: "2026-03-14T00:00:00.000"
                dt = datetime.fromisoformat(item['draw_date'].split('T')[0])
                # Numbers are space separated: "15 30 35 43 46 56"
                white_balls = [int(x) for x in item['winning_numbers'].split()]
                bonus = int(item['bonus'])
                
                draws.append({
                    'date': dt,
                    'white_balls': white_balls,
                    'special_ball': bonus,
                    'multiplier': None
                })
            except Exception:
                continue
        return draws

class NewYorkTake5Fetcher(LotteryFetcher):
    """
    JMc - [2026-03-18] - Fetches NY Take 5 from Socrata (5/39).
    Splits Midday and Evening into separate game entries.
    """
    game_name = "NewYorkTake5"
    state_code = "NY"
    url = "https://data.ny.gov/resource/dg63-4siq.json"

    def fetch_data(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        draws = []
        for item in data:
            try:
                dt = datetime.fromisoformat(item['draw_date'].split('T')[0])
                
                if 'midday_winning_numbers' in item:
                    mid_balls = [int(x) for x in item['midday_winning_numbers'].split()]
                    draws.append({
                        'date': dt,
                        'white_balls': mid_balls,
                        'special_ball': None,
                        'multiplier': None,
                        'game_name': f"{self.game_name} Midday"
                    })
                    
                if 'evening_winning_numbers' in item:
                    eve_balls = [int(x) for x in item['evening_winning_numbers'].split()]
                    draws.append({
                        'date': dt,
                        'white_balls': eve_balls,
                        'special_ball': None,
                        'multiplier': None,
                        'game_name': f"{self.game_name} Evening"
                    })
            except Exception:
                continue
        return draws

    def sync_to_db(self, db: Session):
        try:
            raw_draws = self.fetch_data()
        except Exception as e:
            logger.error(f"Failed to fetch data for {self.game_name}: {e}")
            return False
            
        new_records = 0
        for draw in raw_draws:
            actual_game_name = draw.get('game_name', self.game_name)
            exists = db.query(DrawRecord).filter(
                DrawRecord.state_code == self.state_code,
                DrawRecord.game_name == actual_game_name,
                DrawRecord.draw_date == draw['date'].date()
            ).first()
            
            if not exists:
                sorted_whites = sorted(draw['white_balls'])
                white_str = ",".join(str(x) for x in sorted_whites)
                record = DrawRecord(
                    state_code=self.state_code,
                    game_name=actual_game_name,
                    draw_date=draw['date'].date(),
                    white_balls=white_str,
                    special_ball=draw['special_ball'],
                    multiplier=draw.get('multiplier')
                )
                db.add(record)
                new_records += 1
        db.commit()
        return new_records

class NewYorkPickFetcher(LotteryFetcher):
    """
    JMc - [2026-03-18] - Base for NY Numbers (Pick 3) and Win 4.
    """
    state_code = "NY"
    url = "https://data.ny.gov/resource/hsys-3def.json"

    def fetch_data(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        draws = []
        for item in data:
            try:
                dt = datetime.fromisoformat(item['draw_date'].split('T')[0])
                
                # Pick 3 (Numbers)
                if self.mode == "numbers":
                    if 'midday_daily' in item:
                        balls = [int(d) for d in item['midday_daily']]
                        draws.append({
                            'date': dt,
                            'white_balls': balls,
                            'special_ball': None,
                            'multiplier': None,
                            'game_name': f"{self.game_name} Midday"
                        })
                    if 'evening_daily' in item:
                        balls = [int(d) for d in item['evening_daily']]
                        draws.append({
                            'date': dt,
                            'white_balls': balls,
                            'special_ball': None,
                            'multiplier': None,
                            'game_name': f"{self.game_name} Evening"
                        })
                
                # Pick 4 (Win 4)
                elif self.mode == "win4":
                    if 'midday_win_4' in item:
                        balls = [int(d) for d in item['midday_win_4']]
                        draws.append({
                            'date': dt,
                            'white_balls': balls,
                            'special_ball': None,
                            'multiplier': None,
                            'game_name': f"{self.game_name} Midday"
                        })
                    if 'evening_win_4' in item:
                        balls = [int(d) for d in item['evening_win_4']]
                        draws.append({
                            'date': dt,
                            'white_balls': balls,
                            'special_ball': None,
                            'multiplier': None,
                            'game_name': f"{self.game_name} Evening"
                        })
            except Exception:
                continue
        return draws

    def sync_to_db(self, db: Session):
        try:
            raw_draws = self.fetch_data()
        except Exception as e:
            logger.error(f"Failed to fetch data for {self.game_name}: {e}")
            return False
            
        new_records = 0
        for draw in raw_draws:
            actual_game_name = draw.get('game_name', self.game_name)
            exists = db.query(DrawRecord).filter(
                DrawRecord.state_code == self.state_code,
                DrawRecord.game_name == actual_game_name,
                DrawRecord.draw_date == draw['date'].date()
            ).first()
            
            if not exists:
                # Order matters for Pick games
                white_str = ",".join(str(x) for x in draw['white_balls'])
                record = DrawRecord(
                    state_code=self.state_code,
                    game_name=actual_game_name,
                    draw_date=draw['date'].date(),
                    white_balls=white_str,
                    special_ball=draw['special_ball'],
                    multiplier=draw.get('multiplier')
                )
                db.add(record)
                new_records += 1
        db.commit()
        return new_records

class NewYorkPick3Fetcher(NewYorkPickFetcher):
    game_name = "NewYorkNumbers"
    mode = "numbers"

class NewYorkPick4Fetcher(NewYorkPickFetcher):
    game_name = "NewYorkWin4"
    mode = "win4"
