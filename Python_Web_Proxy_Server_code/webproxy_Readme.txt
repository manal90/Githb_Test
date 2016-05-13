README FILE :
=============
Project : Implementing  Multithreaded HTTP/1.0 Web-proxy along with Caching and Link Prefetch using Python 3.0
Author : Manal P. Chhaya
Version : ver. 3.1
Date : November 21,2015.

CONTENTS:
=========
1.) Description
2.) Software Requirements
3.) Configuration.

=============================

1.) Description :

The assignment describes the use of Web proxy server to handle HTTP 1.0 requests. The Web-proxy receives requests from the client browser, filters the requests to handle GET method and HTTP 1.0 protocol version. Once the request is filtered, it forwards the requests to the server and caches the response in the Dictionary using a new thread for each function. Also, in the background a new process is started to perform Link Prefetch. In this , all the links embedded in the webpage would be cached in the dictionary.

Once the web-page is cached, if the request comes up once again, the response would be returned from the cache itself rather than connecting to the server. This further adds to the better user experience.

Once, the value is cached the timer is started and the value is  checked continuosly into another thread . The value os removed from the dictionary once the time exceeds the time-out as specified by the user.



2.) Software requirements:
---------------------------

Operating system : Windows XP,7 or 8
IDE : Eclipse (Canopy) , Microsoft Word, Notepad.

3.) Configuration:
----------------------

Manually configure the Mozilla Firefox Browser to pass through the proxy server created by us.
