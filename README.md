# ppchecker
Simple Prototype Pollution Checker tool. 

Executes some basic prototype pollution payloads and checks if the site is vulnerable to prototype pollution. You can also feed urls with parameter and check if the parameters are vulnerable as well.

Everytime this script runs, it starts a browser with puppeter. With the given currency, it starts opening new tabs with the urls. After the prototype pollution check is finished, it terminates the tab. This approach is not very good on big wordlists as tabs might hang, they may not be reachable. It may lead to extereme amounts of tabs opened and therefore a crash. So if you want to feed this tool a big wordlist please take a look at [Additional](https://github.com/morph3/ppchecker/blob/main/README.md#additional) section 

# Example Run

[![asciicast](https://asciinema.org/a/425330.svg)](https://asciinema.org/a/425330)

# Example Usages

```
python3 ppchecker.py -l urls.txt -c 30
python3 ppchecker.py -l urls.txt -c 20 -d 
python3 ppchecker.py -u http://ctf.m3.wtf/pplab3.html -c 20
python3 ppchecker.py -u 'https://morph3sec.com/index.html?foo=' -c 20
```


# Additional

If you are going to work on big wordlists I suggest you to use the command below to distribute the load equally.

```
cat urls.txt | xargs -I% -P 50 sh -c 'python3 ppchecker.py -u "%"'
```
