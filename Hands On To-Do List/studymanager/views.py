from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from . import app, db
from .models import Board, List, Card
from flask import jsonify
import logging

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/boards')
@login_required
def boards():
    try:
        boards = Board.query.filter_by(user_id=current_user.id).order_by(Board.position).all()
        return render_template('index.html', boards=boards)
    except Exception as e:
        logging.error(f"Boards error: {str(e)}")
        flash('An error occurred loading boards.')
        return redirect(url_for('boards'))

@app.route('/board/<int:board_id>')
@login_required
def board(board_id):
    board = Board.query.get_or_404(board_id)
    if board.user_id != current_user.id:
        flash('You do not have access to this board.')
        return redirect(url_for('boards'))
    
    # Calculate progress: completed cards and total cards in board
    total_cards = 0
    completed_cards = 0
    for lst in board.lists:
        total_cards += len(lst.cards)
        completed_cards += sum(c.completed for c in lst.cards)
    board_progress_percent = round((completed_cards / total_cards * 100), 1) if total_cards > 0 else 0

    return render_template('board.html', board=board,
                           total_cards=total_cards,
                           completed_cards=completed_cards,
                           board_progress_percent=board_progress_percent)


@app.route('/add_board', methods=['POST'])
@login_required
def add_board():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Board name is required.')
        return redirect(url_for('boards'))
    try:
        max_pos = db.session.query(db.func.max(Board.position)).filter_by(user_id=current_user.id).scalar() or 0
        board = Board(name=name, user_id=current_user.id, position=max_pos + 1)
        db.session.add(board)
        db.session.commit()
        lists = [('To Do', 1), ('In Progress', 2), ('Done', 3)]
        for name, pos in lists:
            list_obj = List(name=name, board_id=board.id, position=pos)
            db.session.add(list_obj)
        db.session.commit()
        flash('Board created successfully.')
    except Exception as e:
        logging.error(f"Add board error: {str(e)}")
        db.session.rollback()
        flash('An error occurred creating the board.')
    return redirect(url_for('boards'))

@app.route('/delete_board/<int:board_id>')
@login_required
def delete_board(board_id):
    try:
        board = Board.query.get_or_404(board_id)
        if board.user_id != current_user.id:
            flash('You do not have access to this board.')
            return redirect(url_for('boards'))
        for list_obj in board.lists:
            for card in list_obj.cards:
                db.session.delete(card)
            db.session.delete(list_obj)
        db.session.delete(board)
        db.session.commit()
        flash('Board deleted successfully.')
    except Exception as e:
        logging.error(f"Delete board error: {str(e)}")
        db.session.rollback()
        flash('An error occurred deleting the board.')
    return redirect(url_for('boards'))

@app.route('/add_card/<int:list_id>', methods=['POST'])
@login_required
def add_card(list_id):
    try:
        list_obj = List.query.get_or_404(list_id)
        if list_obj.board.user_id != current_user.id:
            flash('You do not have access to this list.')
            return redirect(url_for('boards'))
        title = request.form.get('title', '').strip()
        if not title:
            flash('Card title is required.')
            return redirect(url_for('board', board_id=list_obj.board_id))
        description = request.form.get('description', '')
        due_date_str = request.form.get('due_date', '')
        reminder = False
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                today = datetime.now().date()
                if (due_date - today).days <= 3:
                    reminder = True
            except ValueError:
                flash('Invalid due date format. Use YYYY-MM-DD.')
                return redirect(url_for('board', board_id=list_obj.board_id))
        max_pos = db.session.query(db.func.max(Card.position)).filter_by(list_id=list_id).scalar() or 0
        card = Card(title=title, description=description, due_date=due_date_str, list_id=list_id, position=max_pos + 1, reminder=reminder)
        db.session.add(card)
        db.session.commit()
        flash('Card added successfully.')
    except Exception as e:
        logging.error(f"Add card error: {str(e)}")
        db.session.rollback()
        flash('An error occurred adding the card.')
    return redirect(url_for('board', board_id=list_obj.board_id))

@app.route('/edit_card/<int:card_id>', methods=['GET', 'POST'])
@login_required
def edit_card(card_id):
    try:
        card = Card.query.get_or_404(card_id)
        if card.list.board.user_id != current_user.id:
            flash('You do not have access to this card.')
            return redirect(url_for('boards'))
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            if not title:
                flash('Card title is required.')
                return render_template('edit_card.html', card=card)
            card.title = title
            card.description = request.form.get('description', '')
            due_date_str = request.form.get('due_date', '')
            if due_date_str:
                try:
                    datetime.strptime(due_date_str, '%Y-%m-%d')
                except ValueError:
                    flash('Invalid due date format. Use YYYY-MM-DD.')
                    return render_template('edit_card.html', card=card)
            card.due_date = due_date_str
            card.completed = 'completed' in request.form
            db.session.commit()
            flash('Card updated successfully.')
            return redirect(url_for('board', board_id=card.list.board_id))
        return render_template('edit_card.html', card=card)
    except Exception as e:
        logging.error(f"Edit card error: {str(e)}")
        db.session.rollback()
        flash('An error occurred editing the card.')
        return redirect(url_for('boards'))

