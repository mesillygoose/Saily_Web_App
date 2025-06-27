from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'saily-esim-secret-key'

# Data storage file (simple JSON file instead of database)
DATA_FILE = 'data/esim_data.json'

def load_data():
    """Load data from JSON file - if file doesn't exist, create default data"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            # If file is corrupted, return default data
            pass
    # Default data if file doesn't exist
    return {
        'plans': [],
        'destinations': [
            {'country': 'Japan', 'flag': '🇯🇵', 'price_1gb': 9.99, 'price_3gb': 19.99, 'price_5gb': 29.99},
            {'country': 'France', 'flag': '🇫🇷', 'price_1gb': 7.99, 'price_3gb': 15.99, 'price_5gb': 23.99},
            {'country': 'Germany', 'flag': '🇩🇪', 'price_1gb': 8.99, 'price_3gb': 17.99, 'price_5gb': 25.99},
            {'country': 'United States', 'flag': '🇺🇸', 'price_1gb': 12.99, 'price_3gb': 24.99, 'price_5gb': 39.99},
            {'country': 'United Kingdom', 'flag': '🇬🇧', 'price_1gb': 9.99, 'price_3gb': 18.99, 'price_5gb': 27.99},
            {'country': 'Italy', 'flag': '🇮🇹', 'price_1gb': 8.99, 'price_3gb': 16.99, 'price_5gb': 24.99},
            {'country': 'Spain', 'flag': '🇪🇸', 'price_1gb': 7.99, 'price_3gb': 15.99, 'price_5gb': 22.99},
            {'country': 'Australia', 'flag': '🇦🇺', 'price_1gb': 11.99, 'price_3gb': 22.99, 'price_5gb': 34.99}
        ],
        'user_balance': 150.00,
        'active_plans': 0,
        'data_used': 0,
        'countries_covered': 200
    }
def save_data(data):
    """Save data to JSON file"""
    # Create data folder if it doesn't exist
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
@app.route('/')
def index():
    """Main dashboard page - this is what users see first"""
    data = load_data()

    # Get the last 5 plans for recent activity
    recent_plans = data['plans'][-5:] if data['plans'] else []

    return render_template('index.html',
                           balance=data['user_balance'],
                           active_plans=len([p for p in data['plans'] if p.get('status') == 'active']),
                           data_used=sum(p.get('data_used', 0) for p in data['plans']),
                           countries_covered=data['countries_covered'],
                           recent_plans=recent_plans)
@app.route('/destinations')
def destinations():
    """Show all available countries where you can buy eSIM"""
    data = load_data()
    return render_template('destinations.html', destinations=data['destinations'])

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    """Buy a new eSIM plan"""
    data = load_data()
    # If user just wants to see the page (GET request)
    if request.method == 'GET':
        return render_template('purchase.html', destinations=data['destinations'])
    # If user submitted the form (POST request)
    if request.method == 'POST':
        # Get form data
        country = request.form.get('country')
        data_amount = request.form.get('data_amount')  # like '1gb', '3gb', '5gb'
        duration = request.form.get('duration', '30')  # default 30 days
        # Check if country was selected
        if not country:
            flash('Please select a country', 'error')
            return redirect(url_for('purchase'))
        # Check if data plan was selected
        if not data_amount:
            flash('Please select a data plan', 'error')
            return redirect(url_for('purchase'))
        # Find the selected country in our list
        destination = None
        for dest in data['destinations']:
            if dest['country'] == country:
                destination = dest
                break
        if not destination:
            flash('Invalid country selected', 'error')
            return redirect(url_for('purchase'))
        # Get the price for selected data plan
        price_key = f'price_{data_amount}'  # becomes 'price_1gb', 'price_3gb', etc.
        if price_key not in destination:
            flash('Invalid data plan selected', 'error')
            return redirect(url_for('purchase'))
        price = destination[price_key]
        # Check if user has enough money
        if data['user_balance'] < price:
            flash(f'Not enough money! You need €{price:.2f} but only have €{data["user_balance"]:.2f}', 'error')
            return redirect(url_for('purchase'))
        # Create the new plan
        new_plan = {
            'id': len(data['plans']) + 1,  # simple ID system
            'country': country,
            'flag': destination['flag'],
            'data_amount': data_amount,
            'duration': int(duration),
            'price': price,
            'purchase_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active',
            'data_used': 0  # no data used yet
        }
        # Add plan to user's account
        data['plans'].append(new_plan)

        # Take money from user's balance
        data['user_balance'] -= price

        # Save everything
        save_data(data)

        # Show success message
        flash(f'Success! Bought {data_amount.upper()} plan for {country}. Cost: €{price:.2f}', 'success')
        return redirect(url_for('my_plans'))
    # This shouldn't happen, but just in case
    return render_template('purchase.html', destinations=data['destinations'])

@app.route('/my_plans')
def my_plans():
    """Show all plans the user has purchased"""
    data = load_data()
    return render_template('my_plans.html', plans=data['plans'])

@app.route('/top_up', methods=['GET', 'POST'])
def top_up():
    """Add money to user's account balance"""
    data = load_data()
    # If user just wants to see the page (GET request)
    if request.method == 'GET':
        return render_template('top_up.html', current_balance=data['user_balance'])
    # If user submitted the form (POST request)
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            # Check if amount is valid
            if amount <= 0:
                flash('Please enter an amount greater than €0', 'error')
                return redirect(url_for('top_up'))
            if amount > 1000:
                flash('Maximum top-up amount is €1000', 'error')
                return redirect(url_for('top_up'))
            # Add money to balance
            data['user_balance'] += amount
            save_data(data)

            flash(f'Successfully added €{amount:.2f} to your account!', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('Please enter a valid number', 'error')
            return redirect(url_for('top_up'))
    # This shouldn't happen, but just in case
    return render_template('top_up.html', current_balance=data['user_balance'])

@app.route('/activate_plan/<int:plan_id>')
def activate_plan(plan_id):
    """Activate a purchased plan (simple function for demo)"""
    data = load_data()
    # Find the plan with ID
    plan = None
    for p in data['plans']:
        if p['id'] == plan_id:
            plan = p
            break
    if not plan:
        flash('Plan not found', 'error')
        return redirect(url_for('my_plans'))

    if plan['status'] == 'active':
        flash('Plan is already active', 'warning')
    else:
        plan['status'] = 'active'
        plan['activation_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_data(data)
        flash(f'Successfully activated plan for {plan["country"]}!', 'success')
    return redirect(url_for('my_plans'))

# Simple API endpoints
@app.route('/api/destinations')
def api_destinations():
    """API to get all destinations as JSON"""
    data = load_data()
    return jsonify(data['destinations'])

@app.route('/api/balance')
def api_balance():
    """API to get current balance as JSON"""
    data = load_data()
    return jsonify({'balance': data['user_balance']})

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    print("Starting Saily eSIM Management System...")
    print("Open your browser to: http://localhost:5000")
    print("Manage your global connectivity with ease!")

    app.run(debug=True, host='0.0.0.0', port=5000)