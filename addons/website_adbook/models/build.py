from odoo import fields, models, api
from datetime import datetime

class AdbookBuild(models.AbstractModel):
    _name = 'adbook.build'
    _description = 'Создание/обновления справочника контактов'

    def adbook_build(self, full_sync=False):
        date_update = datetime.now()
        
       
        ad_ou_list = self.env['ad.ou'].sudo().search([
                                ('active', '=', True),
                                ('is_view_adbook', '=', True),
                            ])
        for ad_ou in ad_ou_list:
            search_dep = self.env['adbook.department'].sudo().search([
                            ('ad_ou_id', '=', ad_ou.id),
                        ],limit=1)
            
            if len(search_dep)>0:
                dep_id = search_dep
                dep_vals = {
                    'name': ad_ou.name,
                    'ad_ou_id': ad_ou.id,
                    'level': 0,
                    'date_update': date_update,
                }
                search_dep.write(dep_vals)
            else:
                dep_vals = {
                    'name': ad_ou.name,
                    'adbook_name': ad_ou.name,
                    'ad_ou_id': ad_ou.id,
                    'level': 0,
                    'date_update': date_update,
                }
                dep_id = self.env['adbook.department'].sudo().create(dep_vals)
      


        # СОТРУДНИКИ

        ad_users_list = self.env['ad.users'].sudo().search([
                                ('active', '=', True),
                                ('is_view_adbook', '=', True),
                                ('ou_id', 'in', ad_ou_list.ids),
                            ])
        ad_users_list += self.env['ad.users'].sudo().search([
                                ('active', '=', False),
                                ('is_view_adbook', '=', True),
                                ('is_view_disabled_adbook', '=', True),
                                ('ou_id', 'in', ad_ou_list.ids),
                            ])
        adbook_emloyer = self.env['adbook.employer'].sudo()
        for user in ad_users_list:

            is_fired = False
            search_emloyer = adbook_emloyer.search([
                                ('ad_users_id', '=', user.id),
                            ])
            hr_vals = {}

            if user.employee_id:
                hr_employer = user.employee_id
                hr_vals = {
                    'hr_employee_id': hr_employer.id,
                    'title': hr_employer.job_title,
                }
                is_fired = hr_employer.is_fired
            
                # Добавить поиск по документам Отпус и прочее
            
            # Выссшее подразделение 
            department_branch_id = self.env['adbook.department'].sudo().search([
                                ('ad_ou_id', '=', user.ou_id.id),
                            ], limit=1)
            if len(department_branch_id)>0:
                b_vals = {
                    'branch_id': department_branch_id.id
                }


            ad_vals = {
                'name': user.name,
                'title': user.title,
                'ip_phone': user.ip_phone,
                'phone': user.phone,
                'sec_phone': user.sec_phone,
                'email': user.email,
                'photo': user.photo,
                'ad_users_id': user.id,
                'date_update': date_update,
            }

            vals = {**ad_vals, **hr_vals, **b_vals}
            if not is_fired:
                if search_emloyer:
                    search_emloyer.write(vals)
                else:
                    search_emloyer.create(vals)


        # Удаляем записи которые небыли обновлены
        adbook_emloyer.search([
                                ('date_update', '<', date_update),
                                ('ad_users_id', '!=', ''),
                            ]).unlink()

        
        adbook_emloyer_list = adbook_emloyer.search([])
        department_list_ids = [] # Список актуальных записей, родителей которых нужно обновить
        for employer in adbook_emloyer_list:
            if employer.hr_employee_id:
                if employer.hr_employee_id.department_id:
                    search_dep = self.env['adbook.department'].sudo().search([
                                    ('hr_department_id', '=', employer.hr_employee_id.department_id.id),
                                ],limit=1)
                    
                    if len(search_dep)>0:
                        dep_id = search_dep
                        dep_vals = {
                            'name': employer.hr_employee_id.department_id.name,
                            'hr_department_id': employer.hr_employee_id.department_id.id,
                            'branch_id': employer.branch_id.id,
                            'is_records': True,
                            'date_update': date_update,

                        }
                        search_dep.write(dep_vals)
                    else:
                        dep_vals = {
                            'name': employer.hr_employee_id.department_id.name,
                            'adbook_name': employer.hr_employee_id.department_id.name,
                            'hr_department_id': employer.hr_employee_id.department_id.id,
                            'branch_id': employer.branch_id.id,
                            'is_records': True,
                            'date_update': date_update,

                        }
                        dep_id = self.env['adbook.department'].sudo().create(dep_vals)
                    
                    employer.department_id = dep_id.id
                    department_list_ids.append(dep_id.id)
                else:
                    search_dep = self.env['adbook.department'].sudo().search([
                                ('is_default', '=', True),
                            ],limit=1)
                    if len(search_dep)>0:
                        employer.department_id = search_dep.id

                # Статус сотрудника
                employer.service_status = employer.hr_employee_id.service_status
                employer.service_status_start_date = employer.hr_employee_id.service_status_start_date
                employer.service_status_end_date = employer.hr_employee_id.service_status_end_date

            elif employer.ad_users_id and not employer.is_manual:
                search_dep = []
                if employer.ad_users_id.department_id:
                    search_dep = self.env['adbook.department'].sudo().search([
                                    ('ad_department_id', '=', employer.ad_users_id.department_id.id),
                                ],limit=1)
                
                    
                    if len(search_dep)>0:
                        dep_id = search_dep
                        dep_vals = {
                            'name': employer.ad_users_id.department_id.name,
                            'ad_department_id': employer.ad_users_id.department_id.id,
                            'branch_id': employer.branch_id.id,
                            'is_records': True,
                            'date_update': date_update,

                        }
                        
                        search_dep.write(dep_vals)
                    else:
                        dep_vals = {
                            'name': employer.ad_users_id.department_id.name,
                            'adbook_name': employer.ad_users_id.department_id.name,
                            'ad_department_id': employer.ad_users_id.department_id.id,
                            'branch_id': employer.branch_id.id,
                            'is_records': True,
                            'date_update': date_update,

                        }
                        print(dep_vals)
                        dep_id = self.env['adbook.department'].sudo().create(dep_vals)
                    
                    employer.department_id = dep_id.id
                    department_list_ids.append(dep_id.id)
                else:
                    search_dep = self.env['adbook.department'].sudo().search([
                                ('is_default', '=', True),
                            ],limit=1)
                    if len(search_dep)>0:
                        employer.department_id = search_dep.id


        
        # Обновляем родителей
        # dep_list = self.env['adbook.department'].sudo().browse(hr_department_list_ids)
        dep_list = self.env['adbook.department'].sudo().search([
                                    ('id', 'in', department_list_ids),
                                ])
        for dep in dep_list:
            if not dep.hr_department_id:
                dep.parent_id = dep.branch_id.id
                continue
            
            hr_parent_id = dep.hr_department_id.parent_id
            i = 1
            while hr_parent_id:
                if i==1:
                    current_dep = dep
                
                if hr_parent_id.is_view_adbook:
                    search_dep = self.env['adbook.department'].sudo().search([
                                    ('hr_department_id', '=', hr_parent_id.id),
                                ],limit=1)
                    
                    if len(search_dep)>0:
                        dep_id = search_dep
                        dep_vals = {
                            'name': hr_parent_id.name,
                            'hr_department_id': hr_parent_id.id,
                            'branch_id': dep.branch_id.id,
                            'date_update': date_update,

                        }
                        search_dep.write(dep_vals)

                    else:
                        dep_vals = {
                            'name': hr_parent_id.name,
                            'adbook_name': hr_parent_id.name,
                            'hr_department_id': hr_parent_id.id,
                            'branch_id': dep.branch_id.id,
                            'date_update': date_update,

                        }
                        dep_id = self.env['adbook.department'].sudo().create(dep_vals)
                    
                    
                    current_dep.parent_id = dep_id.id
                    hr_parent_id = hr_parent_id.parent_id
                    i+=1
                    current_dep = dep_id
                else:
                    current_dep.parent_id =  dep.branch_id.id
                    break
            
            current_dep.parent_id =  dep.branch_id.id

        # Удаляем записи которые небыли обновлены
        self.env['adbook.department'].sudo().search([
                                ('date_update', '<', date_update),
                                '|','|',
                                ('hr_department_id', '!=', ''),
                                ('ad_department_id', '!=', ''),
                                ('ad_ou_id', '!=', ''),
                            ]).unlink()

        
        
        # НАЗНАЧЕНИЯ УРОВНЯ ОТДЕЛАМ
        dep_list = self.env['adbook.department'].sudo().search([])
        for dep in dep_list:
            level = 0
            dep_parent = dep.parent_id
            while dep_parent:
                level += 1
                dep_parent = dep_parent.parent_id

            dep.level = level

        
        return True