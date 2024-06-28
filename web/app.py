
from flask import Flask
from flask_admin import Admin

from .views import main_views, loged_views
from .login import login_manager
from .config import config
from .models import (db, migrate, User, ProjectRol, Language, MediaType, Project,
                     ProjectInfo, ProjectMedia, Config, ConfigInfo, Social)
from .adminviews import (UserAdmin, ProjectRolAdmin, LanguageAdmin, MediaTypeAdmin, 
                         ProjectAdmin, ProjectInfoAdmin, ProjectMediaAdmin, ConfigAdmin, 
                         ConfigInfoAdmin, SocialAdmin)

# Create App
application: Flask = Flask(import_name=__name__, instance_relative_config=True)
application.config.from_mapping(mapping=config)
application.jinja_env.auto_reload = True



def has_no_empty_params(rule) -> bool:
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

from flask import url_for
@main_views.route(rule="/site-map")
def site_map() -> list:
    links: list = []
    for rule in application.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule=rule):
            url: str = url_for(endpoint=rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    
    return links
            
application.register_blueprint(blueprint=main_views, url_prefix='/')
application.register_blueprint(blueprint=loged_views, url_prefix='/loged')


login_manager.init_app(app=application)
db.init_app(app=application)
migrate.init_app(app=application, db=db)

# with application.app_context():
#     db.create_all()
#     db.session.commit()

admin: Admin = Admin(app=application, name='Admin Panel', template_mode='bootstrap4')
admin.add_view(view=UserAdmin(model=User, session=db.session))
admin.add_view(view=ProjectRolAdmin(model=ProjectRol, session=db.session))
admin.add_view(view=LanguageAdmin(model=Language, session=db.session))
admin.add_view(view=MediaTypeAdmin(model=MediaType, session=db.session))
admin.add_view(view=ProjectAdmin(model=Project, session=db.session))
admin.add_view(view=ProjectInfoAdmin(model=ProjectInfo, session=db.session))
admin.add_view(view=ProjectMediaAdmin(model=ProjectMedia, session=db.session))
admin.add_view(view=ConfigAdmin(model=Config, session=db.session))
admin.add_view(view=ConfigInfoAdmin(model=ConfigInfo, session=db.session))
admin.add_view(view=SocialAdmin(model=Social, session=db.session))


if __name__ == '__main__':
    
    # db.create_all()

    # Print SQL in command window
    db.engine.echo = True
    application.config['SQLALCHEMY_ECHO'] = True

    application.run(port=5000, debug=True)


    '''
    To create the database you must open the flask shell in the terminal:
    >> flask shell

    And execute the initialization
    >> app.app_context().push()

    >> from app import db, Role, Station, User, Vehicle, Tank
    >> db.create_all()

    The db.create_all() function does not recreate or update a table if it 
    already exists. For example, if you modify your model by adding a new column, 
    and run the db.create_all() function, the change you make to the model will 
    not be applied to the table if the table already exists in the database. The 
    solution is to delete all existing database tables with the db.drop_all() 
    function and then recreate them with the db.create_all() function like so:
    >> db.drop_all()
    >> db.create_all()

    Sin estar en la shell de flask:
    
    To create migration file:
    >> flask db init

    To make a migration:
    >> flask db migrate -m "Initial migration."
    >> flask db upgrade 
    '''
