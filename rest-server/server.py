"""
server.py
Copyright (C) <2017>  <S. Cline>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import sqlite3
from flask import Flask, abort, jsonify

DB_PATH = os.getcwd() + '/data/database/college-scorecard.sqlite'

COLLEGE_NAMES, COLLEGE_IDS, YEAR_NAMES, DATA_TYPE_NAMES = (), (), (), ()

app = Flask(__name__)

def init_server():
    """Call functions to get and store database info for input validation."""
    global YEAR_NAMES, COLLEGE_NAMES, COLLEGE_IDS, DATA_TYPE_NAMES
    YEAR_NAMES = _get_year_names()
    COLLEGE_NAMES = _get_college_names()
    COLLEGE_IDS = _get_college_ids()
    DATA_TYPE_NAMES = _get_data_type_names()

def valid_inputs(college=None, college_id=None, year=None, data_type=None):
    """Validate any inputs to the API passed through the URI.

    Args:
        college: Name of the college passed through the URI.
        college_id: College id passed through the URI.
        year: Name of the year passed through the URI.
        data_type: Name of the data_type passed through the URI.

    Returns:
        boolean: True if inputs match the database, false if they do not.
    """
    if college is not None and college not in COLLEGE_NAMES:
        return False
    if college_id is not None and college_id not in COLLEGE_IDS:
        return False
    if year is not None and year not in YEAR_NAMES:
        return False
    if data_type is not None and data_type not in DATA_TYPE_NAMES:
        return False
    return True

@app.route('/cscvis/api/v2.0/data/colleges', methods=['GET'])
def get_all_colleges():
    """GET method for all colleges.

    Returns:
        colleges: JSON array of objects containing college ids and their names.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('select college_id, instnm from College order by instnm')
    colleges = []
    for result in cur.fetchall():
        colleges.append({'id':result[0], 'name':result[1]})
    conn.close()
    return jsonify({'college':colleges})

@app.route('/cscvis/api/v2.0/data/colleges/<int:college_id>', methods=['GET'])
def get_college(college_id):
    """GET method for specific college. Returns all global and year data.

    Args:
        college_id: College id.

    Returns:
        data: JSON object containing objects representing year and global data
            for the college.
    """
    min_year = min(int(year) for year in YEAR_NAMES)
    max_year = max(int(year) for year in YEAR_NAMES)
    year_data = get_college_years(college_id, str(min_year), str(max_year), json=False)
    global_data = get_college_global(college_id, json=False)
    data = year_data.copy()
    data.update(global_data)
    return jsonify(data)

@app.route('/cscvis/api/v2.0/data/colleges/<int:college_id>/global', methods=['GET'])
def get_college_global(college_id, json=True):
    """GET method for global (non-year-specific) college data.

    Args:
        college_id: College id.

    Returns:
        global_data: JSON object containing the global college data.
    """
    if not valid_inputs(college_id=college_id):
        abort(404)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('PRAGMA table_info(%s)' % ('College'))
    college_global_data_types = cur.fetchall()

    cur.execute('''select * from College where college_id = ?''', (college_id,))
    global_data = {}
    for data_type, value in zip(college_global_data_types, cur.fetchone()):
        if value is None:
            continue
        global_data[data_type[1]] = value
    conn.close()
    if json is False:
        return {'global':global_data}
    return jsonify({'global':global_data})

@app.route('/cscvis/api/v2.0/data/colleges/<int:college_id>/year/<string:min_year>', methods=['GET'])
@app.route('/cscvis/api/v2.0/data/colleges/<int:college_id>/year&min=<string:min_year>&max=<string:max_year>', methods=['GET'])
def get_college_years(college_id, min_year, max_year=None, json=True):
    """GET method for a college in a specific year.

    A single year or range of years may be specified.

    Args:
        college_id: College id.
        min_year: First year of Scorecard data to return.
        max_year: Last year of Scorecard data to return.

    Returns:
        all_data: JSON object containing objects of college data over the year
            range.
    """
    if max_year is None:
        max_year = min_year
    if int(min_year) > int(max_year):
        abort(404)
    if not valid_inputs(college_id=college_id, year=min_year):
        abort(404)
    if not valid_inputs(year=max_year):
        abort(404)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    all_data = {}
    for year in range(int(min_year), int(max_year)+1):
        cur.execute(
            '''select * from "%s" where college_id = ?'''
            % (year), (college_id,))
        year_data = {}
        query_result = cur.fetchone()
        if query_result is None:
            continue
        for data_type, result in zip(DATA_TYPE_NAMES, query_result):
            if result is None:
                continue
            year_data[data_type] = result
        all_data[str(year)] = year_data

    conn.close()

    if json is False:
        return all_data
    else:
        return jsonify(all_data)

