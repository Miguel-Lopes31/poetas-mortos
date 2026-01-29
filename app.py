import os
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy import func
from config import Config
from models import db, Book, ReadingDiary, Note, DailyQuote, init_quotes
import random

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
with app.app_context():
    db.create_all()
    init_quotes(db)


# ============================================
# Page Routes
# ============================================

@app.route('/')
def index():
    """Dashboard page."""
    return render_template('index.html')


@app.route('/biblioteca')
def library():
    """Library page."""
    return render_template('library.html')


@app.route('/livro')
@app.route('/livro/<int:book_id>')
def book_page(book_id=None):
    """Book detail/edit page."""
    return render_template('book.html', book_id=book_id)


@app.route('/fila')
def queue():
    """Reading queue page."""
    return render_template('queue.html')


@app.route('/diario')
def diary():
    """Reading diary page."""
    return render_template('diary.html')


@app.route('/estatisticas')
def stats():
    """Statistics page."""
    return render_template('stats.html')


@app.route('/notas')
def notes_page():
    """Notes page."""
    return render_template('notes.html')


# ============================================
# API: Books
# ============================================

@app.route('/api/books', methods=['GET'])
def get_books():
    """Get all books with optional filters."""
    status = request.args.get('status')
    author = request.args.get('author')
    publisher = request.args.get('publisher')
    genre = request.args.get('genre')
    year = request.args.get('year')
    search = request.args.get('search')
    
    query = Book.query
    
    if status:
        query = query.filter(Book.status == status)
    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))
    if publisher:
        query = query.filter(Book.publisher.ilike(f'%{publisher}%'))
    if genre:
        query = query.filter(Book.genre.ilike(f'%{genre}%'))
    if year:
        query = query.filter(db.extract('year', Book.purchase_date) == int(year))
    if search:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%')
            )
        )
    
    books = query.order_by(Book.created_at.desc()).all()
    return jsonify([book.to_dict() for book in books])


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a single book by ID."""
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())


@app.route('/api/books', methods=['POST'])
def create_book():
    """Create a new book."""
    data = request.get_json()
    
    book = Book(
        title=data.get('title'),
        author=data.get('author'),
        publisher=data.get('publisher'),
        genre=data.get('genre'),
        pages=data.get('pages'),
        cover_url=data.get('cover_url'),
        status=data.get('status', 'want_to_read'),
        priority=data.get('priority', 'normal'),
        purchase_place=data.get('purchase_place'),
        purchase_price=data.get('purchase_price'),
        purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data.get('purchase_date') else None,
        delivery_days=data.get('delivery_days'),
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
        current_page=data.get('current_page', 0),
        rating=data.get('rating'),
        observations=data.get('observations')
    )
    
    # Set queue order for new books
    max_order = db.session.query(func.max(Book.queue_order)).scalar() or 0
    book.queue_order = max_order + 1
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify(book.to_dict()), 201


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update a book."""
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    # Update fields if provided
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'publisher' in data:
        book.publisher = data['publisher']
    if 'genre' in data:
        book.genre = data['genre']
    if 'pages' in data:
        book.pages = data['pages']
    if 'cover_url' in data:
        book.cover_url = data['cover_url']
    if 'status' in data:
        book.status = data['status']
    if 'priority' in data:
        book.priority = data['priority']
    if 'purchase_place' in data:
        book.purchase_place = data['purchase_place']
    if 'purchase_price' in data:
        book.purchase_price = data['purchase_price']
    if 'purchase_date' in data:
        book.purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data['purchase_date'] else None
    if 'delivery_days' in data:
        book.delivery_days = data['delivery_days']
    if 'start_date' in data:
        book.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data['start_date'] else None
    if 'end_date' in data:
        book.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data['end_date'] else None
    if 'current_page' in data:
        book.current_page = data['current_page']
    if 'rating' in data:
        book.rating = data['rating']
    if 'observations' in data:
        book.observations = data['observations']
    
    db.session.commit()
    return jsonify(book.to_dict())


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book."""
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return '', 204


@app.route('/api/books/current', methods=['GET'])
def get_current_book():
    """Get the currently reading book."""
    book = Book.query.filter_by(status='reading').order_by(Book.start_date.desc()).first()
    if book:
        return jsonify(book.to_dict())
    return jsonify(None)


# ============================================
# API: Reading Queue
# ============================================

@app.route('/api/queue', methods=['GET'])
def get_queue():
    """Get reading queue (want_to_read books ordered)."""
    books = Book.query.filter_by(status='want_to_read').order_by(Book.queue_order).all()
    return jsonify([book.to_dict() for book in books])


@app.route('/api/queue/reorder', methods=['PUT'])
def reorder_queue():
    """Reorder the reading queue."""
    data = request.get_json()
    order = data.get('order', [])  # List of book IDs in new order
    
    for index, book_id in enumerate(order):
        book = Book.query.get(book_id)
        if book:
            book.queue_order = index
    
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/books/<int:book_id>/priority', methods=['PUT'])
def update_priority(book_id):
    """Update book priority."""
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    book.priority = data.get('priority', 'normal')
    db.session.commit()
    return jsonify(book.to_dict())


# ============================================
# API: Reading Diary
# ============================================

@app.route('/api/diary', methods=['GET'])
def get_diary():
    """Get all diary entries."""
    month = request.args.get('month')
    year = request.args.get('year')
    
    query = ReadingDiary.query
    
    if month and year:
        query = query.filter(
            db.extract('month', ReadingDiary.date) == int(month),
            db.extract('year', ReadingDiary.date) == int(year)
        )
    
    entries = query.order_by(ReadingDiary.date.desc()).all()
    return jsonify([entry.to_dict() for entry in entries])


@app.route('/api/diary/<string:date_str>', methods=['GET'])
def get_diary_entry(date_str):
    """Get diary entry for a specific date."""
    try:
        entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    entry = ReadingDiary.query.filter_by(date=entry_date).first()
    if entry:
        return jsonify(entry.to_dict())
    return jsonify(None)


@app.route('/api/diary', methods=['POST'])
def create_diary_entry():
    """Create a new diary entry."""
    data = request.get_json()
    
    entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    
    # Check if entry already exists for this date
    existing = ReadingDiary.query.filter_by(date=entry_date).first()
    if existing:
        return jsonify({'error': 'Entry already exists for this date'}), 400
    
    entry = ReadingDiary(
        book_id=data.get('book_id'),
        date=entry_date,
        pages_read=data.get('pages_read', 0),
        reading_time=data.get('reading_time'),
        did_read=data.get('did_read', True),
        skip_reason=data.get('skip_reason'),
        notes=data.get('notes')
    )
    
    db.session.add(entry)
    db.session.commit()
    
    return jsonify(entry.to_dict()), 201


@app.route('/api/diary/<int:entry_id>', methods=['PUT'])
def update_diary_entry(entry_id):
    """Update a diary entry."""
    entry = ReadingDiary.query.get_or_404(entry_id)
    data = request.get_json()
    
    if 'book_id' in data:
        entry.book_id = data['book_id']
    if 'pages_read' in data:
        entry.pages_read = data['pages_read']
    if 'reading_time' in data:
        entry.reading_time = data['reading_time']
    if 'did_read' in data:
        entry.did_read = data['did_read']
    if 'skip_reason' in data:
        entry.skip_reason = data['skip_reason']
    if 'notes' in data:
        entry.notes = data['notes']
    
    db.session.commit()
    return jsonify(entry.to_dict())


@app.route('/api/diary/<int:entry_id>', methods=['DELETE'])
def delete_diary_entry(entry_id):
    """Delete a diary entry."""
    entry = ReadingDiary.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return '', 204


# ============================================
# API: Statistics
# ============================================

@app.route('/api/stats/overview', methods=['GET'])
def get_stats_overview():
    """Get dashboard overview statistics."""
    total_books = Book.query.count()
    books_read = Book.query.filter_by(status='read').count()
    books_reading = Book.query.filter_by(status='reading').count()
    books_want = Book.query.filter_by(status='want_to_read').count()
    
    # Pages read today
    today = date.today()
    today_entry = ReadingDiary.query.filter_by(date=today).first()
    pages_today = today_entry.pages_read if today_entry else 0
    
    # Average pages per day (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    avg_pages = db.session.query(func.avg(ReadingDiary.pages_read)).filter(
        ReadingDiary.date >= thirty_days_ago,
        ReadingDiary.did_read == True
    ).scalar() or 0
    
    # Reading streak
    streak = calculate_streak()
    
    # Current book
    current_book = Book.query.filter_by(status='reading').first()
    
    return jsonify({
        'total_books': total_books,
        'books_read': books_read,
        'books_reading': books_reading,
        'books_want': books_want,
        'pages_today': pages_today,
        'avg_pages_day': round(avg_pages, 1),
        'streak': streak,
        'current_book': current_book.to_dict() if current_book else None
    })


def calculate_streak():
    """Calculate current reading streak."""
    today = date.today()
    streak = 0
    current_date = today
    
    while True:
        entry = ReadingDiary.query.filter_by(date=current_date, did_read=True).first()
        if entry:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak


@app.route('/api/stats/pages', methods=['GET'])
def get_pages_stats():
    """Get pages read statistics."""
    period = request.args.get('period', 'month')  # day, month, year
    
    today = date.today()
    
    if period == 'day':
        # Last 30 days
        start_date = today - timedelta(days=30)
        entries = ReadingDiary.query.filter(
            ReadingDiary.date >= start_date
        ).order_by(ReadingDiary.date).all()
        
        data = [{'date': e.date.isoformat(), 'pages': e.pages_read} for e in entries]
        
    elif period == 'month':
        # Last 12 months
        data = []
        for i in range(11, -1, -1):
            month_date = today - timedelta(days=i*30)
            month = month_date.month
            year = month_date.year
            
            total = db.session.query(func.sum(ReadingDiary.pages_read)).filter(
                db.extract('month', ReadingDiary.date) == month,
                db.extract('year', ReadingDiary.date) == year
            ).scalar() or 0
            
            data.append({
                'month': f'{year}-{month:02d}',
                'pages': total
            })
    else:
        # Last 5 years
        data = []
        for i in range(4, -1, -1):
            year = today.year - i
            total = db.session.query(func.sum(ReadingDiary.pages_read)).filter(
                db.extract('year', ReadingDiary.date) == year
            ).scalar() or 0
            
            data.append({
                'year': year,
                'pages': total
            })
    
    return jsonify(data)


@app.route('/api/stats/publishers', methods=['GET'])
def get_publishers_stats():
    """Get books count by publisher."""
    stats = db.session.query(
        Book.publisher,
        func.count(Book.id)
    ).filter(
        Book.publisher.isnot(None),
        Book.publisher != ''
    ).group_by(Book.publisher).all()
    
    return jsonify([{'publisher': s[0], 'count': s[1]} for s in stats])


@app.route('/api/stats/spending', methods=['GET'])
def get_spending_stats():
    """Get spending statistics."""
    total = db.session.query(func.sum(Book.purchase_price)).filter(
        Book.purchase_price.isnot(None)
    ).scalar() or 0
    
    # By month (last 12 months)
    today = date.today()
    monthly = []
    for i in range(11, -1, -1):
        month_date = today - timedelta(days=i*30)
        month = month_date.month
        year = month_date.year
        
        total_month = db.session.query(func.sum(Book.purchase_price)).filter(
            db.extract('month', Book.purchase_date) == month,
            db.extract('year', Book.purchase_date) == year
        ).scalar() or 0
        
        monthly.append({
            'month': f'{year}-{month:02d}',
            'amount': total_month
        })
    
    return jsonify({
        'total': total,
        'monthly': monthly
    })


@app.route('/api/stats/reading-time', methods=['GET'])
def get_reading_time_stats():
    """Get average reading time per book."""
    # Books that have both start and end dates
    books = Book.query.filter(
        Book.start_date.isnot(None),
        Book.end_date.isnot(None)
    ).all()
    
    if not books:
        return jsonify({'avg_days': 0, 'books': []})
    
    total_days = 0
    book_times = []
    
    for book in books:
        days = (book.end_date - book.start_date).days
        total_days += days
        book_times.append({
            'title': book.title,
            'days': days,
            'pages': book.pages or 0
        })
    
    avg_days = total_days / len(books) if books else 0
    
    return jsonify({
        'avg_days': round(avg_days, 1),
        'books': book_times
    })


# ============================================
# API: Notes
# ============================================

@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Get all notes."""
    note_type = request.args.get('type')
    book_id = request.args.get('book_id')
    
    query = Note.query
    
    if note_type:
        query = query.filter(Note.type == note_type)
    if book_id:
        query = query.filter(Note.book_id == int(book_id))
    
    notes = query.order_by(Note.created_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])


