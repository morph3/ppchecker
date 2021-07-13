# ppchecker
Simple Prototype Pollution Checker tool. 

Executes some basic prototype pollution payloads and checks if the site is vulnerable to prototype pollution. You can also feed urls with parameter and check if the parameters are vulnerable as well.


# Example Run

[![asciicast](https://asciinema.org/a/425330.svg)](https://asciinema.org/a/425330)

## Example Usages

```
python3 ppchecker.py -l urls.txt -c 30
python3 ppchecker.py -l urls.txt -c 20 -d 
python3 ppchecker.py -u http://ctf.m3.wtf/pplab3.html -c 20
python3 ppchecker.py -u 'https://morph3sec.com/index.html?foo=' -c 20
```