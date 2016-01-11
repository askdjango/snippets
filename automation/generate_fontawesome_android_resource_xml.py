import re
import requests
from bs4 import BeautifulSoup
import struct


def main():
    url = "http://fortawesome.github.io/Font-Awesome/cheatsheet/"
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    codes = []
    for col in soup.select('.col-md-4'):
        try:
            code_tag = col.select('.text-muted')[-1]
            code = code_tag.text.replace('[', '').replace(']', '')
            if code.startswith('&'):
                for tag in col.select('span, i, small'):
                    tag.extract()

                name = re.sub(r'\s+', '', col.text).replace('-', '_')
                codes.append((name, code))
        except IndexError:
            continue


    matched = re.search(r'Awesome\s+(\d+\.\d+\.\d+)\s+icon', html)
    if matched:
        version = matched.group(1)
    else:
        version = ''

    print('''
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- font awesome {} -->
    <!-- http://fortawesome.github.io/Font-Awesome/cheatsheet/ -->
'''.format(version))

    for name, code in codes:
        print('<string name="{}">{}</string>'.format(name, code))

    print('''
    <string name="fa_adjust">&#xf042;</string>
</resources>
''')

        # <i class="fa fa-fw"></i>
              # fa-youtube-square



if __name__ == '__main__':
    main()

