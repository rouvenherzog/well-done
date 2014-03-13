from flask import render_template, request, redirect, url_for, session
from ext.sys.database import db
from flask.ext.security import login_required
from flask_security.core import current_user
from models.models import User, Badge
from json import loads
from random import choice

praises = [
	"Well done",
	"Awesome",
	"Amazing",
	"Incredible",
	"Nice"
]

def register_views( project ):
	@project.route('/')
	def index():
		return render_template(
			'index.html'
		)

	@project.route('/dashboard')
	@login_required
	def dashboard():
		messages = 'flash' in session and session['flash'] or []
		session['flash'] = []
		return render_template(
			'dashboard.html',
			other_users = User.query.filter( User.email != current_user.email ).all(),
			messages = messages,
			news = Badge.get_news(),
			praise = choice(praises)
		)

	@project.route('/give-badge', methods=["POST"])
	@login_required
	def give_badge():
		receiver = User.query.get(request.form.get('receiver'))
		if receiver:
			title = request.form.get('title')
			badge = Badge()
			badge.title = title
			badge.sender = current_user
			badge.receiver = receiver

			db.session.add(badge)
			db.session.commit()

			session['flash'] = {
				"success": ["You gave {0} a badge.".format( receiver.name )]
			}
		else:
			session['flash'] = {
				"failure": ["Don't lie to me! That user does not even exist."]
			}

		return redirect(request.referrer)

	@project.route('/user/<int:user_id>')
	@login_required
	def show_user( user_id ):
		messages = 'flash' in session and session['flash'] or []
		session['flash'] = []

		user = User.query.get( user_id )
		if user:
			return render_template(
				'user.html',
				user = user,
				messages = messages
			)
		else :
			return render_template(
				'errors/404.html'
			)

	@project.route('/badge/<int:badge_id>/agree')
	@login_required
	def agree_badge( badge_id ):
		badge = Badge.query.get( badge_id )
		if badge:
			if badge.sender != current_user and badge.receiver != current_user:
				if current_user in badge.agreeing:
					badge.agreeing.remove( current_user )
				else:
					badge.agreeing.append( current_user )

				db.session.add( badge )
				db.session.commit()

				session['flash'] = {
					"success": ["You {0}.".format("agree" if current_user in badge.agreeing else "disagree")]
				}
				return redirect( request.referrer )
			else:
				session['flash'] = {
					"failure": ["Don't fool me. You received or send this badge."]
				}
				return redirect( request.referrer )
		else:
			session['flash'] = {
				"failure": ["Naah. This badge doesn't even exist."]
			}
			return redirect( request.referrer )