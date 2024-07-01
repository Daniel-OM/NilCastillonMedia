
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    
class UserAdmin(AdminModelView):
    column_list: tuple[str] = ('name', 'email', 'password', 'active')
    column_labels: dict[str, str] = {'name': 'Name', 'email': 'Email', 'password': 'Password', 
                                     'active': 'Active'}
    column_filters: tuple[str] = ('name', 'email', 'password', 'active')
    
class LanguageAdmin(AdminModelView):
    column_list: tuple[str] = ('code', 'name', 'active')
    column_labels: dict[str, str] = {'code': 'Code', 'name': 'Name', 'active': 'Active'}
    column_filters: tuple[str] = ('code', 'name', 'active')

class ProjectRolAdmin(AdminModelView):
    column_list: tuple[str] = ('active',)
    column_labels: dict[str, str] = {'active': 'Active'}
    column_filters: tuple[str] = ('active',)

class ProjectRolInfoAdmin(AdminModelView):
    column_list: tuple[str] = ('rol_fk', 'language_fk', 'name', 'active')
    column_labels: dict[str, str] = {'rol_fk': 'Rol', 'language_fk':'Language', 'name': 'Name', 
                                     'active': 'Active'}
    column_filters: tuple[str] = ('rol_fk.id', 'language_fk.name', 'name', 'active')
    
class MediaTypeAdmin(AdminModelView):
    column_list: tuple[str] = ('active',)
    column_labels: dict[str, str] = {'active': 'Active'}
    column_filters: tuple[str] = ('active',)
    
class MediaTypeInfoAdmin(AdminModelView):
    column_list: tuple[str] = ('type_fk', 'language_fk', 'name', 'description', 'active')
    column_labels: dict[str, str] = {'type_fk': 'Media Type', 'language_fk': 'Language', 'name': 'Name', 
                                     'description': 'Description', 'active': 'Active'}
    column_filters: tuple[str] = ('type_fk.id', 'language_fk.name', 'name', 'description', 'active')
    
class ProjectAdmin(AdminModelView):
    column_list: tuple[str] = ('rol_fk', 'active')
    column_labels: dict[str, str] = {'rol_fk': 'Rol', 'active':'Active'}
    column_filters: tuple[str] = ('rol_fk.id', 'active')
    
class ProjectInfoAdmin(AdminModelView):
    column_list: tuple[str] = ('project_fk', 'language_fk', 'name', 'description', 'active')
    column_labels: dict[str, str] = {'project_fk': 'Project', 'language_fk': 'Language', 'name': 'Name', 
                                     'description': 'Description', 'active': 'Active'}
    column_filters: tuple[str] = ('project_fk.id', 'language_fk.name', 'name', 'description', 'active')
    
class ProjectMediaAdmin(AdminModelView):
    column_list: tuple[str] = ('project_fk', 'type_fk', 'path', 'active')
    column_labels: dict[str, str] = {'project_fk': 'Project', 'type_fk': 'Type', 'path': 'Path', 'active':'Active'}
    column_filters: tuple[str] = ('project_fk.id', 'type_fk.id', 'path', 'active')
    
    
class ConfigAdmin(AdminModelView):
    column_list: tuple[str] = ('html_id', 'name', 'active')
    column_labels: dict[str, str] = {'html_id': 'HTML id', 'name': 'Name', 'active': 'Active'}
    column_filters: tuple[str] = ('html_id', 'name', 'active')
    
class ConfigInfoAdmin(AdminModelView):
    column_list: tuple[str] = ('config_fk', 'language_fk', 'data', 'active')
    column_labels: dict[str, str] = {'config_fk': 'Config', 'language_fk': 'Language', 'data': 'Data', 'active': 'Active'}
    column_filters: tuple[str] = ('config_fk.name', 'language_fk.name', 'data', 'active')

class SocialAdmin(AdminModelView):
    column_list: tuple[str] = ('name', 'url', 'active')
    column_labels: dict[str, str] = {'name': 'Name', 'url': 'URL', 'active': 'Active'}
    column_filters: tuple[str] = ('name', 'url', 'active')
