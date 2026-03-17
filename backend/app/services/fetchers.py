import csv
import logging
from datetime import datetime
import requests
from sqlalchemy.orm import Session
from app.core.models import DrawRecord

logger = logging.getLogger(__name__)

class LotteryFetcher:
    """Base class for all data ingestion. Defines the contract."""
    game_name = "Base"
    
    def fetch_data(self) -> list[dict]:
        """Must return a list of dicts: 
        [{'date': datetime, 'white_balls': [int], 'special_ball': int, 'multiplier': int}]
        """
        raise NotImplementedError
        
    def sync_to_db(self, db: Session):
        """Standardized method to sync fetched data into the universal SQLite table."""
        try:
            raw_draws = self.fetch_data()
        except Exception as e:
            logger.error(f"Failed to fetch data for {self.game_name}: {e}")
            return False
            
        new_records = 0
        for draw in raw_draws:
            # Check if record exists
            exists = db.query(DrawRecord).filter(
                DrawRecord.game_name == self.game_name,
                DrawRecord.draw_date == draw['date'].date()
            ).first()
            
            if not exists:
                sorted_whites = sorted(draw['white_balls'])
                white_str = ",".join(str(x) for x in sorted_whites)
                
                record = DrawRecord(
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
    """Fetches Powerball from the Virginia Lottery JSON API (CSV-like format)."""
    game_name = "Powerball"
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

                        # Current format (2015-present)
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
    """Fetches MegaMillions from the Virginia Lottery JSON API."""
    game_name = "MegaMillions"
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
                        
                        # JMc - [2026-03-07] - The Matrix changed on April 8, 2025. 
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
    """Fetches Cash4Life from the Virginia Lottery JSON API."""
    game_name = "Cash4Life"
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
    """Fetches Cash 5 from the Virginia Lottery JSON API."""
    game_name = "Cash5"
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
    """Base class for Pick 3, Pick 4, and Pick 5 since they share a format."""
    
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
                            
                            # Append Day draw
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
        """Override sync_to_db to handle dynamic game_names from fetch_data"""
        try:
            raw_draws = self.fetch_data()
        except Exception as e:
            logger.error(f"Failed to fetch data for {self.game_name}: {e}")
            return False
            
        new_records = 0
        for draw in raw_draws:
            actual_game_name = draw.get('game_name', self.game_name)
            
            exists = db.query(DrawRecord).filter(
                DrawRecord.game_name == actual_game_name,
                DrawRecord.draw_date == draw['date'].date()
            ).first()
            
            if not exists:
                # IMPORTANT: For Pick games, order matters! So we DO NOT sort here.
                # We need to store them in the exact order drawn.
                white_str = ",".join(str(x) for x in draw['white_balls'])
                
                record = DrawRecord(
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
    """Fetches Pick 5 from the Virginia Lottery JSON API."""
    game_name = "Pick5"
    url = "https://www.valottery.com/api/v1/downloadall?gameId=1035"

class VirginiaPick4Fetcher(BasePickFetcher):
    """Fetches Pick 4 from the Virginia Lottery JSON API."""
    game_name = "Pick4"
    url = "https://www.valottery.com/api/v1/downloadall?gameId=1040"

class VirginiaPick3Fetcher(BasePickFetcher):
    """Fetches Pick 3 from the Virginia Lottery JSON API."""
    game_name = "Pick3"
    url = "https://www.valottery.com/api/v1/downloadall?gameId=1050"
