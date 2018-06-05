from learner import Learner
from imgur import Imgur
from meme import Memer

import logging

doom_img_key = "__doomimg__"
doom_quote_key = "__doomquote__"

class Doom():

    def memify(self, image, content):
        memer = Memer()

        parts = [x.strip() for x in content.encode('utf-8').split(",")]
        top = parts[0] if len(parts) > 0 else None
        bottom = parts[1] if len(parts) > 1 else None

        return memer.get_meme(image, top, bottom)

    def doom_meme(self, content):
        learner = Learner()
        image = learner.get(doom_img_key)

        quote = content if content else learner.get(doom_quote_key)
        return self.memify(image, quote)

    def doom_pic(self, image):
        learner = Learner()
        learner.learn(doom_img_key, image)

        return "got a pick of DOOM"

    def doom_quote(self, quote):
        learner = Learner()
        learner.learn(doom_quote_key, quote)

        return "got some verse from DOOM"

    def doom(self, details):
        if not details or len(details) == 0:
            return self.doom_meme(None)
        elif details[0] == "quote":
            return self.doom_quote(" ".join(details[1:]))
        elif details[0] == "pic" or details[0] == "img":
            return self.doom_pic(details[1])
        else:
            return self.doom_meme(" ".join(details))


