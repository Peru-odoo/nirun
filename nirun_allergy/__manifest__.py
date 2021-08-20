#  Copyright (c) 2021 Piruin P.

{
    "name": "Allergy & Intolerance",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient", "nirun_medication"],
    "data": [
        "security/ir.model.access.csv",
        "views/patient_views.xml",
        "views/allergy_views.xml",
        "views/allergy_code_views.xml",
        "views/allergy_menu.xml",
    ],
    "demo": [],
    "application": False,
    "auto_install": False,
    "installable": True,
}