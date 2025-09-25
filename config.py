import requests
import re
from bs4 import BeautifulSoup as parser
from rich import print
from rich.console import Console
from rich.align import Align
import sys
import time
import inquirer
import os

folder_name = "ViewConfig"
console = Console()

class AllConfig:
    def __init__(self):
        self.requ = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
            'Referer': 'https://sfile.mobi/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def GetConfig(self):
        response = self.requ.get(
            'https://sfile.mobi/loads/6/Config.html',
            headers=self.headers
        )
        html = parser(response.text, 'html.parser')

        # response sfile
            #<img alt="xl axis vidio ssl v122.hc" height="30" src="https://sfile.mobi/icon/smallicon/hc.svg" width="30"/>
            #<a href="https://sfile.mobi/9cmf92SWVaC">xl axis vidio ssl v122.hc</a><br/>
            #<small>39.11 KB, Uploaded: 22 Sep 2025, Download: 1</small></div>
        list_config = []
        for _ in html.find_all("div", {"class":"list"}):
            a_tag = _.find("a")
            if a_tag:
                url  = a_tag.get("href")
                name = a_tag.text
                if '.hc' in name:
                    info = _.find('small').text
                    list_config.append({'name': name, 'url': url, 'info': info})
        return list_config

    def Step1(self, url: str):
        response = self.requ.get(
            url,
            headers=self.headers.update({'Referer': 'https://sfile.mobi/loads/6/Config.html'})
        )
        next = re.search('id="download" href="(.*?)"', str(response.text)).group(1)
        return next, ("; ".join([f"{k}={v}" for k, v in response.cookies.get_dict().items()]))
    
    def Step2(self, url: str, cookies):
        response = self.requ.get(
            url,
            headers=self.headers.update({'Referer': url}),
            cookies=cookies
        )
        next = re.search('var sf = "(.*?)"', str(response.text)).group(1)
        return next.replace('\\/', '/').replace('\\', '')
    
    def Finis(self, name: str, url: str):
        response = self.requ.get(
            url,
            headers=self.headers
        )
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        downloaded = 0

        with open(f'{folder_name}/{name.replace(" ", "")}', 'wb') as f:
            for data in response.iter_content(block_size):
                f.write(data)
                downloaded += len(data)
                bar_length = 40
                percent = (downloaded / total_size) * 100 if total_size else 0
                filled_length = int(bar_length * downloaded // total_size) if total_size else 0
                bar = '█' * filled_length + '-' * (bar_length - filled_length)
                sys.stdout.write(f'\r|{bar}| {percent:6.2f}% {downloaded/1024:.2f}KB/{total_size/1024:.2f}KB')
                sys.stdout.flush()
                time.sleep(0.05)  # beri delay agar animasi terlihat bagus
            sys.stdout.write('\n')
        print(f"\n> Config '{name}' berhasil disimpan di folder '{folder_name}'.")
    
class Home:
    def __init__(self):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        self.Hc = AllConfig()
        self.banner = r"""[cyan]
____   ____                   _____.__        
\   \ /   /____  ____   _____/ ____\__| ____  
 \   Y   // ___\/  _ \ /    \   __\|  |/ ___\ 
  \     /\  \__(  <_> )   |  \  |  |  / /_/  >
   \___/  \___  >____/|___|  /__|  |__\___  / 
              \/           \/        /_____/  [/cyan]"""

    def Menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        aligned_banner = Align.center(self.banner, vertical="middle")
        console.print(aligned_banner)
        console.print(Align.center("https://github.com/ViewTechOrg/Vconfig", vertical="middle"))
        ConfigHC = self.Hc.GetConfig()
        choices = [f"{config['name']} - {config['info']}" for config in ConfigHC]
        questions = [
            inquirer.List(
            "config",
            message="Pilih config",
            choices=choices
            )
        ]
        answer = inquirer.prompt(questions)
        chs = choices.index(answer["config"])
        chs_data = ConfigHC[chs]
        Stp1,cookies = self.Hc.Step1(chs_data['url'])
        Stp2 = self.Hc.Step2(Stp1, {'cookie':  cookies})

        self.Hc.Finis(chs_data['name'], Stp2)
try:Home().Menu()
except TypeError:
      print ("> Sistem Berhenti")
      exit()
