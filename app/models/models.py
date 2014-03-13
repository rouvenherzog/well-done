from ext.sys.database import db
from flask.ext.security import UserMixin, RoleMixin
from datetime import datetime, timedelta

roles_users = db.Table('roles_users',
		db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
		db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
	)

badges_users = db.Table('badges_users',
		db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
		db.Column('badge_id', db.Integer(), db.ForeignKey('badge.id'))
	)

class Role(db.Model, RoleMixin):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(80), unique=True)
	description = db.Column(db.String(255))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True)
	name = db.Column(db.String(255))
	password = db.Column(db.String(255))
	active = db.Column(db.Boolean())
	confirmed_at = db.Column(db.DateTime())
	roles = db.relationship('Role', secondary=roles_users,
							backref=db.backref('users', lazy='dynamic'))

	agrees = db.relationship('Badge', secondary=badges_users,
							backref=db.backref('agreeing', lazy='dynamic'))

	@property
	def received_badge_points(self):
		return sum([
			( badge.value * pow(2, len(badge.agreeing.all())) )
			for badge in self.valid_received_badges
		])

	@property
	def valid_received_badges(self):
		return [
			b for b in self.received_badges if not b.wasnt_me
		]

class Badge( db.Model ):
	id = db.Column( db.Integer, primary_key=True )
	title = db.Column( db.Text )
	value = db.Column( db.Integer, default=1 )
	send_at = db.Column( db.DateTime, default=datetime.now() )
	wasnt_me = db.Column( db.Boolean, default=0 )

	@classmethod
	def get_news(Badge):
		return [
			"{0} thinks {1} did something awesome.".format(badge.sender.name, badge.receiver.name) 
			for badge in Badge.query.filter(
				Badge.send_at > datetime.now() - timedelta(days=5)
			).order_by(Badge.send_at.desc()).slice(0,5)
		]

	sender_id = db.Column( db.Integer, db.ForeignKey('user.id') )
	sender = db.relationship(
		'User',
		foreign_keys=sender_id,
		backref=db.backref(
			'send_badges',
			lazy='joined'
		)
	)

	receiver_id = db.Column( db.Integer, db.ForeignKey('user.id') )
	receiver = db.relationship(
		'User',
		foreign_keys=receiver_id,
		backref=db.backref(
			'received_badges',
			lazy='joined'
		)
	)