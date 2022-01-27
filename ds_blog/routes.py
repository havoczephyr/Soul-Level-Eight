from random import choice
import secrets
import os
from PIL import Image
from ds_blog import app, bcrypt, db
from ds_blog.models import User, TimelineDelta, TimelineEntry, Announcements, Comments, BonfireLocation, add_new_td
from ds_blog.forms import LoginForm, RegistrationForm, TimelineEntryForm, AnnouncementsForm, CommentForm, UpdateAccountForm
from ds_blog.dictionary import bonfire_locations, weapon_dict, armor_dict
from flask import render_template, url_for, flash, redirect, request


from xmltodict import parse
from json import dumps, loads

from flask_login.utils import login_user, current_user, logout_user, login_required

random_gestures = ['Umbasa', 'Vereror Nox', 'See You, Space Cowboy', 'Easy Come, Easy Go', 'See you, Space Samurai', 'See you, Cowgirl, Someday, Somewhere', "You're gonna carry that weight", "Soul of the mind, key to lifes' ether. Soul of the lost, withdrawn from its vessel. Let strength be granted, so the world might be mended... so the world might be mended.", "Let these souls, withdrawn from their vesels, Manifestations of disparity, Elucidated by fire, Burrow deep within me, Retreating to a darkness beyond the reach of flame, Let them assume a new master, Inhabiting ash, casting themselves upon new forms."]

@app.route('/')
@app.route('/home')
def home():
    gesture = choice(random_gestures)
    return render_template('home.html', title='Home Page', gesture=gesture)

@app.route('/timeline')
def timeline():
    gesture = choice(random_gestures)
    return render_template('timeline.html', title='Timeline', gesture=gesture)

@app.route('/timeline_entry/<int:tl_id>', methods=['GET', 'POST'])
def view_timeline_entry(tl_id):
    entry = TimelineEntry.query.get_or_404(tl_id)
    delta_entry = TimelineDelta.query.filter_by(tl_entry_id=tl_id).first()
    gesture = choice(random_gestures)
    return render_template('timeline_entry.html', title='Timeline Entry', entry=entry, delta_entry=delta_entry, gesture=gesture)

@login_required
@app.route('/post_tl', methods=['GET', 'POST'])
def timeline_entry():
    form = TimelineEntryForm()
    if form.validate_on_submit():
        character_name = form.character_name.data
        slash_data = loads(dumps(parse(form.slash_data.data)))
        pg_data = loads(dumps(parse(form.player_game_data.data)))
        attrib_data = loads(dumps(parse(form.attributes.data)))
        charAsm = loads(dumps(parse(form.char_equip.data)))
        base_stats = loads(dumps(parse(form.base_stats.data)))

        attrib_index = attrib_data.get('CheatTable').get('CheatEntries').get('CheatEntry').get('CheatEntries').get('CheatEntry')
        soul_level = int(attrib_index[0].get('LastState').get('@Value'))
        vitality = int(attrib_index[1].get('LastState').get('@Value'))
        attunement = int(attrib_index[2].get('LastState').get('@Value'))
        endurance = int(attrib_index[3].get('LastState').get('@Value'))
        strength = int(attrib_index[4].get('LastState').get('@Value'))
        dexterity = int(attrib_index[5].get('LastState').get('@Value'))
        resistance = int(attrib_index[6].get('LastState').get('@Value'))
        intelligence = int(attrib_index[7].get('LastState').get('@Value'))
        faith = int(attrib_index[8].get('LastState').get('@Value'))

        slash_index = slash_data.get('CheatTable').get('CheatEntries').get('CheatEntry').get('CheatEntries').get('CheatEntry')
        journey_cyl = int(slash_index[0].get('LastState').get('@Value')) + 1
        bonfire = bonfire_locations.get(slash_index[1].get('LastState').get('@Value'))

        pg_index = pg_data.get('CheatTable').get('CheatEntries').get('CheatEntry').get('CheatEntries').get('CheatEntry')
        play_time = int(pg_index[0].get('LastState').get('@Value'))
        total_deaths = int(pg_index[10].get('LastState').get('@Value'))

        char_index = charAsm.get('CheatTable').get('CheatEntries').get('CheatEntry').get('CheatEntries').get('CheatEntry')
        primary_left_weapon = weapon_dict.get(char_index[0].get('LastState').get('@Value'))
        primary_right_weapon = weapon_dict.get(char_index[1].get('LastState').get('@Value'))
        secondary_left_weapon = weapon_dict.get(char_index[2].get('LastState').get('@Value'))
        secondary_right_weapon = weapon_dict.get(char_index[3].get('LastState').get('@Value'))
        helmet = armor_dict.get(char_index[8].get('LastState').get('@Value'))
        armor = armor_dict.get(char_index[9].get('LastState').get('@Value'))
        gauntlet = armor_dict.get(char_index[10].get('LastState').get('@Value'))
        leggings = armor_dict.get(char_index[11].get('LastState').get('@Value'))

        bs_index = base_stats.get('CheatTable').get('CheatEntries').get('CheatEntry').get('CheatEntries').get('CheatEntry')
        max_HP = int(bs_index[1].get('LastState').get('@Value'))
        max_stamina = int(bs_index[5].get('LastState').get('@Value'))
        soft_humanity = int(bs_index[6].get('LastState').get('@Value'))
        timeline_entry = TimelineEntry(
            character_name=character_name,
            soul_level=soul_level,
            vitality=vitality,
            attunement=attunement,
            endurance=endurance,
            strength=strength,
            dexterity=dexterity,
            resistance=resistance,
            intelligence=intelligence,
            faith=faith,
            last_bonfire=bonfire,
            total_deaths=total_deaths,
            journey_cycle=journey_cyl,
            max_HP=max_HP,
            max_stamina=max_stamina,
            soft_humanity=soft_humanity,
            primary_left_weapon=primary_left_weapon,
            primary_right_weapon=primary_right_weapon,
            secondary_left_weapon=secondary_left_weapon,
            secondary_right_weapon=secondary_right_weapon,
            helmet=helmet,
            armor=armor,
            gauntlet=gauntlet,
            leggings=leggings,
            play_time=play_time
        )
        add_new_td(character_name, total_deaths, soul_level, play_time)
        #before I commit timeline_entry, I need to perform timeline_delta's entry so that first() pulls the latest entry from the db. THEN perform tiemline entry's new entry.
        db.session.add(timeline_entry)
        db.session.commit()
        flash('Timeline Entry has been created!', 'success')
        return redirect(url_for('timeline'))
    gesture = choice(random_gestures)
    return render_template('post_timeline_entry.html', form=form, gesture=gesture)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)





@app.route('/about')
def about():
    gesture = choice(random_gestures)
    return render_template('about.html', title='About')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! you are able to log in', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))