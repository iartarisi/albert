#!/usr/bin/env python

from __future__ import with_statement

import sys
from datetime import datetime

from jinja2 import Template
from jenkinsapi import jenkins

JENKINS = "http://river.suse.de"

def index():
    jserver = jenkins.Jenkins(JENKINS)
    our_job = jserver.get_job('openstack-unittest')

    upstreams = [u['name'] for u in our_job._data['upstreamProjects']]
    statuses = {}
    latest_builds = (our_job.get_build(b) for b in our_job.get_build_ids())
    while upstreams:
        build = latest_builds.next()
        upstream = build.get_actions()['causes'][0]['upstreamProject']
        if upstream in upstreams:
            build_time = datetime.strptime(build._data['id'],
                                           "%Y-%m-%d_%H-%M-%S" )
            statuses[upstream] = (build.get_status(), build.baseurl, build_time)
            upstreams.remove(upstream)

    return Template("""
    <!doctype html>
    <head>
         <title>Albert is watching</title>
         <style type="text/css">
             body { width: auto; margin: 5% 25%; }
             table { font-size: 1.3em; }
             tr.failed { background: #F7DAE6; }
             tr.ok { background: #CAE8CC; }
             td { padding: .7em; }</style>
    </head>
    <body>
        <table>
          <tr><th>Job</th><th>Status</th><th>Time</th></tr>
          {% for job_name, (status, url, build_time) in statuses.items() %}
          {% if status == "FAILURE" %}
          <tr class="failed">
          {% else %}
          <tr class="ok">
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

    # run it continously - or how to flood jenkins
    # while True:
    output = index()

    with open(ofile, 'w') as f:
        f.write(output)
