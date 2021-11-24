# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Сотрудники доп поля adbook",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Savrasov Mikhail <savrasovmv@tmenergo.ru> ",
    "website": "https://github.com/savrasovmv/",
    "category": "Human Resources",
    "summary": "Дополнительные поля ",
    "depends": ["hr", "ad_base"],
    "data": [
        "views/hr_employee.xml",
        "views/hr_invitation_mail_templates.xml",
        "views/hr_department.xml",
        "views/res_country.xml",
        "views/res_company.xml",
        "views/hr_personal_doc.xml",
        "views/hr_menu.xml",
        'security/ir.model.access.csv',

        ],
    "installable": True,
}
