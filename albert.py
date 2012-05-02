#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2011 Ionuț Arțăriși <iartarisi@suse.cz>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import with_statement

import sys
from time import sleep
from datetime import datetime

from jinja2 import Template
from jenkinsapi import jenkins

JENKINS = "http://river.suse.de"
JOB = 'openstack-unittest'
SECONDS = 3 # how often will the page be refreshed

def build_time(build):
    """Return the relative time for when the build finished"""
    time = datetime.strptime(build._data['id'], "%Y-%m-%d_%H-%M-%S" )
    delta = datetime.now() - time
    return next("%i %s ago" % (getattr(delta, measure) / div, output)
                for output, div, measure in (('days', 1, 'days'),
                                             ('hours', 3600, 'seconds'),
                                             ('minutes', 60, 'seconds'),
                                             ('seconds', 1, 'seconds'))
                if getattr(delta, measure) / div)

def index():
    jserver = jenkins.Jenkins(JENKINS)
    our_job = jserver.get_job(JOB)

    upstreams = [u['name'] for u in our_job._data['upstreamProjects']]
    statuses = {}
    latest_builds = (our_job.get_build(b) for b in our_job.get_build_ids())
    while upstreams:
        build = latest_builds.next()
        upstream = build.get_actions()['causes'][0]['upstreamProject']
        if upstream in upstreams:
            statuses[upstream] = (build.get_status(),
                                  build.baseurl,
                                  build_time(build))
            upstreams.remove(upstream)

    return Template("""
    <!doctype html>
    <head>
         <title>Albert is watching</title>
         <style type="text/css">
             body { width: auto; margin: 5% 25%; }
             table { font-size: 1.3em; }
             tr.failed { background: #F7DAE6; }
             tr.success { background: #CAE8CC; }
             tr.unknown { background: white; }
             td { padding: .7em; }</style>
    </head>
    <body>
        <table>
          <tr><th>Job</th><th>Status</th><th>Time</th></tr>
          {% for job_name, (status, url, build_time) in statuses.items() %}
          {% if status == "FAILURE" %}
          <tr class="failed">
          {% elif status == "SUCCESS" %}
          <tr class="success">
          {% else %}
          <tr class="unknown">
          {% endif %}
            <td><a href="{{ url }}">{{ job_name }}</a></td>
            <td>{{ status }}</td>
            <td>{{ build_time }}</td>
          </tr>
          {% endfor %}
        </table>

        <p>Last generated: {{ time }}</p>
    </body>
    """).render(statuses=statuses, time=datetime.now())

if __name__ == "__main__":
    ofile = sys.argv[1]

    while True:
        output = index()
        with open(ofile, 'w') as f:
            f.write(output)
        sleep(SECONDS)
