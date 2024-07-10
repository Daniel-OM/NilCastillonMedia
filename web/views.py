
import enum
import datetime as dt

import numpy as np
import pandas as pd

from http import HTTPStatus
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, flash, redirect, render_template, request, url_for, Response, send_from_directory
from flask_login import login_required, current_user
from .config import config, serializer
from .models import db
from .api import (ApiResponse, MasterAPI, UserAPI, ProjectAPI)

def formatDict(dic:dict) -> dict:
    
    for k, v in dic.items():
        if isinstance(v, dict):
            dic[k] = formatDict(dic=v)
        elif v == None:
            continue
        elif isinstance(v, dt.date) or isinstance(v, dt.datetime):
            dic[k] = v.strftime('%Y-%m-%d %H:%M')
        elif not isinstance(v, str) and not isinstance(v, float) and not isinstance(v, int):
            dic[k] = float(v)
        else:
            continue
            
    return dic

# checKey = lambda k, dic: dic[k] if k in dic else None
def checKey(k, dic):# -> Any | None:
    return dic[k] if k in dic else None

# entityToDict = lambda entity, hidden_fields: {k: v for k, v in entity.__dict__.items() if k not in hidden_fields}
def entityToDict(entity, hidden_fields:list=[]) -> dict:
    return {k: v for k, v in entity.__dict__.items() if k not in hidden_fields}
                                
def nanToNull(value: (int | float)) -> int | float | None:
    return value if value == value else None


user_api: UserAPI = UserAPI(db=db)
master_api: MasterAPI = MasterAPI(db=db)
project_api: ProjectAPI = ProjectAPI(db=db)


loged_views = Blueprint(name='loged_views', import_name=__name__)

@loged_views.route(rule='/register', methods=['GET', 'POST'])
def register() -> str | dict[str, (bool | str)]:
    
    if request.method == 'POST':
        response: ApiResponse = user_api.post(
            email=request.form['email'], 
            password=request.form['password'],
            first_name=request.form['name'],
            active=True
        )
        
        if response.executed:
            return {'executed':True, 'description': 'success', 'data':render_template(template_name_or_list='/user/login.html')}
            # return redirect(url_for('user_views.login'))
        else:
            return render_template(template_name_or_list='/layout.html', active='register_sidebar', modal=response.description)
    
    return {'executed':True, 'description': 'success', 
            'data':render_template(template_name_or_list='/user/register.html')}

@loged_views.route(rule='/login', methods=['GET', 'POST'])
def login() -> Response | str | dict[str, (bool | str)]:
    
    if request.method == 'POST':
        response: ApiResponse = user_api.login(email=request.form['email'], password=request.form['password'])
        if response.executed:
            return redirect(location=url_for(endpoint='main_views.dashboard')) # 'admin.index'
        elif response.status == ApiResponse.Status.SUCCESS:
            return render_template(template_name_or_list='/layout.html', active='login_sidebar', 
                                   modal='You couldn\'t login. Make sure you inserted the correct email and password.')
        
    return {'executed':True, 'description': 'success', 'data':render_template(template_name_or_list='/user/login.html')}

@loged_views.route(rule='/logout', methods=['GET', 'POST'])
@login_required
def logout() -> Response | dict[str, (bool | str)]:

    response: ApiResponse = user_api.logout()

    if response.executed:
        return redirect(location=url_for(endpoint='main_views.main'))
    else:
        print(response.description)
        # return redirect(url_for('main_views.dashboard'))
        return {'executed':False, 'description': 'error', 'data':render_template(template_name_or_list='/loged/loged_layout.html', 
                            modal=response.description)}

@loged_views.route(rule='/forgot-password', methods=['GET', 'POST'])
def forgot_password() -> dict[str, (bool | str)]:

    if request.method == 'POST':

        response: ApiResponse = user_api.userForgotPassword(email=request.form['email'])

        if response.executed:
            flash(message=response.description, category='success')
            return {'executed':True, 'description': 'success', 
                    'data':render_template(template_name_or_list='/user/login.html', modal=None)}
        elif response.status == ApiResponse.Status.SUCCESS:
            # return render_template('/user/forgot_password.html', modal=response.description)
            return {'executed':True, 'description': 'success', 
                    'data':render_template(template_name_or_list='/user/forgot_password.html', modal=response.description)}
    
    return {'executed':True, 'description': 'success', 
            'data':render_template(template_name_or_list='/user/forgot_password.html', modal=None)}

