#COPY RIGHTS
# AUTHOR-------> GARVIT SHARMA  &&  SATYA PRAKASH   &&  AKSHATA DHAGE  
# Mail Id------> "garvitsharma2611@gmail.com" | "satyaprk92@gmail.com"  | "akshatadhage979@gmail.com"

#importing the main event loop

import tornado.ioloop          
import os
import koji
# for the HTTP requesthandlers (to map the request to request handler)
import tornado.web 
import json

url_add1 = 'git+'
url_add2 = '#'

BUILD_TRIGGER = 'kojibuild'
BUILD_TARGET = 'f38'

KOJIHUB = 'http://cdackoji.pune.cdac.in/kojihub'
SERVERCA = os.path.abspath('/home/akshata/.koji/koji_ca_cert.crt')
CLIENTCA = os.path.abspath('/home/akshata/.koji/koji_ca_cert.crt')
CLIENTCERT = os.path.abspath('/home/akshata/.koji/akshata.pem')



class handler(tornado.web.RequestHandler):
    def koji_build(self,final_url):
        kojisession = koji.ClientSession(KOJIHUB)
        print(kojisession)
        kojisession.ssl_login(CLIENTCERT, CLIENTCA, SERVERCA)
        result = kojisession.build(final_url,BUILD_TARGET)
        print("Build started")
        print("Build Id is ",result)

    
    def post(self):
        try:
            print("=================================================")
            print("Event occurs. Trying to get the data....")
            global url_add1, url_add2
            data = json.loads(self.request.body)
            print("Successfully got the data in JSON format.")
            #print(data)
            json_obj = json.dumps(data)
            with open("sample.json", "w") as outfile:
                outfile.write(json_obj)
            
            file_obj = open('sample.json')
            get_data = json.load(file_obj)
            Condition_Message = get_data['commits'][0]['message']
            Build_Condition = Condition_Message.find(BUILD_TRIGGER) 
            if Build_Condition != -1:
                print("MESSAGE: Match Found.")
                url_id = get_data['commits'][0]['id']
                url_var = get_data['commits'][0]['url']
                url_parts = url_var.split("/commit",1)
                final_url = "'" + url_add1 + url_parts[0] + url_add2 + url_id + "'"
                print(final_url)

                self.koji_build(final_url)
            else:
                print("MESSAGE: Missing \"kojibuild\" message in the commit.")
            
            print("==================================================")

        except json.JSONDecodeError:
            self.set_status(400, "Invalid JSON payload")
            return
    

def make_app():
    return tornado.web.Application([
        (r"/",handler)

    ])
   

if __name__ == "__main__":
    app = make_app()
    port = 8081                  # port use for the tornado
    app.listen(port)
    print('Server is listenning on ',port,"....")

    # to start the server on the current thread
    tornado.ioloop.IOLoop.current().start()
        