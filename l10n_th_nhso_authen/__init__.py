#  Copyright (c) 2023 NSTDA

from . import models
import platform
import json

from odoo import api, SUPERUSER_ID


def setup_config_param(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    config = env["ir.config_parameter"].sudo()

    base_url = "https://pucws.nhso.go.th"
    config.set_param("nsho_authen.base_url", base_url)

    header = {
        "Content-Type": "application/json",
        "User-Agent": "Nirun/16.0 ({}) Odoo/16.0".format(platform.platform()),
    }
    config.set_param("nhso_authen.header", json.dumps(header, indent=4))

    mock_data = {
        "statusAuthen": True,
        "statusMessage": "พบข้อมูลการ authen",
        "personalId": "14799XXXXXXX6",
        "firstName": "อัมพร",
        "lastName": "จาเพียญราชา",
        "fullName": "อัมพร จาเพียญราชา",
        "sex": "ชาย",
        "age": "44 ปี 7 เดือน 8 วัน",
        "nationCode": "099",
        "nationDescription": "ไทย",
        "provinceCode": "4700",
        "provinceName": "สกลนคร",
        "mainInscl": "UCS",
        "mainInsclName": "สิทธิหลักประกันสุขภาพแห่งชาติ",
        "subInscl": "89",
        "subInsclName": "ช่วงอายุ 12-59 ปี",
        "serviceHistories": [
            {
                "hcode": "13814",
                "hname": "รพ.ศิริราช",
                "serviceDate": "2023-10-06T15:16:38",
                "claimCode": "PP1015363237",
                "serviceCode": "PG0150001",
                "serviceName": "คัดกรองโควิดแบบ Antigen",
            },
            {
                "hcode": "13814",
                "hname": "รพ.ศิริราช",
                "serviceDate": "2021-12-20T16:50:57",
                "claimCode": "PP1015363259",
                "serviceCode": "PG0010066",
                "serviceName": "คัดกรองโควิดแบบ RTPCR",
            },
        ],
    }
    config.set_param("nhso_authen.mock_data", json.dumps(mock_data, indent=4))
