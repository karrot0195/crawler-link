import threading
from Configs.enum import ServerConfig
from CrawlerLib.Pymongo import MongodbClient
from CrawlerLib.helper import get_master_attr
from CrawlerLib.show_notify import show_debug, show_warning
from Facade.Selemium.SeleniumBuilder import SeleniumBuilder
from Facade.Selemium.InstagramPost import InstagramPost
from Facade.Selemium.YoutubePost import YoutubePost
from Facade.Selemium.FBPost import FBPost
import requests


class Selenium:
    main_selenium = None

    def __init__(self):
        self.driver = SeleniumBuilder.build(ServerConfig.SELENIUM_TYPE.value)
        self.selenium_types = {
            'FB': FBPost(),
            'IG': InstagramPost(),
            'YT': YoutubePost()
        }

    @staticmethod
    def get_instance():
        Selenium.main_selenium = Selenium()
        return Selenium.main_selenium

    def screen_post(self, post_type, post_id):
            if ServerConfig.ENABLE_SCREENSHOT.value and post_type in self.selenium_types:
                x = threading.Thread(target=self.process_thread_screenshot, args=(post_type, post_id))
                x.start()
            return None


    def process_thread_screenshot(self, post_type, post_id):
        try:
            # show_debug('Process take screenshot ...' + post_id)
            link = MongodbClient.get_instance().get_link_collection().find_one({'link_id': post_id})
            if link:
                data = {
                    'processing_screenshot': 0
                }
                screenshot = self.selenium_types[post_type].screen_post(self, post_id)
                if screenshot:
                    data['screenshot'] = screenshot
                MongodbClient.get_instance().get_link_collection().update_one({'_id': link['_id']}, {
                    '$set': data
                })

                data = {
                    'link_id': get_master_attr('link_id', link, None),
                    'type': get_master_attr('type', link, None),
                    'screenshot': get_master_attr('screenshot', link, None)
                }
                hook_url = link['hook_url']
                result = requests.post(hook_url, data)
            else:
                show_debug('NOT FOUND LINK')
        except Exception as e:
            print('error code: #117228')
            print(format(e))
