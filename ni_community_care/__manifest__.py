#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Community Care",
    "version": "16.0.0.2.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient", "ni_service", "ni_condition"],
    "data": [
        "datas/ni_condition_class_data.xml",
        "datas/ir_sequence_data.xml",
        "security/ir.model.access.csv",
        "security/ir_rules_data.xml",
        "views/ni_service_views.xml",
        "views/ni_patient_views.xml",
        "views/ni_cc_report_monthly.xml",
        "views/ni_community_care_menu.xml",
        "views/ni_service_event_view.xml",
    ],
    "application": True,
    "auto_install": False,
    "installable": True,
}
