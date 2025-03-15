from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Expense
from datetime import datetime
from passlib.hash import bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # SQLite database
app.secret_key = '5f2362154737ebb06a856d70123456'



# Initialize the database
db.init_app(app)


#Home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def loginn():
    return render_template('login.html')

@app.route('/register')
def signup():
    return render_template('register.html')



# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        
        password = request.form['password']
        confirm_password = request.form['confirm_password']

# both passwords match or not
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))


        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another one.','danger')
            return redirect(url_for('register'))

        # Hash the password
        # hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create a new user instance
        new_user = User(username=username, password=password)
        
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.','success')
        return redirect(url_for('login'))
#ekkada return undhi login ki veltada leda first reistation veltada???




    return render_template('register.html')




# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query the user by username
        user = User.query.filter_by(username=username).first()

        # If the user exists and password is correct
        if user and user.check_password(user.password, password):
            # flash('Login successful!', 'success')

            # Store the user in session
            session['user_id'] = user.id
            session['username'] = user.username

            return redirect(url_for('dashboard'))

        # If the credentials are incorrect
        flash('Login failed. Please check your username and password.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

# User dashboard route (only accessible after login)
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    # Get the start and end date from the form (if provided)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Get the selected category from the query parameters (if provided)
    selected_category = request.args.get('category')

    # Get the search term from the query parameters (if provided)
    search_term = request.args.get('search_term')

    # Available categories (static or dynamic)
    available_categories = ['Food', 'Travel', 'Entertainment', 'Bills', 'Other']

    # Initialize the query for expenses (filter by user_id)
    expenses = Expense.query.filter_by(user_id=session['user_id'])

    # Apply filters
    if start_date and end_date:
        expenses = expenses.filter(Expense.date >= start_date, Expense.date <= end_date)
    if selected_category:
        expenses = expenses.filter_by(category=selected_category)
    if search_term:
        expenses = expenses.filter(Expense.description.ilike(f'%{search_term}%'))

    # Execute the query and get the results
    expenses = expenses.all()

    # Calculate total expenses
    total_expenses = sum(expense.amount for expense in expenses)

    # Fetch the user's total limit and budget
    user = User.query.filter_by(id=session['user_id']).first()
    # total_limit = user.total_limit if user else None
    budget = user.budget if user else None

    # Check if total expenses exceed the budget
    if budget and total_expenses > budget:
        flash(f'You have exceeded your budget of ₹{budget}!', 'danger')
    remaining_budget = budget - total_expenses if budget is not None else None
    # Calculate category-wise breakdown
    category_breakdown = {}
    for expense in expenses:
        if expense.category:
            if expense.category not in category_breakdown:
                category_breakdown[expense.category] = 0
            category_breakdown[expense.category] += expense.amount

    return render_template('dashboard.html', expenses=expenses, total_expenses=total_expenses,
                           category_breakdown=category_breakdown, available_categories=available_categories, budget=budget,remaining_budget=remaining_budget)

# 

# Route for adding expenses
@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount')
        date = request.form.get('date')
        category = request.form.get('category')

        # Convert date input to a valid date object
        expense_date = datetime.strptime(date, '%Y-%m-%d')  

        # Create a new expense
        new_expense = Expense(user_id=session['user_id'], description=description, amount=float(amount), date=expense_date, category=category)

        # Add the new expense to the database
        db.session.add(new_expense)
        db.session.commit()
# -----
        flash('Expense added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_expense.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

    # edit expense----------

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    
    expense = Expense.query.get_or_404(expense_id)
    
    if request.method == 'POST':
        expense.description = request.form['description']
        expense.amount = float(request.form['amount'])
        expense.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        expense.category = request.form['category']
        db.session.commit()
        
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_expense.html', expense=expense)


#-------------------------------------------------------------------------------------------------------------------------------------------
#delete expense
@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != session['user_id']:
        flash('You do not have permission to delete this expense.', 'danger')
        return redirect(url_for('dashboard') ) 
    db.session.delete(expense)
    db.session.commit()
    
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

#-------------------------------------------------------------------------------------------------------------
@app.route('/set_budget', methods=['GET', 'POST'])
def set_budget():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        budget = request.form.get('budget')
        if budget:
            user.budget = float(budget)
            db.session.commit()
            flash('Budget set successfully!', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('set_budget.html', budget=user.budget)


@app.route('/delete_budget', methods=['POST'])
def delete_budget():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user.budget = 0.0  # Reset the budget to zero or None
    db.session.commit()
    flash('Budget deleted successfully!', 'success')
    
    return redirect(url_for('dashboard'))






if __name__ == '__main__':
   
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)
