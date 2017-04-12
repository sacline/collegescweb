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

table_names, college_names, column_names = [], [], []

app = Flask(__name__)

def init_server():
    """Call functions to get and store database info for input validation."""
    global table_names, college_names, column_names
    table_names = _get_table_names()
    college_names = _get_college_names()
    column_names = _get_column_names()

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
    if college_name not in college_names:
        abort(404)
    try:
        cur.execute(
            'select college_id from College where INSTNM=?', (college_name,))
        college_id = str(cur.fetchone()[0])
    except:
        abort(404)

    results = {}
    for year_table in table_names:
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
    if college_name not in college_names:
        abort(404)
    if year not in table_names:
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
    if college_name not in college_names:
        abort(404)
    if year not in table_names:
        abort(404)
    if data_type not in column_names:
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
    table_names = []
    for tup in cur.fetchall():
        if tup[0] not in 'sqlite_sequence':
            table_names.append(tup[0])
    return table_names

def _get_college_names():
    """Retrieve college names from the database and store for input validation.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('select instnm from College')
    college_names = []
    for tup in cur.fetchall():
        college_names.append(tup[0])
    return college_names

def _get_column_names():
    """Retrieve column names from the database and store for input validation.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    column_names = []
    for table in table_names:
        cur.execute('PRAGMA table_info("%s")' % (table))
        for value in cur.fetchall():
            if value[1] not in column_names:
                column_names.append(value[1])
    return column_names

if __name__ == '__main__':
    init_server()
    app.run(debug=True)
