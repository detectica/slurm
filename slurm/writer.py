import requests
from bs4 import BeautifulSoup
import tempfile
from imgur import Imgur
import logging
import sys

class Writer():
    
    def get_writing(self, string_to_write):
        payload = {
            'text':string_to_write,
            'bias':0.15,
            'samples':1
        }

        try:
            response = requests.get('http://www.cs.toronto.edu/~graves/handwriting.cgi', params=payload)
            if response.status_code != 200:
                return "there was an error creating the image. code: %s" % response.status_code

            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            image = soup.find_all("img")[-1]
            image_src = image['src']
            b64 = image_src[(image_src.index(',') + 1):]

            file = tempfile.NamedTemporaryFile(suffix=".png")
            file.write(b64.decode("base64"))
            file.flush()
                       
            img = Imgur()
            url = img.save_from_file(file.name)
            file.close()
            return url

        except Exception as e:
            print "there was an error", e.message
            return "foo"
        except:
            logging.debug("there was an error!")
            logging.debug(sys.exc_info()[0])
            return "there was an error writing!"
