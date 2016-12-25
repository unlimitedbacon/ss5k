from datetime import datetime
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import RegisterForm, LoginForm, AddCarForm, EditForm
from .models import User, Car
from .email import send_confirmation

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.now()
        db.session.add(g.user)
        db.session.commit()

@app.route('/')
@app.route('/index')
def index():
    if g.user.is_authenticated:
        return redirect(url_for('your_cars'))
    else:
        return render_template('index.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'GET':
        return render_template('register.html', title='Register', form=form)
    elif form.validate():
        email = form.email.data
        password = form.password.data
        errors = []
        if User.query.filter_by(email=email).first():
            errors.append('That email is already registered')
        if len(password) < 8:
            errors.append('Passwords must be 8 characters or more')
        if len(errors) > 0:
            for error in errors:
                flash(error)
            return render_template('register.html', title='Register', form=form)
        user = User(email, password)
        db.session.add(user)
        send_confirmation(user)
        db.session.commit()
        return redirect(url_for('pending'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', title='Login', form=form)
    elif form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            if user.confirmed:
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('index'))
            else:
                return redirect(url_for('pending'))
        flash('Invalid username or password')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/confirm/<code>')
def confirm(code):
    user = User.query.filter(User.confirmation == code).first()
    if not user:
        flash('Invalid confirmation code')
        return redirect(url_for('index'))
    else:
        user.confirmed = True
        user.confirmation = None
        login_user(user)
        db.session.commit()
        flash('Account activated. Welcome to Jalopalert.', 'success')
        return redirect(url_for('your_cars'))

@app.route('/pending')
def pending():
    return render_template('pending.html')

@app.route('/your_cars')
@login_required
def your_cars():
    cars = g.user.cars
    return render_template('your_cars.html',
                           title='Your Cars',
                           cars=cars)

@app.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car(title='Add Car',car=None):
    edit = False
    if car is not None:
        edit = True
    # Load car info if we are doing an edit
    if edit:
        car_id = car.id
        years = car.years.split(', ')
        yards = [ y.id for y in car.yards ]
        form = AddCarForm(make=car.make,model=car.model,years=years,yards=yards)
    else:
        form = AddCarForm()
    if request.method == 'GET':
        if len(g.user.cars) >= 20:
            flash('Sorry, you cannot have more than 20 cars')
            return redirect(url_for('your_cars'))
        else:
            return render_template('add_car.html', title=title, form=form)
    elif form.validate():
        if not edit and len(g.user.cars) >= 20:
            flash('Sorry, you cannot have more than 20 cars')
            return redirect(url_for('your_cars'))
        make = form.make.data
        model = form.model.data
        years = form.years.data
        yards = form.yards.data
        # Check to make sure they actually entered something
        if not make and not model and years == []:
            flash('You need to enter a make, a model, or a year')
            return render_template('add_car.html', title=title, form=form)
        if yards == []:
            flash('You need to choose at leat one junkyard')
            return render_template('add_car.html', title=title, form=form)
        # Delete original if this is an edit
        if edit:
            db.session.delete(car)
        car = Car(make,model,years,yards,g.user)
        db.session.add(car)
        db.session.commit()
        flash('Car Saved', 'success')
        return redirect(url_for('your_cars'))
    flasherrors(form.errors)
    return render_template('add_car.html', title=title, form=form)

@app.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    car = Car.query.get(car_id)
    if car is None:
        flash('Car does not exist')
        return redirect(url_for('your_cars'))
    if car.user_id != g.user.id:
        flash('That is not your car')
        return redirect(url_for('your_cars'))
    return add_car(title='Edit Car',car=car)

@app.route('/delete_car/<int:car_id>')
@login_required
def delete_car(car_id):
    car = Car.query.get(car_id)
    if car is None:
        flash('Car does not exist')
        return redirect(url_for('your_cars'))
    if car.user_id != g.user.id:
        flash('That is not your car')
        return redirect(url_for('your_cars'))
    db.session.delete(car)
    db.session.commit()
    flash('Car removed', 'success')
    return redirect(url_for('your_cars'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.context_processor
def inject():
    return {
            'user': current_user
            }

def flasherrors(errors):
    print(errors)
    for field, errorlist in errors.items():
        flash('Error in %s: %s' % (field, "<br".join(errorlist)) )
