import sqlite3

def migrate():
    print("Connecting to database...")
    conn = sqlite3.connect('data/lottery.db')
    cursor = conn.cursor()

    print("Migrating historical_draws...")
    cursor.execute("""
        CREATE TABLE historical_draws_new (
            id INTEGER NOT NULL PRIMARY KEY,
            state_code VARCHAR NOT NULL DEFAULT 'VA',
            game_name VARCHAR NOT NULL,
            draw_date DATE NOT NULL,
            white_balls VARCHAR NOT NULL,
            special_ball INTEGER,
            multiplier INTEGER,
            CONSTRAINT uq_state_game_date UNIQUE (state_code, game_name, draw_date)
        )
    """)
    cursor.execute("""
        INSERT INTO historical_draws_new (id, game_name, draw_date, white_balls, special_ball, multiplier)
        SELECT id, game_name, draw_date, white_balls, special_ball, multiplier FROM historical_draws
    """)
    # Update NAT games
    cursor.execute("UPDATE historical_draws_new SET state_code = 'NAT' WHERE game_name IN ('Powerball', 'MegaMillions')")
    
    cursor.execute("DROP TABLE historical_draws")
    cursor.execute("ALTER TABLE historical_draws_new RENAME TO historical_draws")
    cursor.execute("CREATE INDEX ix_historical_draws_game_name ON historical_draws (game_name)")
    cursor.execute("CREATE INDEX ix_historical_draws_state_code ON historical_draws (state_code)")
    cursor.execute("CREATE INDEX ix_historical_draws_id ON historical_draws (id)")

    print("Migrating saved_ticket_batches...")
    cursor.execute("""
        CREATE TABLE saved_ticket_batches_new (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            state_code VARCHAR NOT NULL DEFAULT 'VA',
            game_name VARCHAR NOT NULL,
            pool_white_balls VARCHAR NOT NULL,
            pool_special_balls VARCHAR,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users (id)
        )
    """)
    cursor.execute("""
        INSERT INTO saved_ticket_batches_new (id, user_id, game_name, pool_white_balls, pool_special_balls, created_at)
        SELECT id, user_id, game_name, pool_white_balls, pool_special_balls, created_at FROM saved_ticket_batches
    """)
    cursor.execute("UPDATE saved_ticket_batches_new SET state_code = 'NAT' WHERE game_name IN ('Powerball', 'MegaMillions')")

    cursor.execute("DROP TABLE saved_ticket_batches")
    cursor.execute("ALTER TABLE saved_ticket_batches_new RENAME TO saved_ticket_batches")
    cursor.execute("CREATE INDEX ix_saved_ticket_batches_state_code ON saved_ticket_batches (state_code)")
    cursor.execute("CREATE INDEX ix_saved_ticket_batches_id ON saved_ticket_batches (id)")

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()