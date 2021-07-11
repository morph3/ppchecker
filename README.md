# ppchecker
Simple Prototype Pollution Checker tool. 

Executes some basic prototype pollution payloads and checks if the site is vulnerable to prototype pollution. You can also feed urls with parameter and check if the parameters are vulnerable as well.


## Usage

*** I will implement multiple concurrency and detailed scan soon. ***

For now just use for multiple concurrency
```
cat urls.txt | xargs -I% -P 50 sh -c 'python3 ppchecker.py -u "%"'

```
or 
```
cat urls.txt | parallel -j 50 python3 ppchecker.py -u
```


For single url,

```
python3 ppchecker.py -u 'https://morph3sec.com/index.html?foo='
```