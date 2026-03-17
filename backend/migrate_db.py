import sqlite3

def migrate():
    print("Connecting to database...")
    conn = sqlite3.connect('data/lottery.db')
    cursor = conn.cursor()

    print("Migrating historical_draws...")
    cursor.execute("""
        CREATE TABLE historical_draws_new (
            id INTEGER NOT NULL PRIMARY KEY,
            game_name VARCHAR NOT NULL,
            draw_date DATE NOT NULL,
            white_balls VARCHAR NOT NULL,
            special_ball INTEGER,
            multiplier INTEGER,
            CONSTRAINT uq_game_date UNIQUE (game_name, draw_date)
        )
    """)
    cursor.execute("""
        INSERT INTO historical_draws_new (id, game_name, draw_date, white_balls, special_ball, multiplier)
        SELECT id, game_name, draw_date, white_balls, special_ball, multiplier FROM historical_draws
    """)
    cursor.execute("DROP TABLE historical_draws")
    cursor.execute("ALTER TABLE historical_draws_new RENAME TO historical_draws")
    cursor.execute("CREATE INDEX ix_historical_draws_game_name ON historical_draws (game_name)")
    cursor.execute("CREATE INDEX ix_historical_draws_id ON historical_draws (id)")

    print("Migrating saved_ticket_batches...")
    cursor.execute("""
        CREATE TABLE saved_ticket_batches_new (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER NOT NULL,
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
    cursor.execute("DROP TABLE saved_ticket_batches")
    cursor.execute("ALTER TABLE saved_ticket_batches_new RENAME TO saved_ticket_batches")
    cursor.execute("CREATE INDEX ix_saved_ticket_batches_id ON saved_ticket_batches (id)")

    print("Migrating saved_tickets...")
    cursor.execute("""
        CREATE TABLE saved_tickets_new (
            id INTEGER NOT NULL PRIMARY KEY,
            batch_id INTEGER NOT NULL,
            ticket_white_balls VARCHAR NOT NULL,
            ticket_special_ball INTEGER,
            FOREIGN KEY(batch_id) REFERENCES saved_ticket_batches (id)
        )
    """)
    cursor.execute("""
        INSERT INTO saved_tickets_new (id, batch_id, ticket_white_balls, ticket_special_ball)
        SELECT id, batch_id, ticket_white_balls, ticket_special_ball FROM saved_tickets
    """)
    cursor.execute("DROP TABLE saved_tickets")
    cursor.execute("ALTER TABLE saved_tickets_new RENAME TO saved_tickets")
    cursor.execute("CREATE INDEX ix_saved_tickets_id ON saved_tickets (id)")

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()