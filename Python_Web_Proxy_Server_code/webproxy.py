import thread
import sys
import socket
import re
import hashlib
import time
import requests
from bs4 import BeautifulSoup

BACKLOG = 5000
count = 0;
Hashes = {} # Dictionary for Cache storage
Hashes_1 = {} # Dictionary for Time-out storage

# Code block to take Time-out value from the user.    
try:
    cache_timeout = sys.argv[1]
    cache_timeout = cache_timeout*60
except:
    print('Error : Kindly enter the cache expiration value to continue')
    sys.exit()

# Main function. Program execution starts from this function.
def main():
    host = '127.0.0.1' # Host address
    port = 2002 # Port number defined.
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket created to accept the request from client.
        print('Socket Created') 
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host , port)) # Bind the socket created earlier to the Host and Port defined in the previous step.       
        print('Socket Bind Complete')
        s.listen(BACKLOG) # Socket enters in listen mode.
        print('Socket in Listen Mode')
        
    except socket.error:
        print('Error : Could not open the socket')
        sys.exit()        
    
    # Infinite Loop defined to accept connections from the client browser.
    
    while 1 :                       
        conn , client_address = s.accept()       
        thread.start_new_thread(proxy, (conn , client_address)) # New thread started for each of the received connection which calls the 'proxy' function to communicate with the server.
                
    s.close()            
# This function is called whenever a new thread is created. It accepts the request from the client and communicates with the server to fetch the response.

def proxy(conn , client_address):
    global cache_timeout ; global count
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket which communicates with the server to fetch the response.
    s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    request = conn.recv(4096)
    
    #print(request)
    if request:
        
        if (request.endswith('\r\n\r\n')):
            #print('True')
            pass;
        else:
            request = request + '\r\n\r\n'   # To enable telnet         
        
        line_1 = request.splitlines()[0]                         
        #method = re.search('(\w+)(\s)' , line_1.decode('utf-8')) # Variable which stores the method type requested from the client.           
        HTTP_version = re.search('(\s)(\w\w\w\w\/\d\.\d)' , line_1.decode('utf-8')) # Variable which stores the HTTP version of the GET request.

        # Filtering only the GET requests.            
        if ('GET' in line_1.decode('utf-8')):                        
            # Filtering only the HTTP versions.
                        
            if (HTTP_version.group(2) == 'HTTP/1.0'):
            
                url = line_1.decode('utf-8').split(' ')[1]   
                http_pos = url.find("://")                   
                if (http_pos==-1): # when value = '-1' , it means the substring does not exist.
                    temp = url
                else:
                    temp = url[(http_pos+3):] # if the substring exists, the 'url' is 3 spaces after the ://
                                        
                hashvalue1 = hashlib.md5(temp.encode('utf-8')) # Calculating the Hash value of the URL extracted earlier.
                u = hashvalue1.hexdigest()            
                
                # If the URL extracted is a valid URL , then the PREFETCH function would be called which would carry out link prefetch.
                
                if (url.startswith('http:')):
                    if (url.endswith('/')):            
                        thread.start_new_thread(prefetch , (url ,) ); # New thread would be started for the prefetch condition.
                
                # This code block checks if the URL hash value is already present in the Dictionary named Hashes.
                # If the URL hash is already present, then the Response would be returned from the dictionary and the connection would be closed.
                
                if u in Hashes.keys():
                    count = count + 1;
                    conn.send(Hashes[u])
                    print('Reading from cache - ' + str(count))
                    conn.close()
                    s1.close()            
                
                # If the URL value is not present in the Dictionary, then the 'response_capture' function would be 
                #called which communicates with the server and returns the response to the client.
                            
                else:
                    response_capture(temp ,s1 ,u ,request,conn);
            
            else:
                resp_1 = "HTTP/1.0 400 BAD REQUEST:Invalid Method\r\n\r\n" + '<h1>400 BAD REQUEST:Invalid HTTP version</h1>'
                conn.send(resp_1)
                conn.close()
                                    
        else:            
            resp = "HTTP/1.0 400 BAD REQUEST:Invalid Method\r\n\r\n" + '<h1>400 BAD REQUEST:Invalid Method</h1>'
            conn.send(resp)        
            conn.close()
            #s1.close()

# This function is used to capture the response from the server and return it to the client.
            
