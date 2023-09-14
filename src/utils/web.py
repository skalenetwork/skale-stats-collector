#   -*- coding: utf-8 -*-
#
#   This file is part of skale-stats-collector
#
#   Copyright (C) 2023 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
from http import HTTPStatus
from flask import Response


def construct_response(status, data, pretty=False):
    response_data = json.dumps(data, indent=4) if pretty else json.dumps(data)
    return Response(
        response=response_data,
        status=status,
        mimetype='application/json'
    )


def construct_ok_response(data=None, pretty=False):
    if data is None:
        data = {}
    return construct_response(HTTPStatus.OK, {'status': 'ok', 'payload': data}, pretty)
