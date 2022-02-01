from datetime import date, datetime
from ds_blog import db
from flask_login import UserMixin

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

class TimelineDelta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tl_entry_id = db.Column(db.Integer, db.ForeignKey('timeline_entry.id'), nullable=False)
    death_delta = db.Column(db.Float, nullable=False)
    sl_delta = db.Column(db.Float, nullable=False)
    playtime_delta = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"TimelineDelta('{self.tl_entry_id}', '{self.death_delta}', '{self.sl_delta}', '{self.playtime_delta}')"

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