
import enum
import datetime as dt

from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, url_for
from flask_login import login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm import aliased

from .config import serializer
from .models import (db, migrate, User, ProjectRol, Language, MediaType, Project,
                     ProjectInfo, ProjectMedia, Config, ConfigInfo, Social)
from .email_send import EmailSender



'''
For pagination instead of .all() use:

.paginate(page=n, per_page=m)
Methods:
 - page: actual page
 - per_page: actual per page items
 - items: actual page items
 - total: total number of items across all pages
 - first: first item on page
 - last: last item on page
 - pages: total number of pages
 - has_prev: True if there is previous page
 - prev_num: Number of previous page
 - prev: Query the previous page
 - has_next: True if the is next page
 - next_num: Number of the next page
 - next: Query the next page
 
'''


# checKey = lambda k, dic: dic[k] if k in dic else None
def checKey(k, dic):
    return dic[k] if k in dic else None

def nanToNull(value: (int | float)) -> int | float | None:
    return value if value == value else None

def formatDict(dic:dict) -> dict:
    
    for k, v in dic.items():
        if isinstance(v, dict):
            dic[k] = formatDict(dic=v)
        elif v == None:
            continue
        elif isinstance(v, dt.date) or isinstance(v, dt.datetime):
            dic[k] = v.strftime(format='%Y-%m-%d %H:%M')
        elif not isinstance(v, str) and not isinstance(v, float) and not isinstance(v, int):
            dic[k] = float(v)
        else:
            continue
            
    return dic

# entityToDict = lambda entity, hidden_fields: {k: v for k, v in entity.__dict__.items() if k not in hidden_fields}
def entityToDict(entity, hidden_fields:list=[]) -> dict:
    return formatDict(dic={k: v for k, v in entity.__dict__.items() if k not in hidden_fields})

class ApiResponse:

    class Status(enum.Enum):
        SUCCESS: str = 'success'
        ERROR: str = 'error'

    def __init__(self, status:Status=Status.SUCCESS, executed:bool=True, description:str='',
                 data:(list | dict)= None) -> None:
        self.status: self.Status = status
        self.executed: bool = executed
        self.description: str = description
        self.data: list | dict = data

    def to_dict(self) -> dict:
        self.status: str = self.status.value
        return self.__dict__

class APITemplate:
    
    def __init__(self, db:SQLAlchemy) -> None:
        self.db: SQLAlchemy = db
    
    def formToDict(self, form) -> dict:
        
        '''
        form: ImmutableMultiDict
        '''
        
        return {k: v[0] if len(v) == 1 else v
                for k, v in form.to_dict(flat=False).items() \
                if v or v > 0 or len(v) > 0}
        
    def commit(self) -> None:
        self.db.session.commit()
      