def response_capture(temp , s1 , u , request , conn ):

    port_pos = temp.find(":")           # find the port pos (if any)                          
    webserver_pos = temp.find("/")
    
    if webserver_pos == -1:
        webserver_pos = len(temp)                        
    webserver = ""
    port = -1
    
    if (port_pos==-1 or webserver_pos < port_pos):      # default port
        port = 80
        webserver = temp[:webserver_pos]
    else:                             
        port_1 = re.search(r'(\w+\W)(\d+)' , temp) 
        port = int(port_1.group(2))
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]    
    
    # In the below code block, the socket connects to the server and accepts the response from the server.
        
    try:
        s1.connect((webserver, port))
        s1.settimeout(2)
        s1.send(request)
    except:
        pass 
    
    y = ''
    
    # This loop receives response from the server and stores the value (i.e the Response ) in a Dictionary.
    
    while 1:                    
        try:
            data = s1.recv(4096)
        except:
            #print('Time-out')
            s1.close()
            conn.close()                       
            break;
        
        y = y + str(data)                                                               
        if (len(data) > 0):
        # send to browser
            conn.send(data)
        else:
            break;
    
    # This dictionary, is used to store the hash value of the URL and the response as its value mapping.
    
    Hashes[u] = y
    
    # This dictionary stores the hash value of te URL and its response which is the current system time-stamp for time-out
    
    Hashes_1[u] = int(round(time.time()))        
    
    now_1 = (int(round(time.time())))
    
    # The below loop checks if the Current cached value has expired. If the cached value exceeds the time-out value, 
    #then the object would be deleted from the dictionary.
    
    for keys in Hashes_1.keys():        
        if (now_1 - Hashes_1[keys] > cache_timeout):
            Hashes_1.pop(keys , None)
            Hashes.pop(keys, None)                
    s1.close()
    conn.close()

# The below  function is used to implement link prefetch functionality.
def prefetch(url):
    
    url = url[:-1]    
    # Below code block is used to parse the entire web-page using requests.    
    try:
        response = requests.get(url)
        page = str(BeautifulSoup(response.content , "html.parser"))
    except:
        print('Invalid Host')
        sys.exit()
        
    
    # This function is used to find the number of occurences of the HREF which indictaes the Links embedded in the web-page.
    
    def getUrl(page):
    
        start_link = page.find("a href")
        if start_link == -1:
            return None, 0
        start_quote = page.find('"', start_link)
        end_quote = page.find('"', start_quote + 1)
        url_2 = page[start_quote + 1: end_quote]    
        return url_2, end_quote
    
    # This loop iterates through the number of links and fetch the response for the same.
    
    while True:
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        url_1, n = getUrl(page)
        page = page[n:]
        #print('Iterator')
        #print(url_1)
        if url_1:        
            if url_1.startswith('http:'):
                new_url = url_1
            elif url_1.startswith('https:'):
                pass
            elif url_1.startswith('.'):
                url_1 = url_1[1:]
                url_1 = url + url_1
                new_url = url_1            
            else:          
                if (url_1.startswith('/')):                 
                    url_1 = url + url_1
                    new_url = url_1
                else:
                    url_1 = url + '/' + url_1
                    new_url = url_1
                        
            http_pos = new_url.find("://")        
            #print(http_pos)            
            if (http_pos==-1): # when value = '-1' , it means the substring does not exist.
                new_url_1 = new_url
            else:
                new_url_1 = new_url[(http_pos+3):] # if the substring exists, the 'url' is 3 spaces after the ://
            #print(new_url)
            
            hashvalue2 = hashlib.md5(new_url.encode('utf-8'))
            u1 = hashvalue2.hexdigest() 
            
            port_pos = new_url_1.find(":")           # find the port pos (if any)            
                    # find end of web server            
            
            webserver_pos = new_url_1.find("/")
            
            if webserver_pos == -1:
                webserver_pos = len(new_url_1)                        
            webserver = ""
            port = -1
            
            if (port_pos==-1 or webserver_pos < port_pos):      # default port
                port = 80
                webserver = new_url_1[:webserver_pos]
            
            # This is the GET request constructed by the proxy itself to get the response from the server and store it in the Dictionary.
            
            prefetch_request = 'GET '+new_url+' '+'HTTP/1.0'+'\r\n'+'Host: '+webserver+'\r\n'+'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'+'\r\n'+'Accept-Language: en-GB,en;q=0.5'+'\r\n'+'Accept-Encoding: gzip, deflate'+'\r\n'+'Connection: keep-alive'+'\r\n\r\n'

            try:
                s2.connect((webserver, port))
                s2.settimeout(2)
                s2.send(prefetch_request)                
            except:
                pass;
            
            z = ''
            
            # Below loop accepts the response from the server.
            
            while 1:                    
                try:
                    data = s2.recv(4096)
                except socket.timeout:
                    s2.close()
                    #conn.close()                       
                    break;
                                                            
                if (len(data) > 0):
                # send to browser
                    z = z + str(data)
                    
                else:
                    break;
            # It stores the values values of the key which is a hash value of the URL and the value is the response from the server.                
            Hashes[u1] = z            
            # This dictionary stores the hash value of te URL and its response which is the current system time-stamp for time-out
            Hashes_1[u1] = int(round(time.time()))
                                                        
        else:
            break;    
        
if __name__=='__main__':
    main()                    
        