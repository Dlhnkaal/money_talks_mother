-- Создаем таблицу розыгрышей
CREATE TABLE IF NOT EXISTS giveaways (
    giveaway_id SERIAL PRIMARY KEY,
    message_id BIGINT,
    participants_count INT DEFAULT 0
);

-- Создаем таблицу участников
CREATE TABLE IF NOT EXISTS participants (
    user_id BIGINT NOT NULL,
    giveaway_id INT NOT NULL,
    paid BOOLEAN DEFAULT FALSE,
    nickname TEXT,
    PRIMARY KEY (user_id, giveaway_id),
    CONSTRAINT fk_giveaway
        FOREIGN KEY(giveaway_id) 
        REFERENCES giveaways(giveaway_id)
        ON DELETE CASCADE
);