class MasterAPI(APITemplate):
    
    class Rol(APITemplate):
    
        def __init__(self, db:SQLAlchemy) -> None:
            super().__init__(db=db)
        
        def get(self) -> ApiResponse:

            try:
                items: list[dict] = [entityToDict(entity=v, hidden_fields=['_sa_instance_state', 'active']) for v in \
                                    self.db.session.query(ProjectRol).filter(ProjectRol.active == True).all()]
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Rols obtained.',
                                                    data=items)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data=[])
            
            return response
        
        def getById(self, id:int) -> ApiResponse:

            try:
                item: dict = entityToDict(entity=self.db.session.query(ProjectRol).filter(ProjectRol.id == id).first(), 
                                          hidden_fields=['_sa_instance_state'])
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Rol obtained.',
                                                    data=item)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data={})
            
            return response
        
        def post(self, name:str, active:bool=True) -> ApiResponse:
            
            try:
                item: ProjectRol = ProjectRol(
                    name = name.lower(),
                    active = active)
                self.db.session.add(item)
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Rol registered.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response
        
        def update(self, id:int, form:dict={}, name:str=None, active:bool=None) -> ApiResponse:
            
            try:
                data: dict = form
                if name != None: data['name'] = name
                if active != None: data['active'] = active
            
                self.db.session.query(ProjectRol).filter(ProjectRol.id == id).update(data)
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Rol updated.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response
        
        def delete(self, id:int) -> ApiResponse:
            
            try:
                self.db.session.query(ProjectRol).filter(ProjectRol.id == id).update({'active': False})
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Rol deleted.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response

    class Language(APITemplate):
    
        def __init__(self, db:SQLAlchemy) -> None:
            super().__init__(db=db)
        
        def get(self) -> ApiResponse:

            try:
                items: list[dict] = [entityToDict(entity=v, hidden_fields=['_sa_instance_state', 'active']) for v in \
                                    self.db.session.query(Language).filter(Language.active == True).all()]
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Languages obtained.',
                                                    data=items)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data=[])
            
            return response
        
        def getById(self, id:int) -> ApiResponse:

            try:
                item: dict = entityToDict(entity=self.db.session.query(Language).filter(Language.id == id).first(), 
                                          hidden_fields=['_sa_instance_state'])
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Language obtained.',
                                                    data=item)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data={})
            
            return response
        
        def post(self, code:str, name:str, active:bool=True) -> ApiResponse:
            
            try:
                item: Language = Language(
                    code = code.lower(),
                    name = name.lower(),
                    active = active)
                self.db.session.add(item)
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Language registered.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response
        
        def update(self, id:int, form:dict={}, code:str=None, name:str=None, active:bool=None) -> ApiResponse:
            
            try:
                data: dict = form
                if code != None: data['code'] = code
                if name != None: data['name'] = name
                if active != None: data['active'] = active
            
                self.db.session.query(Language).filter(Language.id == id).update(data)
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Language updated.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response
        
        def delete(self, id:int) -> ApiResponse:
            
            try:
                self.db.session.query(Language).filter(Language.id == id).update({'active': False})
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Language deleted.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response

    class MediaType(APITemplate):
    
        def __init__(self, db:SQLAlchemy) -> None:
            super().__init__(db=db)
        
        def get(self) -> ApiResponse:

            try:
                items: list[dict] = [entityToDict(entity=v, hidden_fields=['_sa_instance_state', 'active']) for v in \
                                    self.db.session.query(MediaType).filter(MediaType.active == True).all()]
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='MediaTypes obtained.',
                                                    data=items)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data=[])
            
            return response
        
        def getById(self, id:int) -> ApiResponse:

            try:
                item: dict = entityToDict(entity=self.db.session.query(MediaType).filter(MediaType.id == id).first(), 
                                          hidden_fields=['_sa_instance_state'])
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='MediaType obtained.',
                                                    data=item)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data={})
            
            return response
        
        def post(self, name:str, description:str, active:bool=True) -> ApiResponse:
            
            try:
                item: MediaType = MediaType(
                    name = name.lower(),
                    description = description,
                    active = active)
                self.db.session.add(item)
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='MediaType registered.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response
        
        def update(self, id:int, form:dict={}, name:str=None, description:str=None, active:bool=None) -> ApiResponse:
            
            try:
                data: dict = form
                if name != None: data['name'] = name
                if description != None: data['description'] = description
                if active != None: data['active'] = active
            
                self.db.session.query(MediaType).filter(MediaType.id == id).update(data)
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='MediaType updated.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response
        
        def delete(self, id:int) -> ApiResponse:
            
            try:
                self.db.session.query(MediaType).filter(MediaType.id == id).update({'active': False})
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='MediaType deleted.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response

    class Config(APITemplate):
    
        def __init__(self, db:SQLAlchemy) -> None:
            super().__init__(db=db)
        
        def get(self) -> ApiResponse:

            try:
                items: list[dict] = [entityToDict(entity=v, hidden_fields=['_sa_instance_state', 'active']) for v in \
                                    self.db.session.query(Config).filter(Config.active == True).all()]
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Configs obtained.',
                                                    data=items)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data=[])
            
            return response
        
        def getById(self, id:int, language_id:str=None, complete:bool=True) -> ApiResponse:

            try:
                item: dict = entityToDict(entity=self.db.session.query(Config).filter(Config.id == id).first(), 
                                          hidden_fields=['_sa_instance_state'])
                
                if complete and language_id != None:
                    item: dict = {**item, 
                                  **entityToDict(entity=self.db.session.query(ConfigInfo).filter(ConfigInfo.config_id == item['id'], 
                                                                                                 ConfigInfo.language_id == language_id).first(), 
                                                hidden_fields=['_sa_instance_state'])}
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Config obtained.',
                                                    data=item)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data={})
            
            return response
        
        def post(self, html_id:str, name:str, active:bool=True) -> ApiResponse:
            
            try:
                item: Config = Config(
                    html_id = html_id,
                    name = name.lower(),
                    active = active)
                self.db.session.add(item)
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Config registered.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response
        
        def update(self, id:int, form:dict={}, html_id:str=None, name:str=None, active:bool=None) -> ApiResponse:
            
            try:
                data: dict = form
                if html_id != None: data['html_id'] = html_id
                if name != None: data['name'] = name
                if active != None: data['active'] = active
            
                self.db.session.query(Config).filter(Config.id == id).update(data)
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Config updated.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response
        
        def delete(self, id:int) -> ApiResponse:
            
            try:
                self.db.session.query(Config).filter(Config.id == id).update({'active': False})
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Config deleted.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response

    class ConfigInfo(APITemplate):
    
        def __init__(self, db:SQLAlchemy) -> None:
            super().__init__(db=db)
        
        def get(self) -> ApiResponse:

            try:
                items: list[dict] = [entityToDict(entity=v, hidden_fields=['_sa_instance_state', 'active']) for v in \
                                    self.db.session.query(ConfigInfo).filter(ConfigInfo.active == True).all()]
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='ConfigInfos obtained.',
                                                    data=items)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data=[])
            
            return response
        
        def getById(self, id:int) -> ApiResponse:

            try:
                item: dict = entityToDict(entity=self.db.session.query(ConfigInfo).filter(ConfigInfo.id == id).first(), 
                                          hidden_fields=['_sa_instance_state'])
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='ConfigInfo obtained.',
                                                    data=item)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data={})
            
            return response
        
        def getByConfigId(self, id:int, language_id:int) -> ApiResponse:

            try:
                item: dict = entityToDict(entity=self.db.session.query(ConfigInfo).filter(ConfigInfo.config_id == id, ConfigInfo.language_id == language_id).first(), 
                                          hidden_fields=['_sa_instance_state'])
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='ConfigInfo obtained.',
                                                    data=item)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data={})
            
            return response
        
        def post(self, config_id:int, language_id:int, data:str, active:bool=True) -> ApiResponse:
            
            try:
                item: ConfigInfo = ConfigInfo(
                    config_id = config_id,
                    language_id = language_id,
                    data = data,
                    active = active)
                self.db.session.add(item)
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='ConfigInfo registered.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response
        
        def update(self, id:int, form:dict={}, config_id:int=None, language_id:int=None, 
                   data:str=None, active:bool=None) -> ApiResponse:
            
            try:
                new_data: dict = form
                if config_id != None: new_data['config_id'] = config_id
                if language_id != None: new_data['language_id'] = language_id
                if data != None: new_data['data'] = data
                if active != None: new_data['active'] = active
            
                self.db.session.query(ConfigInfo).filter(ConfigInfo.id == id).update(new_data)
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='ConfigInfo updated.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response
        
        def delete(self, id:int) -> ApiResponse:
            
            try:
                self.db.session.query(ConfigInfo).filter(ConfigInfo.id == id).update({'active': False})
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='ConfigInfo deleted.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response

    class Social(APITemplate):
    
        def __init__(self, db:SQLAlchemy) -> None:
            super().__init__(db=db)
        
        def get(self) -> ApiResponse:

            try:
                items: list[dict] = [entityToDict(entity=v, hidden_fields=['_sa_instance_state', 'active']) for v in \
                                    self.db.session.query(Social).filter(Social.active == True).all()]
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Socials obtained.',
                                                    data=items)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data=[])
            
            return response
        
        def getById(self, id:int) -> ApiResponse:

            try:
                item: dict = entityToDict(entity=self.db.session.query(Social).filter(Social.id == id).first(), 
                                          hidden_fields=['_sa_instance_state'])
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Social obtained.',
                                                    data=item)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data={})
            
            return response
        
        def post(self, name:str, url:str, active:bool=True) -> ApiResponse:
            
            try:
                item: Social = Social(
                    name = name.lower(),
                    url = url,
                    active = active)
                self.db.session.add(item)
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Social registered.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response
        
        def update(self, id:int, form:dict={}, name:str=None, url:str=None, active:bool=None) -> ApiResponse:
            
            try:
                data: dict = form
                if name != None: data['name'] = name
                if url != None: data['url'] = url
                if active != None: data['active'] = active
            
                self.db.session.query(Social).filter(Social.id == id).update(data)
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Social updated.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response
        
        def delete(self, id:int) -> ApiResponse:
            
            try:
                self.db.session.query(Social).filter(Social.id == id).update({'active': False})
                self.commit()

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Social deleted.')    
                
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e)
            
            return response


