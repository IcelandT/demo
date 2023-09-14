# -*- coding: utf-8 -*-
import requests
import execjs
import parsel


class tubatu:
    def __init__(self):
        self.url = 'https://www.to8to.com/new_login.php'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }

    def get_response(self, url):
        f = open('login.js', encoding='utf-8')
        code = f.read()
        compile_code = execjs.compile(code)
        user = compile_code.call('rsaString', '18958675241')
        password = compile_code.call('rsaString', '010928ttt')
        print('user ====>', user)
        print('password ====>', password, '\n')
        data = {
            'referer': 'https://www.to8to.com/new_login.php',
            'val': user,
            'password': password
        }
        session = requests.session()
        response = session.post(url=url, headers=self.headers, data=data)
        print(session.cookies.get_dict())
        return response.text

    def get_data(self):
        response = tubatu().get_response(self.url)
        selectors = parsel.Selector(response)
        name = selectors.xpath('//*[@class="mcrbu_detailinfo"]/p/span/text()').get()
        id = selectors.xpath('//*[@class="mcrbu_detailinfo"]/p[2]/text()').get()
        print(name)
        print(id)

    def main(self):
        tubatu().get_data()

if __name__ == '__main__':
    tubatu().main()