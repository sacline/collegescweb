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

db_path = os.getcwd() + '/data/database/college-scorecard.sqlite'
app = Flask(__name__)

@app.route('/cscvis/api/v1.0/colleges', methods=['GET'])
def get_colleges():
    """GET method for all colleges.

    Returns:
        colleges: JSON list of college names sorted alphabetically.
    """
    conn = sqlite3.connect(db_path)
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
        college_data: JSON list of all data for the college formatted as a
            dictionary: {"Table" : [value0, value1, value2...]}
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute(
            'select college_id from College where INSTNM=?', (college_name,))
        college_id = str(cur.fetchone()[0])
    except:
        abort(404)

    cur.execute('select name from sqlite_master where type = "table"')
    valid_tables = []
    for table_name in cur.fetchall():
        if table_name[0] in 'sqlite_sequence':
            continue
        valid_tables.append(table_name[0])

    results = {}
    for year_table in valid_tables:
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
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        '''select * from "%s" inner join College on
        College.college_id = "%s".college_id where instnm = ?'''
        % (year, year), (college_name,))
    return jsonify(cur.fetchall()[0])

if __name__ == '__main__':
    app.run(debug=True)