@app.route('/cscvis/api/v2.0/data/data_types', methods=['GET'])
def get_data_types():
    """GET method for all data types.

    Returns:
        data_types: JSON object containing an array of objects containing the
            data types name, their type, and scope.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    year = min(year for year in YEAR_NAMES)
    cur.execute('PRAGMA table_info("%s")' % (year))
    year_data_types = cur.fetchall()
    cur.execute('PRAGMA table_info(College)')
    global_data_types = cur.fetchall()
    data_types = []
    for result in year_data_types:
        data_types.append({'name':result[1], 'type':result[2], 'scope':'year'})
    for result in global_data_types:
        data_types.append(
            {'name':result[1], 'type':result[2], 'scope':'global'})
    return jsonify({'data_type':data_types})

@app.route('/cscvis/api/v2.0/data/data_types/<path:data_type>/year&min=<string:min_year>&max=<string:max_year>', methods=['GET'])
@app.route('/cscvis/api/v2.0/data/data_types/<path:data_type>/year/<string:min_year>', methods=['GET'])
def get_data_type_year(data_type, min_year, max_year=None):
    """GET method for values of a data type over a year or range of years.

    Args:
        data_type: Data type for which values will be returned.
        min_year: First year of Scorecard data to return.
        max_year: Last year of Scorecard data to return.

    Returns:
        values: JSON object containing arrays of objects for each year, with
            each object containing the college_id and data value.
    """
    if max_year is None:
        max_year = min_year
    if int(min_year) > int(max_year):
        abort(404)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if not valid_inputs(year=min_year, data_type=data_type):
        abort(404)
    if not valid_inputs(year=max_year):
        abort(404)

    all_data = {}
    for year in range(int(min_year), int(max_year)+1):
        cur.execute(
            '''select %s, college_id from "%s" where %s is not null'''
            % (data_type, year, data_type))
        query_result = cur.fetchall()
        if query_result is None:
            continue
        year_data = []
        for college_value in query_result:
            year_data.append({'college_id':college_value[1], 'value':college_value[0]})
        all_data[str(year)] = year_data
    conn.close()
    return jsonify(all_data)

@app.route('/cscvis/api/v2.0/data/data_types/<path:data_type>/global', methods=['GET'])
def get_data_type_global(data_type):
    """GET method for values of a global data type.

    Args:
        data_type: Global data type for which values will be returned.

    Returns:
        values: JSON object containing objects with the college_id and data
            value.
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if not valid_inputs(data_type=data_type):
        print(data_type, 'invalid')
        abort(404)

    all_data = {}
    cur.execute(
        '''select %s, college_id from College where %s is not null'''
        % (data_type, data_type))
    query_result = cur.fetchall()
    global_data = []
    for college_value in query_result:
        global_data.append({'college_id':college_value[1], 'value':college_value[0]})
    conn.close()
    print(all_data)
    return jsonify({'Global':global_data})

def _get_year_names():
    """Retrieve year table names and store for input validation.

    Returns:
        years: Tuple of string year table names from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('select name from sqlite_master where type = "table"')
    years = []
    for tup in cur.fetchall():
        if tup[0] not in ['sqlite_sequence', 'College']:
            years.append(tup[0])
    conn.close()
    return tuple(years)

def _get_college_names():
    """Retrieve college names from the database and store for input validation.

    Returns:
        colleges: Tuple of string college names from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('select instnm from College')
    colleges = []
    for tup in cur.fetchall():
        colleges.append(tup[0])
    conn.close()
    return tuple(colleges)

def _get_college_ids():
    """Retrieve college ids from the database and store for input validation.

    Returns:
        college_ids: Tuple of string college ids from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('select college_id from College')
    college_ids = []
    for tup in cur.fetchall():
        college_ids.append(tup[0])
    conn.close()
    return tuple(college_ids)

def _get_data_type_names():
    """Retrieve data_types from the database and store for input validation.

    Returns:
        data_types: Tuple of string data_type names from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data_types = []

    cur.execute('PRAGMA table_info(College)')
    for value in cur.fetchall():
        if value[1] not in data_types:
            data_types.append(value[1])

    for year in YEAR_NAMES:
        cur.execute('PRAGMA table_info("%s")' % (year))
        for value in cur.fetchall():
            if value[1] not in data_types:
                data_types.append(value[1])
        break;

    conn.close()
    print(data_types)
    return tuple(data_types)

if __name__ == '__main__':
    init_server()
    app.run(debug=False)
