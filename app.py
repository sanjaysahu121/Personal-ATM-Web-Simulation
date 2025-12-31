from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_atm'

# Multi-user data 
users = {
    "101": {"name": "Rahul Sharma", "pin": "1234", "balance": 5000, "history": [], "type": "Savings"},
    "102": {"name": "Sneha Kapoor", "pin": "2222", "balance": 15000, "history": [], "type": "Current"},
    "103": {"name": "Amit Kumar", "pin": "3333", "balance": 2000, "history": [], "type": "Savings"},
    "104": {"name": "Priya Singh", "pin": "4444", "balance": 8500, "history": [], "type": "Savings"},
    "105": {"name": "Vikram Dev", "pin": "5555", "balance": 12000, "history": [], "type": "Current"},
}

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    acc_no = request.form.get('acc_no')
    user_pin = request.form.get('pin')
    if acc_no in users and users[acc_no]["pin"] == user_pin:
        session['user_id'] = acc_no
        return redirect(url_for('dashboard'))
    return render_template('login.html', error="Invalid Account Number or PIN!")

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: 
        return redirect(url_for('login_page'))
    user_id = session['user_id']
    return render_template('index.html', user=users[user_id], acc=user_id)

@app.route('/transaction', methods=['POST'])
def transaction():
    if 'user_id' not in session: return redirect(url_for('login_page'))
    
    acc_no = session['user_id']
    action = request.form.get('action')
    amount = float(request.form.get('amount', 0))

    if action == 'deposit' and amount > 0:
        users[acc_no]["balance"] += amount
        users[acc_no]["history"].append(f"Credited: +₹{amount}")
    elif action == 'withdraw' and amount > 0:
        if amount <= users[acc_no]["balance"]:
            users[acc_no]["balance"] -= amount
            users[acc_no]["history"].append(f"Debited: -₹{amount}")
        else:
            return render_template('index.html', user=users[acc_no], acc=acc_no, error="Insufficient Funds!")
    
    return redirect(url_for('dashboard'))

@app.route('/transfer', methods=['POST'])
def transfer():
    if 'user_id' not in session: return redirect(url_for('login_page'))

    sender_acc = session['user_id']
    receiver_acc = request.form.get('receiver_acc')
    amount = float(request.form.get('amount', 0))

    if receiver_acc not in users:
        return render_template('index.html', user=users[sender_acc], acc=sender_acc, error="Receiver Account Not Found!")
    
    if sender_acc == receiver_acc:
        return render_template('index.html', user=users[sender_acc], acc=sender_acc, error="Cannot transfer to yourself!")

    if amount > users[sender_acc]["balance"]:
        return render_template('index.html', user=users[sender_acc], acc=sender_acc, error="Insufficient Balance!")

    if amount > 0:
        users[sender_acc]["balance"] -= amount
        users[sender_acc]["history"].append(f"Sent: -₹{amount} to {users[receiver_acc]['name']}")
        users[receiver_acc]["balance"] += amount
        users[receiver_acc]["history"].append(f"Received: +₹{amount} from {users[sender_acc]['name']}")
        return render_template('index.html', user=users[sender_acc], acc=sender_acc, success=f"Successfully sent ₹{amount} to {users[receiver_acc]['name']}!")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)