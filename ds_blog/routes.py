"""contains the endpoints for ds_blog
"""
from random import choice

from json import dumps, loads

from flask import render_template, url_for, flash, redirect, request
from flask_login.utils import login_user, current_user, logout_user, login_required

from xmltodict import parse

from ds_blog import app, bcrypt, db, login_manager
from ds_blog.dictionary import bonfire_locations, weapon_dict, armor_dict, random_gestures
from ds_blog.forms import(LoginForm, RegistrationForm,
                        TimelineEntryForm, AnnouncementsForm, UpdateAccountForm)
from ds_blog.logic import add_new_td, td_graph_gen, save_picture
from ds_blog.models import(User, TimelineDelta,
                        TimelineEntry, Announcements)

@login_manager.user_loader
def load_user(user_id):
    """loads up user values for
    authentication and validation.

    Parameters
    ----------
    user_id : int
        id of the user.

    Returns
    -------
    User.query.get()
        fetches user data from db.
    """
    return User.query.get(int(user_id))

@app.route('/')
@app.route('/home')
def home():
    """uses flask route() decorator to open the home page.
    Additionally displays announcements

    Returns
    -------
    render_template
        contains the render_template for 'home.html'
        and passes through the title of 'Home Page'
        gestures and announcements.
    """
    gesture = choice(random_gestures)
    announcements = Announcements.query.all()
    return render_template('home.html',
                        title='Home Page',
                        gesture=gesture,
                        announcements=announcements
                        )

@app.route('/post-an', methods=['GET', 'POST'])
@login_required
def new_post():
    """uses flask route() decorator to open the new announcements page.
    AnnouncementsForm is used to validate and provide entry for the new announcement.
    and then it is published into the DB via SQLA.

    Returns
    -------
    render_template
        contains the render_template
        for 'post_announcement.html' and passes through
        the title of New Announcement,
        AnnouncementsForm() as form gestures.
        checks announcer boolean on end user
    """
    form = AnnouncementsForm()
    if form.validate_on_submit():
        announcement = Announcements(title=form.title.data,
                                content=form.content.data,
                                author=current_user
                                )
        db.session.add(announcement)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('post_announcement.html',
                        title='New Annoucement',
                        form=form,
                        legend ='New Announcement',
                        announcer=current_user.announcer
                        )

@app.route('/timeline')
def timeline():
    """uses flask route() decorator to open the timeline page.
    using timeline_entry, will display all timeline entries
    in order of latest to oldest.

    Returns
    -------
    render_template
        contains the render_template
        for 'timeline.html' and gesture.
    """
    gesture = choice(random_gestures)
    timeline_entry = TimelineEntry.query.order_by(TimelineEntry.id.desc()).all()
    return render_template('timeline.html',
                        title='Timeline',
                        gesture=gesture,
                        timeline_entry=timeline_entry
                        )

@app.route('/timeline_entry/<int:tl_id>', methods=['GET', 'POST'])
def view_timeline_entry(tl_id):
    """uses flask route() decorator to generate a timeline entry page.
    will display all available values of a given entry.

    Parameters
    ----------
    tl_id (int)
        timeline_entry id value.

    Returns
    -------
    render_template
        contains the render_template
        for 'timeline.html' and gesture
    """
    entry = TimelineEntry.query.get_or_404(tl_id)
    delta_entry = TimelineDelta.query.filter_by(tl_entry_id=tl_id).first()
    gesture = choice(random_gestures)
    entry_id = str(tl_id)
    return render_template('timeline_entry.html',
                        title='Timeline Entry',
                        entry=entry,
                        delta_entry=delta_entry,
                        gesture=gesture,
                        entry_id=entry_id)

@login_required
@app.route('/post-tl', methods=['GET', 'POST'])
def timeline_entry():
    """uses flask route() decorator to generate the form
    to generate timeline entries. requires developer boolean.

    Returns
    -------
    render_template
        contains the render_template
        for 'post_timeline_entry.html' and passes through gesture,
        developer boolean and form.
    """
    form = TimelineEntryForm()
    if form.validate_on_submit():
        character_name = form.character_name.data
        slash_data = loads(
            dumps(parse(form.slash_data.data)))
        pg_data = loads(
            dumps(parse(form.player_game_data.data)))
        attrib_data = loads(
            dumps(parse(form.attributes.data)))
        charAsm = loads(
            dumps(parse(form.char_equip.data)))
        base_stats = loads(
            dumps(parse(form.base_stats.data)))

        attrib_index = attrib_data.get('CheatTable').get(
            'CheatEntries').get('CheatEntry').get('CheatEntries').get('CheatEntry')
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
        add_new_td(character_name, total_deaths, soul_level, play_time)
        timeline_entry = TimelineEntry(
            character_name=character_name,
            author=current_user,
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
        db.session.add(timeline_entry)
        db.session.commit()
        latest = TimelineEntry.query.filter_by(character_name=character_name).order_by(TimelineEntry.id.desc()).first()
        id = latest.id
        td_graph_gen(character_name, id)
        flash('Timeline Entry has been created!', 'success')
        return redirect(url_for('timeline'))
    gesture = choice(random_gestures)
    return render_template('post_timeline_entry.html',
                        form=form,
                        gesture=gesture,
                        developer=current_user.developer
                        )



@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    """uses flask route() decorator to generate the form
    to edit account information.

    Returns
    -------
    render_template
        contains the render_template
        for 'account.html' and passes through gesture,
        image_file and form.
    """
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
    gesture = choice(random_gestures)
    return render_template('account.html',
                        title='Account',
                        image_file=image_file,
                        form=form,
                        gesture=gesture
                        )

@app.route('/about')
def about():
    """uses flask route() decorator
    to generate the about page.

    Returns
    -------
    render_template
        contains the render_template
        for 'about.html' and passes through gesture.
    """
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
    return render_template('login.html',
                        title='Login',
                        form=form
                        )

@app.route('/register', methods=['GET', 'POST'])
def register():
    """uses flask route() decorator
    to generate the about page.

    Returns
    -------
    render_template
        contains the render_template
        for 'register.html' and passes through gesture
        and form.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! you are able to log in', 'success')
        return redirect(url_for('home'))
    return render_template('register.html',
                        title='Register',
                        form=form
                        )

@app.route("/logout")
def logout():
    """uses flask route() decorator
    to generate the home page immediately after
    logging out the user.

    Returns
    -------
    redirect
        redirects the user to home()
    """
    logout_user()
    return redirect(url_for('home'))
