
import enum
import datetime as dt

from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, url_for
from flask_login import login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm import aliased

from .config import serializer
from .models import (db, migrate, User, Language, ProjectRol, ProjectRolInfo, 
                     MediaType, MediaTypeInfo, Project, ProjectInfo, ProjectMedia, 
                     Config, ConfigInfo, Social)
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
    
    def __init__(self, db:SQLAlchemy, language:str='es') -> None:
        self.db: SQLAlchemy = db
        self.language: str = language
    
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

    class Language(APITemplate):
    
        def __init__(self, db:SQLAlchemy, language:str='es') -> None:
            super().__init__(db=db, language=language)
        
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
        
        def getByCode(self, code:int) -> ApiResponse:

            try:
                item: dict = entityToDict(entity=self.db.session.query(Language).filter(Language.code == code).first(), 
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
    
    class Rol(APITemplate):
    
        def __init__(self, db:SQLAlchemy, language:str='es') -> None:
            super().__init__(db=db, language=language)
            self.language_id: (int | None) = MasterAPI(db=db, language=language).Language(db=db, language=language).getByCode(code=language).data.get('id', None)
        
        def get(self) -> ApiResponse:

            try:
                items: list[dict] = [{**entityToDict(entity=v[0], hidden_fields=['_sa_instance_state']), 
                                      **{'info': entityToDict(entity=v[1], hidden_fields=['_sa_instance_state'])}} for v in \
                                    self.db.session.query(ProjectRol, ProjectRolInfo).filter(ProjectRol.active == True) \
                                        .join(ProjectRolInfo, (ProjectRolInfo.rol_id == ProjectRol.id) & \
                                                              (ProjectRolInfo.language_id == self.language_id)).all()]
                
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
                items: tuple[ProjectRol, ProjectRolInfo] = self.db.session.query(ProjectRol, ProjectRolInfo).filter(ProjectRol.id == id) \
                                             .join(ProjectRolInfo, (ProjectRolInfo.rol_id == ProjectRol.id) & \
                                                              (ProjectRolInfo.language_id == self.language_id)).first()
                item: dict = {**entityToDict(entity=items[0], hidden_fields=['_sa_instance_state']),
                              **{'info': entityToDict(entity=items[1], hidden_fields=['_sa_instance_state'])}}
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Rol obtained.',
                                                    data=item)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data={})
            
            return response
        
        def post(self, rol_id:int, language_id:int, name:str, active:bool=True) -> ApiResponse:
            
            try:
                rol_id: (int | None) = self.getById(rol_id).data.get('id', None)
                if rol_id == None:
                    rol: ProjectRol = ProjectRol(
                        active = active)
                    self.db.session.add(rol)
                    self.db.session.flush()
                    rol_id: int = rol.id

                item: ProjectRolInfo = ProjectRolInfo(
                    rol_id = rol_id,
                    language_id = language_id,
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
        
        def update(self, id:int, language_id:int, form:dict={}, name:str=None, active:bool=None) -> ApiResponse:
            
            try:
                data: dict = form
                if name != None: data['name'] = name
                if active != None: data['active'] = active
            
                self.db.session.query(ProjectRolInfo).filter((ProjectRolInfo.rol_id == id) & (ProjectRolInfo.language_id == language_id)).update(data)
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
        
    class MediaType(APITemplate):
    
        def __init__(self, db:SQLAlchemy, language:str='es') -> None:
            super().__init__(db=db, language=language)
            self.language_id: (int | None) = MasterAPI(db=db, language=language).Language(db=db, language=language).getByCode(code=language).data.get('id', None)
        
        def get(self) -> ApiResponse:

            try:
                items: list[dict] = [{**entityToDict(entity=v[0], hidden_fields=['_sa_instance_state']), 
                                      **{'info': entityToDict(entity=v[1], hidden_fields=['_sa_instance_state'])}} for v in \
                                    self.db.session.query(MediaType, MediaTypeInfo).filter(MediaType.active == True) \
                                        .join(MediaTypeInfo, (MediaTypeInfo.type_id == MediaType.id) & \
                                                              (MediaTypeInfo.language_id == self.language_id)).all()]
                
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
                items: tuple[MediaType, MediaTypeInfo] = self.db.session.query(MediaType, MediaTypeInfo).filter(MediaType.id == id) \
                                             .join(MediaTypeInfo, (MediaTypeInfo.type_id == MediaType.id) & \
                                                              (MediaTypeInfo.language_id == self.language_id)).first()
                item: dict = {**entityToDict(entity=items[0], hidden_fields=['_sa_instance_state']),
                              **{'info': entityToDict(entity=items[1], hidden_fields=['_sa_instance_state'])}}
                
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='MediaType obtained.',
                                                    data=item)
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=e,
                                                    data={})
            
            return response

        def post(self, type_id:int, language_id:int, name:str, description:str, active:bool=True) -> ApiResponse:
            
            try:
                type_id: (int | None) = self.getById(type_id).data.get('id', None)
                if type_id == None:
                    m_type: MediaType = MediaType(
                        active = active)
                    self.db.session.add(m_type)
                    self.db.session.flush()
                    type_id: int = m_type.id

                item: MediaTypeInfo = MediaTypeInfo(
                    type_id = type_id,
                    language_id = language_id,
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
        
        def update(self, id:int, language_id:int, form:dict={}, name:str=None, description:str=None, active:bool=None) -> ApiResponse:
            
            try:
                data: dict = form
                if name != None: data['name'] = name
                if description != None: data['description'] = description
                if active != None: data['active'] = active
            
                self.db.session.query(MediaTypeInfo).filter((MediaTypeInfo.type_id == id) & (MediaTypeInfo.language_id == language_id)).update(data)
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
    
        def __init__(self, db:SQLAlchemy, language:str='es') -> None:
            super().__init__(db=db, language=language)
            self.language_id: (int | None) = MasterAPI(db=db, language=language).Language(db=db, language=language).getByCode(code=language).data.get('id', None)
        
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
    
        def __init__(self, db:SQLAlchemy, language:str='es') -> None:
            super().__init__(db=db, language=language)
            self.language_id: (int | None) = MasterAPI(db=db, language=language).Language(db=db, language=language).getByCode(code=language).data.get('id', None)
        
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
    
        def __init__(self, db:SQLAlchemy, language:str='es') -> None:
            super().__init__(db=db, language=language)
            self.language_id: (int | None) = MasterAPI(db=db, language=language).Language(db=db, language=language).getByCode(code=language).data.get('id', None)
        
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

    def __init__(self, db:SQLAlchemy, language:str='es') -> None:
        super().__init__(db=db, language=language)
        self.language_id: (int | None) = MasterAPI(db=db, language=language).Language(db=db, language=language).getByCode(code=language).data.get('id', None)
                            
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
    
    def __init__(self, db:SQLAlchemy, language:str='es') -> None:
        super().__init__(db=db, language=language)
        self.language_id: (int | None) = MasterAPI(db=db, language=language).Language(db=db, language=language).getByCode(code=language).data.get('id', None)
    
    def get(self) -> ApiResponse:

        try:
            items: list[dict] = [{**entityToDict(entity=v[0], hidden_fields=['_sa_instance_state']),
                                  **{'info': entityToDict(entity=v[1], hidden_fields=['_sa_instance_state'])}} for v in \
                                    self.db.session.query(Project, ProjectInfo) \
                                    .join(ProjectInfo, (ProjectInfo.project_id == Project.id) & (ProjectInfo.language_id == self.language_id)).all()]
            for item in items:
                item['rol'] = MasterAPI(db=self.db, language=self.language).Rol(db=self.db, language=self.language).getById(id=item['rol_id']).data
                item['media'] = self.getProjectMedia(project_id=item['id']).data
            
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                            executed=True, description='Projects list obtained.',
                                            data=items) 
             
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data=[])
        
        return response
    
    def getById(self, id) -> ApiResponse:

        try:
            item: tuple[Project, ProjectInfo] = self.db.session.query(Project, ProjectInfo).filter(Project.id == id) \
                            .join(ProjectInfo, (ProjectInfo.project_id == Project.id) & (ProjectInfo.language_id == self.language_id)).first()
            item: dict = {**entityToDict(entity=item[0], hidden_fields=['_sa_instance_state']), 
                          **{'info': entityToDict(entity=item[1], hidden_fields=['_sa_instance_state'])}}
            item['rol'] = MasterAPI(db=self.db, language=self.language).Rol(db=self.db, language=self.language).getById(id=item['rol_id']).data
            item['media'] = self.getProjectMedia(project_id=item['id']).data
            
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                            executed=True, description='Project obtained.',
                                            data=item) 
             
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data={})
        
        return response
    
    def getProjectMedia(self, project_id:int) -> ApiResponse:

        try:
            items: list[dict] = [{**entityToDict(entity=v, hidden_fields=['_sa_instance_state']),
                                  **{'type': MasterAPI(db=self.db, language=self.language) \
                                            .MediaType(db=self.db, language=self.language) \
                                            .getById(id=v.type_id)}} for v in \
                                    self.db.session.query(ProjectMedia).filter(ProjectMedia.project_id == project_id).all()]
            
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                            executed=True, description='Projject Media list obtained.',
                                            data=items) 
             
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data=[])
        
        return response

    def post(self, project_id:int, rol_id:int, language_id:int, name:str, description:str) -> ApiResponse:
        
        try:
            project_id: (int | None) = self.getById(id=project_id).data.get('id', None)
            if project_id == None:
                project: Project = Project(
                    rol_id = rol_id,
                    active = True
                )
                self.db.session.add(project)
                self.db.session.flush()
                project_id: int = project.id
            
            item: ProjectInfo = ProjectInfo(
                project_id = project_id,
                language_id = language_id,
                name = name.lower(),
                description = description,
                active = True
            )
            self.db.session.add(item)
            
            self.commit()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='Project registered.',
                                                data=self.getById(id=item.id).data)
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data={})
        
        return response
    
    def update(self, id:int, language_id:int, form:dict={}, rol_id:int=None, name:str=None, description:str=None,
               active:bool=None) -> ApiResponse:
        
        try:
            data: dict = form
            if name != None: data['name'] = name
            if description != None: data['description'] = description
            if active != None: data['active'] = active

            if rol_id != None:
                self.db.session.query(Project).filter(Project.id == id).update({'rol_id': rol_id})

            self.db.session.query(ProjectInfo).filter((ProjectInfo.project_id == id) & (ProjectInfo.language_id == language_id)).update(data)
            self.commit()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='Project updated.',
                                                data=self.getById(id=id).data)    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data={})
        
        return response
    
    def delete(self, id:int) -> ApiResponse:
        
        try:
            self.db.session.query(Project).filter(Project.id == id).update({'active': False})
            self.commit()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='Project deleted.')    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