class UserAPI(APITemplate):
    
    def __init__(self, db:SQLAlchemy) -> None:
        super().__init__(db=db)
                            
    def post(self, email:str, password:str, name:str=None, 
            active:bool=True) -> ApiResponse:
        
        try:
            new_user: User = User(
                name = name.capitalize(), 
                email = email.lower(), 
                password = generate_password_hash(password=password),
                active = active
            )
            self.db.session.add(new_user)
            self.commit()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='User registered.')    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
    
    def login(self, email:str, password:str) -> ApiResponse:
        
        try:
            user: User = self.db.session.query(User).filter(User.email == email.lower()).first()
            
            if user:
                if check_password_hash(pwhash=user.password, password=password):
                    login_user(user=user, remember=True)
                    response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='User logged.')
                else:
                    response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=False, description='Bad password.')   
            else:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=False, description='No user found.')    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
    
    def logout(self) -> ApiResponse:
        
        try:
            logout_user()
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='User logged out.')    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
    
    def get(self) -> ApiResponse:

        try:
            users: list[dict] = [entityToDict(entity=user, hidden_fields=['_sa_instance_state']) \
                    for user in self.db.session.query(User).order_by(User.id).all()]
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                            executed=True, description='Users list obtained.',
                                            data=users) 
             
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data=[])
        
        return response
    
    def getById(self, unwanted_keys:list=['_sa_instance_state']) -> ApiResponse:
        
        try:
            
            entity: User = entityToDict(entity=self.db.session.query(User).filter(User.id == current_user.id).first(),
                                        hidden_fields=unwanted_keys)
            
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='User details obtained.',
                                                data=entity)
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data={})
        
        return response
    
    def update(self, form:dict={}, email:str=None, password:str=None, name:str=None, 
               active:bool=None) -> ApiResponse:
        
        try:
            data: dict = form
            if name != None: data['name'] = name.capitalize()
            if email != None: data['email'] = email.capitalize()
            if password != None: data['password'] = generate_password_hash(password=password)
            if active != None: data['active'] = active

            
            self.db.session.query(User).filter(User.id == current_user.id).update(data)
            self.commit()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='User updated.',
                                                data=self.getById(unwanted_keys=current_user.id).data)    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=f'Your account couldn\'t be updated. Error:{e}',
                                                data={})
        
        return response
    
    def delete(self) -> ApiResponse:
        
        try:
            self.db.session.query(User).filter(User.id == current_user.id).update({'active': False})
            self.commit()

            self.logout()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description=f"Account deleted.")    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=f'Your account couldn\'t be deleted. Error:{e}')

        return response
    
    def forgotPassword(self, email:str) -> ApiResponse:
        
        try:
            # user: User = User.query.filter_by(email=email.lower()).first()
            user: User = self.db.session.query(User).filter(User.email == email.lower()).first()
            if user:
                token: str | bytes = serializer.dumps(obj=user.email, salt='reset-password')
                reset_link: str = url_for(endpoint='views.reset_password', token=token)

                es = EmailSender()
                es.login()
                es.send(message=f'Click the link to reset the password: {request.root_url}{reset_link}', 
                        subject='Omika Reset password', destinatary=[user.email], files=[])
                es.logout()
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Email sent with the password reset link.')  
            else:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=False, description='There is no user with that email.')
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
            
        return response
    
    def resetPassword(self, token:str=None, password:str=None) -> ApiResponse:

        try:
            if token != None:
                email = serializer.loads(s=token, salt='reset-password', max_age=3600)  # Token válido durante 1 hora
            elif current_user.is_authenticated:
                email = current_user.email
        except:
            return ApiResponse(status=ApiResponse.Status.SUCCESS, 
                            executed=False, description='The reset link is not valid or has expired.')  
            
        if password != None:
            try:
                self.db.session.query(User).filter(User.email == email).update({
                    'password': generate_password_hash(password=password)
                })
                self.commit()
                
                response: ApiResponse =  ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Password changed.')
            
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=f'Error changing the password. Try again. ({e})')

        else:
            response: ApiResponse =  ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=False, description=False)  
        
        return response


