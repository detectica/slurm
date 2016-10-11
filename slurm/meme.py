import json
import os
from urllib import unquote_plus, quote
import requests


BASE_URL = "https://memegen.link"

class Memer():

    def get_templates(self):
        temp_url = BASE_URL + "/api/templates/"
        response = requests.get(temp_url).json()

        data = [(v.replace(temp_url, ""), k) for k, v in response.items()]
        data.sort(key = lambda tup: tup[0])
        return data

    def list_templates(self):
        return "\n".join(["`{0}` {1}".format(t[0], t[1])  for t in self.get_templates()])

    def build_url(self, template, top, bottom, alt = None):
        path = "/{0}/{1}/{2}.jpg".format(template, top or "_", bottom or "_").replace(" ", "_")

        if alt:
            path = path + "?alt={}".format(alt)

        return BASE_URL + "/" + path

    def image_exists(self, path):
        if path.split("://")[0] not in ["http", "https"]:
            return False

        r = requests.head(path)
        return r.status_code == requests.codes.ok
    
    def get_meme(self,  template, top, bottom):
        template = template.lstrip("<").rstrip(">")
        valid_templates = [x[0] for x in self.get_templates()]
        if template in valid_templates:
            return self.build_url(template, top, bottom)
        elif self.image_exists(template):
            return self.build_url("custom", top, bottom, template)
        else:
            return "%s isn't a valid template. provide your own url type `?meme` to see valid choices" % template
