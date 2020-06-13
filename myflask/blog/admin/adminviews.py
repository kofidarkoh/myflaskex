import flask_admin as admin
from flask import Blueprint
from blog.dbmodels import User,Article,Article_Likes,AdminUser
from flask_admin.contrib.peewee import ModelView
from flask_wtf import FlaskForm
from blog.dbforms import LoginForms
from flask_admin import expose,BaseView,AdminIndexView



class AdminIndex(AdminIndexView):
	@expose('/')
	def adminview(self):
		form = LoginForms()
		print(form)
		return self.render('admin/index.html',form = form)

admin = admin.Admin(name='hello',template_mode='bootstrap3', index_view=AdminIndex())
