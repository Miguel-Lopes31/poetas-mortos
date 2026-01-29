-- =============================================
-- BIBLIOTECA PESSOAL - Script de Criação do Banco de Dados
-- Execute este script no SQL Editor do Supabase
-- =============================================

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Livros
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    publisher VARCHAR(100),
    genre VARCHAR(50),
    pages INTEGER,
    cover_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'want_to_read',
    queue_order INTEGER DEFAULT 0,
    priority VARCHAR(20) DEFAULT 'normal',
    purchase_place VARCHAR(100),
    purchase_price FLOAT,
    purchase_date DATE,
    delivery_days INTEGER,
    start_date DATE,
    end_date DATE,
    current_page INTEGER DEFAULT 0,
    rating INTEGER,
    observations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Diário de Leitura
CREATE TABLE IF NOT EXISTS reading_diary (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    pages_read INTEGER DEFAULT 0,
    reading_time INTEGER,
    did_read BOOLEAN DEFAULT TRUE,
    skip_reason VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Notas
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    type VARCHAR(20) DEFAULT 'thought',
    content TEXT NOT NULL,
    page_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Citações Diárias
CREATE TABLE IF NOT EXISTS daily_quotes (
    id SERIAL PRIMARY KEY,
    quote TEXT NOT NULL,
    author VARCHAR(100),
    book VARCHAR(200)
);

-- =============================================
-- Índices para melhor performance
-- =============================================

CREATE INDEX IF NOT EXISTS idx_books_user_id ON books(user_id);
CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);
CREATE INDEX IF NOT EXISTS idx_reading_diary_user_id ON reading_diary(user_id);
CREATE INDEX IF NOT EXISTS idx_reading_diary_date ON reading_diary(date);
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
CREATE INDEX IF NOT EXISTS idx_notes_book_id ON notes(book_id);

-- =============================================
-- Inserir citações literárias
-- =============================================

INSERT INTO daily_quotes (quote, author, book) VALUES
('Um leitor vive mil vidas antes de morrer. O homem que nunca lê vive apenas uma.', 'George R.R. Martin', 'A Dança dos Dragões'),
('Os livros são os mais silenciosos e constantes amigos; são os conselheiros mais acessíveis e os professores mais pacientes.', 'Charles W. Eliot', NULL),
('Não existe nenhum problema que a leitura não resolva.', 'Montesquieu', NULL),
('A leitura é uma fonte inesgotável de prazer, mas por incrível que pareça, a quase totalidade, não sente sede.', 'Carlos Drummond de Andrade', NULL),
('Livros não mudam o mundo, quem muda o mundo são as pessoas. Os livros só mudam as pessoas.', 'Mário Quintana', NULL),
('A literatura é a imortalidade da fala.', 'August Wilhelm Schlegel', NULL),
('Ler é sonhar pela mão de outrem.', 'Fernando Pessoa', NULL),
('Há crimes piores que queimar livros. Um deles é não os ler.', 'Ray Bradbury', 'Fahrenheit 451'),
('Quando você vende um homem um livro, você não vende apenas doze onças de papel e tinta e cola - você vende uma vida inteira.', 'Christopher Morley', NULL),
('O paraíso deve ser uma espécie de biblioteca.', 'Jorge Luis Borges', NULL)
ON CONFLICT DO NOTHING;