@app.route('/api/notes/book/<int:book_id>', methods=['GET'])
def get_book_notes(book_id):
    """Get all notes for a specific book."""
    notes = Note.query.filter_by(book_id=book_id).order_by(Note.created_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])


@app.route('/api/notes', methods=['POST'])
def create_note():
    """Create a new note."""
    data = request.get_json()
    
    note = Note(
        book_id=data['book_id'],
        type=data.get('type', 'thought'),
        content=data['content'],
        page_number=data.get('page_number')
    )
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify(note.to_dict()), 201


@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a note."""
    note = Note.query.get_or_404(note_id)
    data = request.get_json()
    
    if 'type' in data:
        note.type = data['type']
    if 'content' in data:
        note.content = data['content']
    if 'page_number' in data:
        note.page_number = data['page_number']
    
    db.session.commit()
    return jsonify(note.to_dict())


@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note."""
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return '', 204


# ============================================
# API: Quotes
# ============================================

@app.route('/api/quote', methods=['GET'])
def get_random_quote():
    """Get a random literary quote."""
    quotes = DailyQuote.query.all()
    if quotes:
        quote = random.choice(quotes)
        return jsonify(quote.to_dict())
    return jsonify(None)


# ============================================
# API: Export
# ============================================

@app.route('/api/export', methods=['GET'])
def export_data():
    """Export all data as JSON."""
    books = [book.to_dict() for book in Book.query.all()]
    diary = [entry.to_dict() for entry in ReadingDiary.query.all()]
    notes = [note.to_dict() for note in Note.query.all()]
    
    return jsonify({
        'books': books,
        'diary': diary,
        'notes': notes,
        'exported_at': datetime.utcnow().isoformat()
    })


# ============================================
# API: Filters (for dropdowns)
# ============================================

@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get available filter values."""
    authors = db.session.query(Book.author).filter(
        Book.author.isnot(None),
        Book.author != ''
    ).distinct().all()
    
    publishers = db.session.query(Book.publisher).filter(
        Book.publisher.isnot(None),
        Book.publisher != ''
    ).distinct().all()
    
    genres = db.session.query(Book.genre).filter(
        Book.genre.isnot(None),
        Book.genre != ''
    ).distinct().all()
    
    return jsonify({
        'authors': [a[0] for a in authors],
        'publishers': [p[0] for p in publishers],
        'genres': [g[0] for g in genres]
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
