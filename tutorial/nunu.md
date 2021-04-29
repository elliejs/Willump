# Nunu
## The server that translates Yeti to English
Nunu is the companion component to Willump. It is a LAN server which runs on the host computer. Nunu can be used to debug LCU methods straight from the browser, and can be used to incorporate web front-ends to League of Legends projects.

## Installing Nunu
Nunu is bundled with Willump. For information on installing Willump, refer to [here](github.com/elliejs/willump).

## Nunu Quickstart
Once Nunu is installed and running (see below), you can test out demo code [here](https://zork.pw). Simply put in the host:port given to you by Nunu into the text box and hit "Click here for custom lobby demo", and you will be put into a custom lobby and the response from the put request will be pasted into the webpage where it says "Nunu Response appears here". The source code for this website is available [here](https://github.com/elliejs/Willump/tree/main/nunu). **Use either `'*'` or `'https://zork.pw'` for Allow_Origin.**

## Starting Nunu
Nunu can be started at any time after Willump has been started and awaited.
```py
import willump
wllp = await willump.start()
wllp = await wllp.start_nunu(Allow_Origin='YOUR_ORIGIN', ssl_key_path='YOUR_SERVER_KEY')
```
Or you can use the following start argument for slightly faster async loading if you're ok with Nunu being loaded before Willump connects to the LCU completely
```py
wllp = willump.start(start_nunu=True, Allow_Origin='YOUR_ORIGIN', ssl_key_path='YOUR_SERVER_KEY')
```

## Nunu Methods
Nunu has the following methods:
- `async start_nunu(self, Allow_Origin: str, ssl_key_path: str, port=None: int, host=None: ip_addr): Willump`
- `async close_nunu(self): None`

These are also always available on the Willump [methods](https://github.com/elliejs/Willump/blob/main/tutorial/method_documentation.md) page.

### Allow_Origin
Allow_Origin is a mandatory argument which sets the [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) header *Access-Control-Allow-Origin*. The option which will allow you access from your local machine and any machine you choose to ping from is `'*'`. **This option is inherently unsafe**, since it allows information from *. AKA anywhere. So B0bby Haxor Joseph who found your LCU server can perform PUT requests on your behalf, as long as they have internet access to your server.

## !!Important!!
### Avoiding XSS and understanding CORS, LAN, WAN, and the internet.
Allow-Origin is a dangerous tool, and understanding CORS is an important step to writing safe programs on the internet.
1) **LAN**:
  LAN stands for Local Access Network. For most users, it is the collection of computers all connected to the same router you are. If you're at home this is usually a safe space. If you're at a public cafe or airport, this is much less true, as there are many strangers connected to the same wifi network.
2) **WAN**:
  WAN stands for Wide Access Network. This is \~*The Internet*\~. If you set up a server on your external IP address, then anyone with the magic number can access it. **UNLESS YOU ARE FULLY AWARE OF THE RISKS OF EXPOSING YOUR SERVER TO THE WORLD DO NOT DO THIS**
3) **CORS & XSS**:
  CORS stands for Cross Origin Resource Sharing. XSS stands for Cross Site Scripting. These topics are big, and you should probably go look them up if you don't know what they are. I'm sure some Medium writer has made a fine article on the subject.

Basically, when you talk from one server to another, you open yourself up to lots of potential threats. Be aware of these threats before making yourself vulnerable and unprepared.

### ssl_key_path
Nunu is a HTTP**S** server, because the internet these days is HTTP**S**. To make this work, Nunu needs a private SSL key. If you don't have one and don't know how to make one you can create a debug self-signed-certificate like so:

**Linux**
```
openssl req -new -x509 -keyout KEYNAME.pem -out KEYNAME.pem -days 365 -nodes
```
(Requres openssl)

Go read a medium article to find out more about TLS, SSL, certificates, and more.

### port
By default Nunu runs on port 8989. If this doesn't work for you, you may supply a different port. (ports > 8000 are recommended)

### host
Nunu is capable of determining where its running and it will tell you in the console when you run it what host it's running on. If you know better and would like to supply it with a specific host to run on, you may do so with this argument.

## Closing Nunu
Nunu will close if it is running when calling Willump's `close(self)` method. If you want to shutdown only the Nunu component you may call Willump's `close_nunu(self)` method.

*Nunu isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.*
