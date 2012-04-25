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
        upstream = _get_build_upstream(build)
        if upstream in upstreams:
            build_time = datetime.strptime(build._data['id'],
                                           "%Y-%m-%d_%H-%M-%S" )
            statuses[upstream] = (build.get_status(), build.baseurl, build_time)
            upstreams.remove(upstream)

    with open('template.html') as f:
        template = Template(f.read())
    return template.render(statuses=statuses,
                           time=datetime.now())

def _get_build_upstream(build):
    return build.get_actions()['causes'][0]['upstreamProject']

if __name__ == "__main__":
    ofile = sys.argv[1]

    # run it continously - or how to flood jenkins
    # while True:
    output = index()

    with open(ofile, 'w') as f:
        f.write(output)