@loged_views.route(rule='/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token=None) -> Response | str:

    if request.method == 'POST':
        if request.form['password'] == request.form['repeat_password']:
            response: ApiResponse = user_api.userResetPassword(token=token, 
                                password=request.form['password'] if request.method == 'POST' else None)
            
            if response.executed:
                if current_user.is_authenticated:
                    return redirect(location=url_for(endpoint='main_views.dashboard'))
                else:
                    flash(message=response.description, category='success')
                    return redirect(location=url_for(endpoint='user_views.login'))
            else:
                return render_template(template_name_or_list='/user/reset_password.html', token=token, modal=response.description)
            
    return render_template(template_name_or_list='/user/reset_password.html', token=token)

@loged_views.route(rule="/detail", methods=['GET'])
@login_required
def user_detail() -> str:

    response: ApiResponse = user_api.getById(unwanted_keys=['_sa_instance_state', 'active', 'role_id'])
    print(response['data'])
    return response.to_dict()

@loged_views.route(rule="/edit", methods=["GET", "POST"])
@login_required
def user_edit() -> Response:
    
    data: dict = user_api.formToDict(form=request.form)
    print(data)
    response: ApiResponse = user_api.update(form=data)
    response: ApiResponse = user_api.getById(unwanted_keys=['_sa_instance_state', 'active', 'role_id'])
    
    return redirect(location=url_for(endpoint='main_views.dashboard'))

@loged_views.route(rule="/delete", methods=["GET", "POST"])
@login_required
def user_delete(forever:bool=False) -> dict:
    
    response: ApiResponse = user_api.delete(forever=forever)
    
    return response.to_dict()




main_views = Blueprint(name='main_views', import_name=__name__)

## UNLOGED ENDPOINTS --------------------------------------------------------------------------------------

@main_views.route(rule="/<path:filename>")
def templates(filename) -> str:
    print(send_from_directory(directory='templates', path=filename))
    return send_from_directory(directory='templates', path=filename)

@main_views.route(rule="/", methods=['GET', 'POST'])
def main() -> str:
    carousel: list[dict[str, (str | list[dict[str, str]] | dict[str, str])]] = [
        {'title': 'Project 1', 'description': 'Movie about fishes', 'media': [{'type':'img', 'src':'https://mdbcdn.b-cdn.net/img/new/slides/041.webp'}], 'thumbnail': {'type':'img', 'src':'https://mdbcdn.b-cdn.net/img/new/slides/041.webp'}},
        {'title': 'Project 2', 'description': 'Movie about fishes', 'media': [{'type':'img', 'src':'https://mdbcdn.b-cdn.net/img/new/slides/042.webp'}], 'thumbnail': {'type':'img', 'src':'https://mdbcdn.b-cdn.net/img/new/slides/042.webp'}},
        {'title': 'Project 3', 'description': 'Movie about fishes', 'media': [{'type':'img', 'src':'https://mdbcdn.b-cdn.net/img/new/slides/043.webp'}], 'thumbnail': {'type':'img', 'src':'https://mdbcdn.b-cdn.net/img/new/slides/043.webp'}},
    ]
    about: dict[str, str] = {
        'title': 'Who am I?',
        'subtitle': 'Nil Castillón Gasch',
        'description': """I'm a film producer and cinematographer who graduated from <a href="https://ecam.es/">ECAM</a> (School of 
						Cinematography and Audiovisual of the Community of Madrid). Since completing 
						my studies, I've had the privilege of working on a variety of exciting projects, 
						both as part of an established production company and as a freelancer. 
						</br>
						My career has been a blend of creative and challenging collaborations, where 
						I've had the opportunity to contribute to music videos for renowned artists 
						like C. Tangana, as well as commercials for major brands like Cupra. Each project 
						has allowed me to explore different styles and approaches, greatly enriching my 
						perspective and skills in the audiovisual industry.
						</br>
						One of my strengths is my ability to adapt to the needs and visions of my clients. 
						Whether capturing the energy and rhythm of a music video or conveying the essence 
						of a brand in a commercial, I always strive to deeply understand what each project 
						requires and bring my creativity and technical expertise to achieve exceptional results.
						</br>
						I'm here to help bring your vision to life. If you have an idea or a project in mind, 
						don't hesitate to get in touch with me. I'm excited about the possibility of working 
						together and creating something amazing!"""
    }
    services: dict[str, (str | list[dict[str, str]])] = {
        'title': 'Services.',
        'description': '''No two projects are the same, and I tailor my services to fit your specific 
							vision and requirements. My flexible approach ensures that I can handle any 
							challenge, whether it's a tight deadline, a limited budget, or a complex 
							concept. I work closely with you throughout the entire process, providing 
							personalized attention and expert guidance to achieve your goals.''',
        'services': [
            {'title': '01. Cinematographer', 
             'description': '''With a keen eye for detail and a passion for storytelling, I provide 
                            top-tier cinematography services that capture the essence of your 
                            project. From concept development to final cut, I ensure every 
                            frame is meticulously crafted to convey the desired emotion and 
                            message. Utilizing state-of-the-art equipment and the latest techniques, 
                            I deliver stunning visuals that leave a lasting impact.'''},
            {'title': '02. Producer', 
             'description': '''From pre-production planning to post-production editing, my video 
                            production services cover the entire filmmaking process. I specialize 
                            in creating high-quality content for a variety of purposes, including 
                            bringing intricate stories to the big screen with cinematic flair, 
                            enhancing brand image and communication with polished professional videos or 
                            creating visually dynamic and impactful videos that resonate with audiences.'''}
        ]
    }
    contact: dict[str, str] = {
        'title': "Let's bring your vision<br>to life.",
        'subtitle': 'Camara, lights and action.',
        'action_message': 'Your email address...',
        'action': 'Contact',
    }
    return render_template(template_name_or_list='layout.html', carousel=carousel, about=about, services=services, contact=contact)

@main_views.route(rule="/home", methods=['GET'])
def home() -> dict[str, (str | bool)]:
    return {'executed':True, 'description': 'success', 'data':render_template(template_name_or_list='/home.html')}

@main_views.route(rule="/services", methods=['GET'])
def services() -> dict[str, (str | bool)]:
    return {'executed':True, 'description': 'success', 'data':render_template(template_name_or_list='/services.html')}

@main_views.route(rule="/about", methods=['GET'])
def about() -> dict[str, (str | bool)]:
    return {'executed':True, 'description': 'success', 'data':render_template(template_name_or_list='home.html')}

            


## LOGED ENDPOINTS ----------------------------------------------------------------------------------------

@loged_views.route(rule="/dashboard", methods=['GET'])
@login_required
def dashboard() -> str:
    subscription: dict = user_api.getSubscription(unwanted_keys=['_sa_instance_state', 'active', 'role_id']).to_dict()
    return render_template(template_name_or_list='/loged/loged_layout.html', subscription=subscription)

@loged_views.route(rule="/home", methods=['GET'])
@login_required
def loged_home() -> dict[str, (str | bool)]:
    return {'executed':True, 'description': 'success', 'data':render_template(template_name_or_list='/loged/home.html')}

@loged_views.route(rule="/accounts/<int:account_class>", methods=['GET'])
@login_required
def loged_accounts(account_class:int) -> dict[dict]:

    user: ApiResponse = user_api.getById()
    countries: ApiResponse = master_api.Country(db=db).get()
    currencies: ApiResponse = master_api.Currency(db=db).get()
    account_types: ApiResponse = master_api.AccountType(db=db).getByAccountClass(id=account_class)
    
    responses: list = [user, countries, currencies, account_types]
    
    if any([r.status.value == ApiResponse.Status.ERROR.value for r in responses]):
        response: dict = {'executed':False, 'description': '\n'.join([r.description for r in responses \
                                                        if r.status.value == ApiResponse.Status.ERROR.value])}
    
    elif any([(not r.executed) for r in responses]):
        response: dict = {'executed':False, 'description': '\n'.join([r.description for r in responses \
                                                                        if not r.executed])}
        
    else:
        response: dict = {'executed':True, 'description': 'success'}
        
    return {**response, 
            **{'data':render_template(template_name_or_list='/loged/accounts.html', 
                user=user.data, countries=countries.data, currencies=currencies.data,
                data={'class': account_types.data['account_class'], 'types': account_types.data})}}

@loged_views.route(rule="/historic", methods=['GET'])
@login_required
def loged_historic() -> dict[str, (str | bool)]:
    return {'executed':True, 'description': 'success', 'data':render_template(template_name_or_list='/loged/historic.html')}

@loged_views.route(rule="/transactions", methods=['GET'])
@login_required
def transactions_list() -> dict[str, (str | bool)]:
    return {'executed':True, 'description': 'success', 'data':[]}

@loged_views.route(rule="/settings", methods=['GET'])
@login_required
def loged_settings() -> dict:
    details: ApiResponse = user_api.getById(unwanted_keys=['_sa_instance_state', 'active', 'role_id'])
    subscriptions: ApiResponse = master_api.getSubscriptions()
    print(details.to_dict())
    print(subscriptions.to_dict())
    return {'executed':True, 'description': 'success', 'data':render_template(template_name_or_list='/loged/settings.html', 
                            token=serializer.dumps(obj=current_user.email, salt='reset-password'),
                            details=details.data, subscriptions=subscriptions.data)}

@loged_views.route(rule="/add-capital", methods=['GET'])
def loged_add_capital() -> dict[str, (str | bool)]:
    return {'executed':True, 'description': 'success', 'data':render_template(template_name_or_list='/loged/home.html')}



            
