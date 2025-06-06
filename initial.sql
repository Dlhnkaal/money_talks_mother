CREATE TABLE giveaways (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    price INTEGER NOT NULL,
    max_participants INTEGER,
    end_datetime TIMESTAMP NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE participants (
    id SERIAL PRIMARY KEY,
    giveaway_id INTEGER REFERENCES giveaways(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    username TEXT,
    is_paid BOOLEAN DEFAULT FALSE,
    payment_id TEXT,
    joined_at TIMESTAMP DEFAULT now()
);

CREATE TABLE winners (
    id SERIAL PRIMARY KEY,
    giveaway_id INTEGER REFERENCES giveaways(id) ON DELETE CASCADE,
    winner_user_id BIGINT NOT NULL,
    username TEXT,
    won_at TIMESTAMP DEFAULT now()
);