@app.route('/delete_card/<int:card_id>')
@login_required
def delete_card(card_id):
    try:
        card = Card.query.get_or_404(card_id)
        if card.list.board.user_id != current_user.id:
            flash('You do not have access to this card.')
            return redirect(url_for('boards'))
        board_id = card.list.board_id
        db.session.delete(card)
        db.session.commit()
        flash('Card deleted successfully.')
        return redirect(url_for('board', board_id=board_id))
    except Exception as e:
        logging.error(f"Delete card error: {str(e)}")
        db.session.rollback()
        flash('An error occurred deleting the card.')
        return redirect(url_for('boards'))

@app.route('/move_card', methods=['POST'])
@login_required
def move_card():
    try:
        data = request.get_json()
        if not data or 'card_id' not in data or 'list_id' not in data or 'old_list_id' not in data:
            return jsonify({'success': False, 'error': 'Invalid request data.'})
        card_id = data['card_id']
        new_list_id = data['list_id']
        old_list_id = data['old_list_id']
        card = Card.query.get_or_404(card_id)
        if card.list.board.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Access denied.'})
        new_list = List.query.get(new_list_id)
        old_list = List.query.get(old_list_id)
        if not new_list or not old_list:
            return jsonify({'success': False, 'error': 'Invalid list.'})
        if new_list.name == 'Done':
            card.completed = True
        elif old_list.name == 'Done' and new_list.name != 'Done':
            card.completed = False
        card.list_id = new_list_id
        db.session.commit()
        
        # Calculate updated progress for the board
        board = card.list.board
        total_cards = sum(len(list.cards) for list in board.lists)
        completed_cards = sum(sum(1 for card in list.cards if card.completed) for list in board.lists)
        progress_percent = (completed_cards / total_cards * 100) if total_cards > 0 else 0
        
        return jsonify({
            'success': True,
            'total_cards': total_cards,
            'completed_cards': completed_cards,
            'progress_percent': progress_percent,
            'completed': card.completed  # Add completed status
        })
    except Exception as e:
        logging.error(f"Move card error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'An error occurred moving the card.'})

@app.route('/progress')
@login_required
def progress():
    try:
        total_cards = Card.query.join(List).join(Board).filter(Board.user_id == current_user.id).count()
        completed_cards = Card.query.join(List).join(Board).filter(Board.user_id == current_user.id, Card.completed == True).count()
        progress_percent = (completed_cards / total_cards * 100) if total_cards > 0 else 0
        return render_template('progress.html', completed=completed_cards, total=total_cards, percent=progress_percent)
    except Exception as e:
        logging.error(f"Progress error: {str(e)}")
        flash('An error occurred loading progress.')
        return redirect(url_for('boards'))
    
@app.route('/get_board_progress/<int:board_id>')
@login_required
def get_board_progress(board_id):
    try:
        board = Board.query.get_or_404(board_id)
        if board.user_id != current_user.id:
            return jsonify({'error': 'Access denied.'}), 403
        total_cards = sum(len(list.cards) for list in board.lists)
        completed_cards = sum(sum(1 for card in list.cards if card.completed) for list in board.lists)
        progress_percent = (completed_cards / total_cards * 100) if total_cards > 0 else 0
        return jsonify({
            'total_cards': total_cards,
            'completed_cards': completed_cards,
            'progress_percent': progress_percent
        })
    except Exception as e:
        logging.error(f"Get board progress error: {str(e)}")
        return jsonify({'error': 'An error occurred.'}), 500

@app.route('/reminders_data')
@login_required
def reminders_data():
    # Query reminders due soon for current_user and return JSON
    today = datetime.now().date()
    three_days_later = today + timedelta(days=3)
    reminders_query = Card.query.join(List).join(Board).filter(
        Board.user_id == current_user.id,
        Card.reminder == True,
        Card.due_date <= three_days_later.strftime('%Y-%m-%d'),
        Card.completed == False
    ).all()
    reminders = []
    for card in reminders_query:
        reminders.append({
            "board_name": card.list.board.name,
            "title": card.title,
            "due_date": card.due_date
        })
    return jsonify(reminders=reminders)

@app.route('/reminders')
@login_required
def reminders():
    today = datetime.now().date()
    three_days = today + timedelta(days=3)
    reminders = Card.query.join(List).join(Board).filter(
        Board.user_id == current_user.id,
        Card.reminder == True,
        Card.due_date <= three_days.strftime("%Y-%m-%d"),
        Card.completed == False
    ).all()
    return render_template('reminders.html', reminders=reminders)
