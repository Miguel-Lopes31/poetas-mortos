from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Book(db.Model):
    """Model for books in the library."""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    pages = db.Column(db.Integer)
    cover_url = db.Column(db.String(500))
    
    # Status: 'read', 'reading', 'want_to_read'
    status = db.Column(db.String(20), default='want_to_read')
    queue_order = db.Column(db.Integer, default=0)
    # Priority: 'high', 'normal', 'low'
    priority = db.Column(db.String(20), default='normal')
    
    # Purchase info
    purchase_place = db.Column(db.String(100))
    purchase_price = db.Column(db.Float)
    purchase_date = db.Column(db.Date)
    delivery_days = db.Column(db.Integer)
    
    # Reading info
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    current_page = db.Column(db.Integer, default=0)  # Pages already read
    rating = db.Column(db.Integer)  # 1-5
    observations = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    diary_entries = db.relationship('ReadingDiary', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert book to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'genre': self.genre,
            'pages': self.pages,
            'cover_url': self.cover_url,
            'status': self.status,
            'queue_order': self.queue_order,
            'priority': self.priority,
            'purchase_place': self.purchase_place,
            'purchase_price': self.purchase_price,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'delivery_days': self.delivery_days,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'current_page': self.current_page or 0,
            'rating': self.rating,
            'observations': self.observations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'pages_read': self.get_pages_read()
        }
    
    def get_pages_read(self):
        """Calculate total pages read from diary entries."""
        from sqlalchemy import func
        result = db.session.query(func.sum(ReadingDiary.pages_read)).filter(
            ReadingDiary.book_id == self.id
        ).scalar()
        return result or 0


class ReadingDiary(db.Model):
    """Model for daily reading entries."""
    __tablename__ = 'reading_diary'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    pages_read = db.Column(db.Integer, default=0)
    reading_time = db.Column(db.Integer)  # Minutes
    did_read = db.Column(db.Boolean, default=True)
    skip_reason = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert diary entry to dictionary."""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'date': self.date.isoformat() if self.date else None,
            'pages_read': self.pages_read,
            'reading_time': self.reading_time,
            'did_read': self.did_read,
            'skip_reason': self.skip_reason,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Note(db.Model):
    """Model for book notes and highlights."""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    # Type: 'quote', 'thought', 'reflection'
    type = db.Column(db.String(20), default='thought')
    content = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert note to dictionary."""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'type': self.type,
            'content': self.content,
            'page_number': self.page_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DailyQuote(db.Model):
    """Model for literary quotes shown on dashboard."""
    __tablename__ = 'daily_quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    quote = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    book = db.Column(db.String(200))
    
    def to_dict(self):
        """Convert quote to dictionary."""
        return {
            'id': self.id,
            'quote': self.quote,
            'author': self.author,
            'book': self.book
        }


def init_quotes(db):
    """Initialize database with some literary quotes."""
    quotes = [
        {
            'quote': 'Um leitor vive mil vidas antes de morrer. O homem que nunca lê vive apenas uma.',
            'author': 'George R.R. Martin',
            'book': 'A Dança dos Dragões'
        },
        {
            'quote': 'Os livros são os mais silenciosos e constantes amigos; são os conselheiros mais acessíveis e os professores mais pacientes.',
            'author': 'Charles W. Eliot',
            'book': None
        },
        {
            'quote': 'Não existe nenhum problema que a leitura não resolva.',
            'author': 'Montesquieu',
            'book': None
        },
        {
            'quote': 'A leitura é uma fonte inesgotável de prazer, mas por incrível que pareça, a quase totalidade, não sente sede.',
            'author': 'Carlos Drummond de Andrade',
            'book': None
        },
        {
            'quote': 'Livros não mudam o mundo, quem muda o mundo são as pessoas. Os livros só mudam as pessoas.',
            'author': 'Mário Quintana',
            'book': None
        },
        {
            'quote': 'A literatura é a imortalidade da fala.',
            'author': 'August Wilhelm Schlegel',
            'book': None
        },
        {
            'quote': 'Ler é sonhar pela mão de outrem.',
            'author': 'Fernando Pessoa',
            'book': None
        },
        {
            'quote': 'Há crimes piores que queimar livros. Um deles é não os ler.',
            'author': 'Ray Bradbury',
            'book': 'Fahrenheit 451'
        },
        {
            'quote': 'Quando você vende um homem um livro, você não vende apenas doze onças de papel e tinta e cola - você vende uma vida inteira.',
            'author': 'Christopher Morley',
            'book': None
        },
        {
            'quote': 'O paraíso deve ser uma espécie de biblioteca.',
            'author': 'Jorge Luis Borges',
            'book': None
        }
    ]
    
    # Only add quotes if table is empty
    if DailyQuote.query.count() == 0:
        for q in quotes:
            quote = DailyQuote(**q)
            db.session.add(quote)
        db.session.commit()
