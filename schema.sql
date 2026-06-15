-- 1. Create Enums for strict type checking
CREATE TYPE user_role AS ENUM ('staff', 'owner');
CREATE TYPE transaction_type AS ENUM ('sell', 'undo', 'damage', 'batch_update', 'restock');
CREATE TYPE transaction_status AS ENUM ('completed', 'reversed');

-- 2. Branches Table
CREATE TABLE branches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    location TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- 3. Users Table (Maps Telegram ID to Bot Roles)
CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    role user_role NOT NULL DEFAULT 'staff',
    branch_id UUID REFERENCES branches(id),
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- 4. Items Master Table
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    barcode VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    low_stock_threshold INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- 5. Inventory Table (Many-to-Many: Items x Branches)
CREATE TABLE inventory (
    item_id UUID REFERENCES items(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    PRIMARY KEY (item_id, branch_id)
);

-- 6. Transactions Table (For checkout, undo, restock, etc.)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID REFERENCES items(id),
    branch_id UUID REFERENCES branches(id),
    user_id BIGINT REFERENCES users(telegram_id),
    type transaction_type NOT NULL,
    quantity INTEGER NOT NULL,
    status transaction_status DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- 7. Defect Logs (Specifically for damage reporting with photos)
CREATE TABLE defect_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID REFERENCES items(id),
    branch_id UUID REFERENCES branches(id),
    user_id BIGINT REFERENCES users(telegram_id),
    quantity INTEGER NOT NULL,
    photo_file_id TEXT NOT NULL, -- Stores Telegram's file_id for the uploaded photo
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);
