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

TABLE_NAMES, COLLEGE_NAMES, COLUMN_NAMES = (), (), ()

app = Flask(__name__)

def init_server():
    """Call functions to get and store database info for input validation."""
    global TABLE_NAMES, COLLEGE_NAMES, COLUMN_NAMES
    TABLE_NAMES = _get_table_names()
    COLLEGE_NAMES = _get_college_names()
    COLUMN_NAMES = _get_column_names()

@app.route('/cscvis/api/v1.0/colleges', methods=['GET'])
def get_colleges():
    """GET method for all colleges.

    Returns:
        colleges: JSON list of college names sorted alphabetically.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('select instnm from College order by instnm')
    colleges = cur.fetchall()
    for index in range(len(colleges)):
        colleges[index] = colleges[index][0]
    return jsonify(colleges)

@app.route('/cscvis/api/v1.0/colleges/<path:college_name>', methods=['GET'])
def get_college(college_name):
    """GET method for specific college. Returns data across all years.

    Args:
        college_name: College name that matches Scorecard's INSTNM property.

    Returns:
        results: JSON dictionary of all data for the college formatted as:
            {"Table" : [value0, value1, value2...]}
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if college_name not in COLLEGE_NAMES:
        abort(404)
    try:
        cur.execute(
            'select college_id from College where INSTNM=?', (college_name,))
        college_id = str(cur.fetchone()[0])
    except:
        abort(404)

    results = {}
    for year_table in TABLE_NAMES:
        cur.execute(
            'select * from "%s" where college_id = ?' %
                (year_table,), (college_id,))
        results[year_table] = cur.fetchone()
    return jsonify(results)

@app.route('/cscvis/api/v1.0/colleges/<path:college_name>/<string:year>', methods=['GET'])
def get_college_year(college_name, year):
    """GET method for a college in a specific year.

    Args:
        college_name: College name that matches Scorecard's INSTNM property.
        year: Valid year of Scorecard data.

    Returns:
        data: JSON list of data for the year.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if college_name not in COLLEGE_NAMES:
        abort(404)
    if year not in TABLE_NAMES:
        abort(404)
    cur.execute(
        '''select * from "%s" inner join College on
        College.college_id = "%s".college_id where instnm = ?'''
        % (year, year), (college_name,))
    data = cur.fetchall()[0]
    return jsonify(data)

@app.route('/cscvis/api/v1.0/colleges/<path:college_name>/<string:year>/<string:data_type>', methods=['GET'])
def get_data_type(college_name, year, data_type):
    """GET method for a single data type for a college in a given year.

    Args:
        college_name: College name that matches Scorecard's INSTNM property.
        year: Valid year of Scorecard data.
        data_type: Data to return that matches the Scorecard property.

    Returns:
        data: JSON data for college_name's data_type in year.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if college_name not in COLLEGE_NAMES:
        abort(404)
    if year not in TABLE_NAMES:
        abort(404)
    if data_type not in COLUMN_NAMES:
        abort(404)
    cur.execute('''select %s from "%s" inner join College on
                College.college_id = "%s".college_id where instnm = ?'''
                % (data_type, year, year), (college_name,))
    data = cur.fetchall()[0]
    return jsonify(data)

def _get_table_names():
    """Retrieve table names from the database and store for input validation.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('select name from sqlite_master where type = "table"')
    tables = []
    for tup in cur.fetchall():
        if tup[0] not in 'sqlite_sequence':
            tables.append(tup[0])
    return tuple(tables)

def _get_college_names():
    """Retrieve college names from the database and store for input validation.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('select instnm from College')
    colleges = []
    for tup in cur.fetchall():
        colleges.append(tup[0])
    return tuple(colleges)

def _get_column_names():
    """Retrieve column names from the database and store for input validation.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    columns = []
    for table in TABLE_NAMES:
        cur.execute('PRAGMA table_info("%s")' % (table))
        for value in cur.fetchall():
            if value[1] not in columns:
                columns.append(value[1])
    return tuple(columns)

if __name__ == '__main__':
    init_server()
    app.run(debug=True)
