#!/usr/bin/env python
# author: thuhak.zhou@nio.com
import types
import json
import logging
import requests
import tornado.web
import tornado.ioloop
from tornado.options import define, options, parse_command_line
from myconf import Conf

define('config', default='/etc/githook.json', help='config file')
parse_command_line()
config = Conf(options.config)


class GitLabHook(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.headers.get('Content-Type') != 'application/json':
            raise tornado.web.HTTPError(400, log_message='only accept json format')
        elif self.request.headers.get('X-Gitlab-Token') != config['server']['token']:
            raise tornado.web.HTTPError(403, log_message='access denied, check your token')


class GitLabTagHook(GitLabHook):
    jenkins_url = ''
    jenkins_token = ''
    trigger = ['add', 'remove']

    def post(self):
        body = json.loads(self.request.body)
        params = {}
        if body.get('event_name') == 'tag_push':
            try:
                params['action'] = 'remove' if int(body['after'], 16) == 0 else 'add'
                params['repo'] = body['project']['ssh_url']
                params['tag'] = body['ref'].split('/')[-1]
                params['user_name'] = body['user_name']
                params['user_email'] = body['user_email']
                params['namespace'] = body['project']['namespace']
                params['project'] = body['project']['name']
                params['token'] = self.jenkins_token
                if params['action'] in self.trigger:
                    requests.get(url=self.jenkins_url, params=params)
                self.finish('finish')
            except Exception as e:
                logging.error('request error: {}'.format(str(e)))
                raise tornado.web.HTTPError(500)


def make_app():
    taghandlers = config['taghandler']
    apps = []
    for h in taghandlers:
        clsdict = taghandlers[h]
        tmpcls = types.new_class(h, (GitLabTagHook, ), {}, lambda ns: ns.update(clsdict))
        tmpcls.__module__ = __name__
        url = '/tag/' + h
        apps.append((url, tmpcls))
    return tornado.web.Application(apps)


def main():
    logging.info('starting gitlab hooker adapter')
    app = make_app()
    app.listen(config['server']['port'])
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