class ProjectAPI(APITemplate):
    
    def __init__(self, db:SQLAlchemy) -> None:
        super().__init__(db=db)
    
    def get(self) -> ApiResponse:

        try:
            items: list[dict] = [{**entityToDict(entity=v[0], hidden_fields=['_sa_instance_state']),
                                  **{'class': entityToDict(entity=v[1], hidden_fields=['_sa_instance_state']),
                                     'type': entityToDict(entity=v[2], hidden_fields=['_sa_instance_state']),
                                     'currency': entityToDict(entity=v[3], hidden_fields=['_sa_instance_state']),
                                     'country': entityToDict(entity=v[4], hidden_fields=['_sa_instance_state'])}} for v in \
                                    self.db.session.query(Project, AccountClass, AccountType, Currency, Country) \
                                    .join(UsersAccounts, UsersAccounts.account_id == Account.id) \
                                    .filter(UsersAccounts.user_id == current_user.id) \
                                    .join(AccountClass, AccountClass.id == Account.class_id) \
                                    .join(AccountType, AccountType.id == Account.type_id) \
                                    .join(Currency, Currency.id == Account.currency_id) \
                                    .join(Country, Country.id == Account.country_id).all()]
            
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                            executed=True, description='Accounts list obtained.',
                                            data=items) 
             
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data=[])
        
        return response
    
    def getById(self, id) -> ApiResponse:

        try:
            items: list[dict] = [{**entityToDict(entity=v[0], hidden_fields=['_sa_instance_state']),
                                  **{'class': entityToDict(entity=v[1], hidden_fields=['_sa_instance_state']),
                                     'type': entityToDict(entity=v[2], hidden_fields=['_sa_instance_state']),
                                     'currency': entityToDict(entity=v[3], hidden_fields=['_sa_instance_state']),
                                     'country': entityToDict(entity=v[4], hidden_fields=['_sa_instance_state'])}} for v in \
                                    self.db.session.query(Project, AccountClass, AccountType, Currency, Country) \
                                    .filter(Account.class_id == id) \
                                    .join(UsersAccounts, UsersAccounts.account_id == Account.id) \
                                    .filter(UsersAccounts.user_id == current_user.id) \
                                    .join(AccountClass, AccountClass.id == Account.class_id) \
                                    .join(AccountType, AccountType.id == Account.type_id) \
                                    .join(Currency, Currency.id == Account.currency_id) \
                                    .join(Country, Country.id == Account.country_id).all()]
            
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                            executed=True, description='Accounts list obtained.',
                                            data=items) 
             
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data=[])
        
        return response
    
    def getComplete(self) -> ApiResponse:

        try:
            
            items: list[dict] = [{**entityToDict(entity=v[1], hidden_fields=['_sa_instance_state']),
                            **{'isowner': v[0],
                               'creator': entityToDict(entity=v[2], hidden_fields=['_sa_instance_state']),
                               'type': entityToDict(entity=v[3], hidden_fields=['_sa_instance_state']),
                               'class': entityToDict(entity=v[4], hidden_fields=['_sa_instance_state']),
                               'currency': entityToDict(entity=v[5], hidden_fields=['_sa_instance_state']),
                               'country': entityToDict(entity=v[6], hidden_fields=['_sa_instance_state'])}} \
                                for v in self.db.session.query(UsersAccounts.owner, Account, User, 
                                                          AccountType, AccountClass, Currency, Country) \
                                    .filter(UsersAccounts.user_id == current_user.id) \
                                    .join(Account, Account.id == UsersAccounts.account_id) \
                                    .join(User, User.id == Account.creator_id) \
                                    .join(AccountType, AccountType.id == Account.type_id) \
                                    .join(AccountClass, AccountClass.id == Account.class_id) \
                                    .join(Currency, Currency.id == Account.currency_id) \
                                    .join(Country, Country.id == Account.country_id) \
                                    .all()]
            items: list[dict] = [{**item, 
                                  **{'owner': entityToDict(entity=self.db.session.query(User) \
                                      .join(UsersAccounts, UsersAccounts.user_id == User.id) \
                                      .filter((UsersAccounts.account_id == item['id']) & (UsersAccounts.owner == True)), 
                                    hidden_fields=['_sa_instance_state'])}} for item in items]
            
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                            executed=True, description='Accounts list obtained.',
                                            data=items) 
             
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data=[])
        
        return response
    
    def getById(self, id:int) -> ApiResponse:

        try:
            v: tuple[bool, Account, User, AccountType, AccountClass, Currency, Country] = \
                self.db.session.query(UsersAccounts.owner, Account, User, AccountType, AccountClass, Currency, Country) \
                    .filter(UsersAccounts.user_id == current_user.id, UsersAccounts.account_id == id) \
                    .join(Account, Account.id == UsersAccounts.account_id) \
                    .join(User, User.id == Account.creator_id) \
                    .join(AccountType, AccountType.id == Account.type_id) \
                    .join(AccountClass, AccountClass.id == Account.class_id) \
                    .join(Currency, Currency.id == Account.currency_id) \
                    .join(Country, Country.id == Account.country_id) \
                    .first()
            owner: User = self.db.session.query(User) \
                            .join(UsersAccounts, UsersAccounts.user_id == User.id) \
                            .filter((UsersAccounts.account_id == v[1].id) & (UsersAccounts.owner == True)).first()
            item: dict = {**entityToDict(entity=v[1], hidden_fields=['_sa_instance_state']),
                            **{'isowner': v[0],
                               'creator': entityToDict(entity=v[2], hidden_fields=['_sa_instance_state']),
                               'type': entityToDict(entity=v[3], hidden_fields=['_sa_instance_state', 'password']),
                               'class': entityToDict(entity=v[4], hidden_fields=['_sa_instance_state']),
                               'currency': entityToDict(entity=v[5], hidden_fields=['_sa_instance_state']),
                               'country': entityToDict(entity=v[6], hidden_fields=['_sa_instance_state']),
                               'owner': entityToDict(entity=owner, hidden_fields=['_sa_instance_state', 'password'])}}
            
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                            executed=True, description='Account obtained.',
                                            data=item) 
             
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data={})
        
        return response

    def post(self, name:str, custom_id:str, description:str, entity:str, type_id:int, 
             class_id:int, country_id:int, currency_id:int, start_amount:float=0.0) -> ApiResponse:
        
        try:
            item: Account = Account(
                name = name.lower(), 
                custom_id = custom_id, 
                description = description, 
                entity = entity,
                creator_id = current_user.id,
                type_id = type_id,
                class_id = class_id,
                start_amount = start_amount,
                current_amount = start_amount,
                country_id = country_id,
                currency_id = currency_id, 
                active = True
            )
            self.db.session.add(item)
            self.db.session.flush()
            self.db.session.add(
                UsersAccounts(
                    user_id = current_user.id, 
                    account_id = item.id, 
                    owner = True,
                    active = True
                )
            )
            
            self.commit()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='Account registered.',
                                                data=self.getById(id=item.id).data)
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data={})
        
        return response
    
    def update(self, id:int, form:dict={}, name:str=None, custom_id:str=None, description:str=None, 
               entity:str=None, type_id:int=None, class_id:int=None, start_amount:float=None, 
               country_id:int=None, currency_id:int=None, current_amount:float=None, 
               active:bool=None) -> ApiResponse:
        
        try:
            data: dict = form
            if name != None: data['name'] = name
            if custom_id != None: data['custom_id'] = custom_id
            if description != None: data['description'] = description
            if entity != None: data['entity'] = entity
            if type_id != None: data['type_id'] = type_id
            if class_id != None: data['class_id'] = class_id
            if start_amount != None: data['start_amount'] = start_amount
            if current_amount != None: data['current_amount'] = current_amount
            if country_id != None: data['country_id'] = country_id
            if currency_id != None: data['currency_id'] = currency_id
            if active != None: data['active'] = active
        
            self.db.session.query(Account).filter(Account.id == id).update(data)
            self.commit()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='Account updated.',
                                                data=self.getById(id=id).data)    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data={})
        
        return response
    
    def delete(self, id:int) -> ApiResponse:
        
        try:
            self.db.session.query(Account).filter(Account.id == id).update({'active': False})
            self.commit()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='Account deleted.')    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
