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
from flask import Flask, jsonify

db_path = os.getcwd() + '/data/database/college-scorecard.sqlite'
app = Flask(__name__)

@app.route('/colleges', methods=['GET'])
def get_colleges():
    """GET method for all colleges.

    Returns:
        colleges: JSON list of all colleges, sorted by name.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('select instnm from College order by instnm')
    colleges = cur.fetchall()
    return jsonify(colleges)

if __name__ == '__main__':
    app.run(debug=True)
