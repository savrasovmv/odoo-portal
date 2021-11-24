# -*- coding: utf-8 -*-
from odoo import http, api
from odoo.http import request
from odoo.addons.website.controllers.main import Website
import werkzeug.utils
import base64
import json

class AdBook(http.Controller):
    

    # Контроллер СПРАВОЧНИК КОНТАКТОВ ВЕБ-САЙТ

    @http.route(['/wadbook','/wadbook/<int:department_id>'], type='http', auth="user", website=True, sitemap=True)
    def index1(self, department_id=False, **kw):

        def _get_dep(obj_dep, parent_id, rows_department):
            search = obj_dep.search([
                            ('parent_id', '=', parent_id)
                        ], order="sequence asc")
            for line in search:
                rows_department.append(line)
                _get_dep(obj_dep, line.id, rows_department)

        
        branch_list = http.request.env['adbook.department'].sudo().search([
                                ('parent_id', '=', False)
                            ], order="sequence asc")
        
        rows_department = branch_list
        # rows_department = []
        # obj_dep = http.request.env['adbook.department'].sudo()
        # _get_dep(obj_dep, False, rows_department)

        employer_list = []
        current_department_name = ''

        if department_id:
            is_homepage = False
            employer_list = http.request.env['adbook.employer'].sudo().search([
                                    ('is_view_adbook', '=', True),
                                    ('department_id', '=', department_id),
                                ], order="sequence asc")
            current_department = http.request.env['adbook.department'].sudo().browse([department_id])
            branch_id = current_department.branch_id
            current_department_name = current_department.adbook_name
        else:
            is_homepage = True
        
        if len(rows_department) == 0:
            return "Нет ниодного подразделения для отображения в справочнике. Установите хотя бы для одного объекта Подразделения AD 'Отображать в справочнике контктов'"

               
        if not department_id:
            branch_id = False

        # import random
        # #Generate 5 random numbers between 10 and 30
        # randomlist = []
        # if len(employer_list)>0:
        #     randomlist = random.sample(range(0, 5), len(employer_list)+1)

            
        return http.request.render('website_adbook.website_index', {
            'search': False,
            'is_homepage': is_homepage,
            'current_branch_id': branch_id,
            'current_department_name': current_department_name,
            # 'branch_list':  branch_list,
            'department_list':  rows_department,
            'employer_list':  employer_list,
            # 'randomlist': randomlist,
        })


    @http.route(['/wadbook/search'], type='http', auth="user", website=True, sitemap=True)
    def wsearch(self, search=False, **kw):

        if not search or search=='':
            return http.request.redirect('/wadbook')

        
        branch_list = http.request.env['adbook.branch'].sudo().search([
                            ], order="sequence asc")

        department_list = http.request.env['adbook.department'].sudo().search([ 
                                                    ], 
                                                        order="sequence asc"
                                                    )

        limit = 50
        employer_list = http.request.env['adbook.employer'].sudo().search([
                            ('search_text', '=ilike', search+'%'),
                            ('active', '=', True),
                            ('is_view_adbook', '=', True),
                            ('branch_id', 'in', branch_list.ids),
                        ], order="name asc", limit=limit)
        
        limit2 = limit - len(employer_list)
        employer_list += http.request.env['adbook.employer'].sudo().search([
                            ('search_text', 'ilike', search),
                            ('id', 'not in', employer_list.ids),
                            ('active', '=', True),
                            ('is_view_adbook', '=', True),
                            ('branch_id', 'in', branch_list.ids),
                        ], order="name asc", limit=limit2)

                    
        
        if not branch_list:
            return "Нет ниодного подразделения для отображения в справочнике. Установите хотя бы для одного объекта Подразделения AD 'Отображать в справочнике контктов'"
            
        return http.request.render('website_adbook.website_index', {
            'search': True,
            'search_text': search,
            'is_limit': True if limit == len(employer_list) else False,
            'is_homepage': False,
            'current_branch_id': False,
            'current_department_name': False,
            'branch_list':  branch_list,
            'department_list':  department_list,
            'employer_list':  employer_list,
        })

    @http.route(['/wadbook/get_employer/<int:department_id>'], type='json', auth="user", website=True, sitemap=True)
    def get_employer(self, department_id=False,**kw):
        if department_id:
            is_homepage = False
            employers = http.request.env['adbook.employer'].sudo().search([
                                    ('is_view_adbook', '=', True),
                                    ('department_id', '=', department_id),
                                ], order="sequence asc")
            current_department = http.request.env['adbook.department'].sudo().browse([department_id])
            branch_id = current_department.branch_id
            current_department_name = current_department.adbook_name

            employer_list = []
            for line in employers:
                employer_list.append({
                    'name': line.name,
                    'title': line.title,
                    'departpent_name': line.branch_id.adbook_name + ' - ' + line.department_id.adbook_name,
                    'ip_phone': line.ip_phone,
                    'phone': line.phone,
                    'sec_phone': line.sec_phone,
                    'email': line.email,
                    'photo': line.photo,
                    'service_status': line.service_status,
                    'service_status_start_date': line.service_status_start_date.strftime("%d.%m.%Y") if line.service_status_start_date else '',
                    'service_status_end_date': line.service_status_end_date.strftime("%d.%m.%Y") if line.service_status_end_date else '',

                })
        else:
            is_homepage = True
        return  {
            'current_branch_name': branch_id.adbook_name,
            'current_department_name': current_department_name,
            'employer_list':  employer_list,
            'is_limited': False,

            # 'employer_list':  json.dumps(employer_list) if employer_list else False ,
        }

    @http.route(['/wadbook/search_employer/<string:search>'], type='json', auth="user", website=True, sitemap=True)
    def search_employer(self, search=False,**kw):
        # print('+++++++++++++', search)
        if not search or search=='':
            return http.request.redirect('/wadbook')
        
        limit = 50
        employers = http.request.env['adbook.employer'].sudo().search([
                            ('search_text', '=ilike', search+'%'),
                            ('active', '=', True),
                            ('is_view_adbook', '=', True),
                        ], order="name asc", limit=limit)
        
        limit2 = limit - len(employers)
        employers += http.request.env['adbook.employer'].sudo().search([
                            ('search_text', 'ilike', search),
                            ('id', 'not in', employers.ids),
                            ('active', '=', True),
                            ('is_view_adbook', '=', True),
                        ], order="name asc", limit=limit2)

        employer_list = []
        for line in employers:
            employer_list.append({
                'name': line.name,
                'title': line.title,
                'departpent_name': line.branch_id.adbook_name + ' - ' + line.department_id.adbook_name,
                'ip_phone': line.ip_phone,
                'phone': line.phone,
                'sec_phone': line.sec_phone,
                'email': line.email,
                'photo': line.photo,
                'service_status': line.service_status,
                'service_status_start_date': line.service_status_start_date.strftime("%d.%m.%Y") if line.service_status_start_date else '',
                'service_status_end_date': line.service_status_end_date.strftime("%d.%m.%Y") if line.service_status_end_date else '',
            })

        is_limited = False

        if len(employer_list) == limit:
            is_limited = True
        
        
        return  {
            'current_branch_name': False,
            'current_department_name': False,
            'employer_list':  employer_list if len(employer_list)>0 else False,
            'search_text': search,
            'is_limited': is_limited,
            # 'employer_list':  json.dumps(employer_list) if employer_list else False ,
        }
 

    