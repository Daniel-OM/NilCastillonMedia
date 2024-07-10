
import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_migrate import Migrate

db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.id} ({self.name})>'
    
class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<Language {self.name}>'
    
class ProjectRol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<ProjectRol {self.id}>'
    
class ProjectRolInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rol_id = db.Column(db.Integer, db.ForeignKey(ProjectRol.id), nullable=False)
    rol_fk = db.relationship(ProjectRol, backref=db.backref('rol_info_rel', lazy=True))
    language_id = db.Column(db.Integer, db.ForeignKey(Language.id), nullable=False)
    language_fk = db.relationship(Language, backref=db.backref('language_rol_rel', lazy=True))
    name = db.Column(db.String(80), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<ProjectRolInfo {self.name}>'
    
class MediaType(db.Model):
    '''Company or Person'''
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<MediaType {self.name}>'
    
class MediaTypeInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey(MediaType.id), nullable=False)
    type_fk = db.relationship(MediaType, backref=db.backref('type_info_rel', lazy=True))
    language_id = db.Column(db.Integer, db.ForeignKey(Language.id), nullable=False)
    language_fk = db.relationship(Language, backref=db.backref('language_type_rel', lazy=True))
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(500), unique=False, nullable=True)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<MediaTypeInfo {self.name}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rol_id = db.Column(db.Integer, db.ForeignKey(ProjectRol.id), nullable=False)
    rol_fk = db.relationship(ProjectRol, backref=db.backref('rol_project_rel', lazy=True))
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<Project {self.id}>'

class ProjectInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey(Project.id), nullable=False)
    project_fk = db.relationship(Project, backref=db.backref('project_info_rel', lazy=True))
    language_id = db.Column(db.Integer, db.ForeignKey(Language.id), nullable=False)
    language_fk = db.relationship(Language, backref=db.backref('language_info_rel', lazy=True))
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(500), unique=False, nullable=True)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<ProjectInfo {self.project_id} - {self.language_id}>'

class ProjectMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey(Project.id), nullable=False)
    project_fk = db.relationship(Project, backref=db.backref('project_media_rel', lazy=True))
    type_id = db.Column(db.Integer, db.ForeignKey(MediaType.id), nullable=False)
    type_fk = db.relationship(MediaType, backref=db.backref('type_media_rel', lazy=True))
    path = db.Column(db.String(500), unique=False, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<ProjectMedia {self.project_id} - {self.path}>'


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    html_id = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<Config {self.name}>'
    
class ConfigInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey(Config.id), nullable=False)
    config_fk = db.relationship(Config, backref=db.backref('config_info_rel', lazy=True))
    language_id = db.Column(db.Integer, db.ForeignKey(Language.id), nullable=False)
    language_fk = db.relationship(Language, backref=db.backref('language_config_rel', lazy=True))
    data = db.Column(db.String(1000), unique=False, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<ConfigInfo {self.name}>'



class Social(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    url = db.Column(db.String(1000), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<Social {self.name}>'