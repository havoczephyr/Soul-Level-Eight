from datetime import date, datetime
from ds_blog import db
from flask_login import UserMixin
import matplotlib.pyplot as plt

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    developer = db.Column(db.Boolean, nullable=False, default=False)
    announcer = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    announcements = db.relationship('Announcements', backref='author', lazy=True)
    timeline_entries = db.relationship('TimelineEntry', backref='author', lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class TimelineEntry(db.Model):
    __tablename__='timeline_entry'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    character_name = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    soul_level = db.Column(db.Integer, nullable=False)
    vitality = db.Column(db.Integer, nullable=False)
    attunement = db.Column(db.Integer, nullable=False)
    endurance = db.Column(db.Integer, nullable=False)
    strength = db.Column(db.Integer, nullable=False)
    dexterity = db.Column(db.Integer, nullable=False)
    resistance = db.Column(db.Integer, nullable=False)
    intelligence = db.Column(db.Integer, nullable=False)
    faith = db.Column(db.Integer, nullable=False)
    last_bonfire = db.Column(db.Integer, nullable=False)
    total_deaths = db.Column(db.Integer, nullable=False)
    journey_cycle = db.Column(db.Integer, nullable=False)
    max_HP = db.Column(db.Integer, nullable=False)
    max_stamina = db.Column(db.Integer, nullable=False)
    soft_humanity = db.Column(db.Integer, nullable=False)
    primary_left_weapon = db.Column(db.String, nullable=False)
    primary_right_weapon = db.Column(db.String, nullable=False)
    secondary_left_weapon = db.Column(db.String, nullable=False)
    secondary_right_weapon = db.Column(db.String, nullable=False)
    helmet = db.Column(db.String, nullable=False)
    armor = db.Column(db.String, nullable=False)
    gauntlet = db.Column(db.String, nullable=False)
    leggings = db.Column(db.String, nullable=False)
    play_time = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"TimelineEntry('{self.last_bonfire}', '{self.date_posted}', '{self.character_name}')"

def td_graph_gen(character_name, id):
    td_plot = []
    entry = TimelineEntry.query.filter_by(character_name=character_name)
    entry_len = 0
    for i in entry:
        td_plot.append(i.total_deaths)
        entry_len = entry_len + 1
    x = list(range(1,(entry_len + 1)))
    y = td_plot
    plt.fill_between(x, y, color='skyblue', alpha=0.8)
    plt.plot(x, y, color='skyblue')
    plt.xlabel('Timeline Entries')
    plt.ylabel('Deaths Over Time')
    plt.savefig(f'ds_blog/static/td_graphs/{id}.jpg')
    

    # _, f_ext = os.path.splitext(form_picture.filename)
    # picture_fn = random_hex + f_ext
    # picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

class TimelineDelta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tl_entry_id = db.Column(db.Integer, db.ForeignKey('timeline_entry.id'), nullable=False)
    death_delta = db.Column(db.Float, nullable=False)
    sl_delta = db.Column(db.Float, nullable=False)
    playtime_delta = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"TimelineDelta('{self.tl_entry_id}', '{self.death_delta}', '{self.sl_delta}', '{self.playtime_delta}')"

def add_new_td(character_name, total_deaths, soul_level, play_time):
    #I need to query the database for the latest entry.
    #I then need to match that entry with the most previous entry with the same character name
    #if no previous match exists, then all values that would otherwise be for the previous entry should be 0
    #finally, I need to take the values from the latest entry and subtract them from the previous entry to collect the delta of each value.
    # data = TimelineEntry.query.filter_by(character_name=character_name).first()
    data = TimelineEntry.query.filter_by(character_name=character_name).order_by(TimelineEntry.id.desc()).first()
    latest_data = TimelineEntry.query.order_by(TimelineEntry.id.desc()).first()
    try:
        last_state_deaths = int(data.total_deaths)
        print(f"last state deaths: {last_state_deaths}")
        last_state_sl = int(data.soul_level)
        print(f"last_state_sl: {last_state_sl}")
        last_state_pt = int(data.play_time)
        print(f"last_state_pt: {last_state_pt}")
    except AttributeError:
        print("couldn't pull data")
        last_state_deaths = 0
        last_state_sl = 0
        last_state_pt = 0
    try:
        last_entry_id = latest_data.id
    except AttributeError:
        print("couldn't find last entry")
        last_entry_id = 0

    tl_entry_id = last_entry_id + 1
    death_delta = total_deaths - last_state_deaths
    print(f'Death Delta {total_deaths} - {last_state_deaths} = {death_delta}')
    sl_delta = soul_level - last_state_sl
    print(f'SL Delta = {soul_level} - {last_state_sl} = {sl_delta}')
    playtime_delta = play_time - last_state_pt
    print(f"Play Time Delta= {play_time} - {last_state_pt} = {playtime_delta}")

    timeline_delta = TimelineDelta(
        tl_entry_id=tl_entry_id,
        death_delta=death_delta,
        sl_delta=sl_delta,
        playtime_delta=playtime_delta
    )
    db.session.add(timeline_delta)
    db.session.commit()


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tl_entry_id = db.Column(db.Integer, db.ForeignKey('timeline_entry.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    visibility = db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return f"Comments('{self.tl_entry_id}', '{self.date_posted}', '{self.user_id}')"

class Announcements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Announcements('{self.title}', '{self.date_posted}')"

class BonfireLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bonfire_name = db.Column(db.String, nullable=False)
    coords_x = db.Column(db.Float, nullable=False)
    coords_y = db.Column(db.Float, nullable=False)