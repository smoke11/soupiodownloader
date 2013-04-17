from BeautifulSoup import BeautifulSoup as bs
import urlparse
import datetime
import time
from urllib2 import urlopen
from urllib import urlretrieve
import os
import sys
ignorewords = { #words to ignore. check before spliting
    "static.soup.io", #static elements like buttons
    "16-square", #icons
    "32-square", #icons
    "24-square", #icons
    "48-square", #icons
}
main_folder = "/soup_io_images/"
image_folder = ""
start_time = datetime.datetime.now()
strstarttime = str(start_time.hour)+'_'+str(start_time.minute)+"_"+str(start_time.second)

def log(message, colls):
    with open(main_folder+"log_"+strstarttime+".txt", 'a') as f: #write to log file
        if colls:
            f.write("------------\r")
            print "------------\r"
        f.write(message)
        print message
        if colls:
            f.write("------------\r")
            print "------------\r"
    f.close()

def main(username, since="0"): # as base of coding, used this: http://stackoverflow.com/questions/257409/download-image-file-from-the-html-page-source-using-python
    global main_folder
    main_folder = main_folder+username+"/"
    if not os.path.exists(main_folder):
        try:
            os.makedirs(main_folder)
            log("Created folder: {0}\r".format(main_folder),False)
        except OSError:
            log("Can`t create folder:{0}. Probably no write rights on this disk/account or no free space.\r".format(main_folder),True)
            image_folder=""
    url="http://"+username+".soup.io"
    nextpage=""
    page=0
    maxPages=15000
    timeStamp=since
    lastNumberOfLinks=0
    numberOfLinks=0
    global lastTimeOfPost
    lastTimeOfPost="no date yet"
    timeOfPost = "no date yet"
    #check if download from newest reposts or from specific
    if since != "0":
        if since[0:5]=='date=':
            nextpage ="/?"+since
            lastTimeOfPost=since[5:]
        else:
            nextpage = "/since/"+str(timeStamp)+"?mode=own"
    #write info
    log("Start SoupIoDownloader:\nStarting on: {0}, for url: {1}\n".format(start_time,url+nextpage), True)
    #check if user exists
    try:
        soup = bs(urlopen(url+nextpage))
    except BaseException:
        log("Something wrong went with: {0} \rPossibly connection shut down. Now waiting a minute in peace and then carry on.\r".format(url+nextpage), True)
        time.sleep(60) #wait a minute to cooldown i guess
    newusername=soup.findAll("h2")
    if len(newusername)>0:
        newusername=newusername[0].next
        if "Happy happy joy joy" in newusername:
            registerUrl="http://www.soup.io/signup?user[login]="+username
            log("There is no user with {0} name. You can create if you want, follow the link: {1}\r".format(username,registerUrl),True)
            log("Exiting script.", False)
            exit()
    #start downloading
    while(page<=maxPages):
        time.sleep(0.5) #for less work on servers
        #get url
        fullUrl=url+nextpage
        #write info
        log("[{0}] Getting images for page: {1}/{2} (max), from: {3}, for url: {4}. (Last date: {5})\r".format(datetime.datetime.now(),page, maxPages, timeStamp, fullUrl,lastTimeOfPost), True)
        #try download page source
        try:
            soup = bs(urlopen(fullUrl))
            parsed = list(urlparse.urlparse(url))
        except BaseException:
            log("Something wrong went with: {0} \rPossibly connection shut down. Now waiting a minute in peace and then carry on.\r".format(fullUrl), True)
            time.sleep(60) #wait a minute to cooldown i guess
            continue
        #download images
        downloadImages(soup,parsed)
        #find if there is next page
        load_more=soup.findAll(id="load_more")
        if len(load_more)>0:
            nextpage=load_more[0].findAll('a')[0]['href'] #finding url to next page
            timeStamp = nextpage.split("/")[2].split("?")[0] #getting timestamp from url for next page
        else:
            nextpage="THE END"
        numberOfLinks+=1
        #get to the end, yay!
        if nextpage is "THE END":
            runTime = str(datetime.datetime.now() - start_time)
            log("You`ve have reached the end.\r",True)
            log("Statistics: \rPages: {0}, Images: {1} (approximately). \rTime: {2} \rLast (since) timestamp: {3}, Last date: {4}\r".format(page, page*lastNumberOfLinks,runTime,timeStamp,lastTimeOfPost),True)
            log("Exiting script.", False)
            exit()
        page+=1
        lastNumberOfLinks=numberOfLinks


def downloadImages(soup, parsed):
    timeOfPost="can`t find a date"
    for image in soup.findAll("img"):
    #check image tag is broken
        if len(image.attrs)==0:
            log("Ignoring: {0}\r".format(image),False)
            continue
        ignoreimage = False
        #check if its image to download or some static/avatar image
        for word in ignorewords:
            if word in image["src"]:
                ignoreimage = True
                break
        if ignoreimage: #checking if its image to download or not
            log("Ignoring: {0}\r".format(image['src']),False)
            continue
        else:
            #get date of posting this image
            i=0
            postContainer=image.parent
            while(i<6):
                if postContainer!=None:
                    idofParent = postContainer.get('id')
                    if idofParent != None:
                        if "post" in idofParent:
                            break
                if postContainer!=None:
                    postContainer=postContainer.parent
                i+=1
            if postContainer!=None:
                spans=postContainer.findAll("span")
                if len(spans)>0:
                    for span in spans:
                        className = span.get('class')
                        if className=="time":
                            abbrs=span.findAll('abbr')
                            if len(abbrs)>=0:
                                timeOfPost=abbrs[0].attrs[0][1]
                                global lastTimeOfPost
                                lastTimeOfPost=timeOfPost
                                split = timeOfPost.split(" ")
                                year = split[2]
                                month = split[0]
                                day = split[1]
                                #making folders for specific year and month
                                global image_folder
                                image_folder=year+"/"+month
                                if not os.path.exists(main_folder+image_folder):
                                    try:
                                        os.makedirs(main_folder+image_folder)
                                        log("Created folder for path: {0} in main folder: {1}\r".format(image_folder, main_folder),False)
                                    except OSError:
                                        log("Can`t create folder: {0} in main folder: {1}. Probably no write rights on this disk/account or no free space.\r".format(image_folder, main_folder),True)
                                        image_folder=""

            log("Image: {0}, from: {1}\r".format(image['src'],timeOfPost),False)


        time.sleep(0.1) #for less work on servers
        filename = image["src"].split("/")[-1] #taking name of image
        parsed[2] = image["src"]
        outpath = os.path.join(main_folder+image_folder, filename)
        # try download image
        try:
            if image["src"].lower().startswith("http"):
                urlretrieve(image["src"], outpath)
            else:
                urlretrieve(urlparse.urlunparse(parsed), outpath)
        except BaseException:
            log("Something wrong went with: {0} \rPossibly connection shut down when downloading file. Now waiting a minute in peace and then carry on.\r".format(image["src"]),True)
            time.sleep(60) #wait a minute to cooldown i guess
            continue

def _usage():
    print "Downloader for images from soup.io sites"
    print "usage: python main.py username pathForImages since/date\r"
    print "i.e. 'python main.py smoke11'"
    print "i.e. python main.py smoke11 E:\soupioimages date=2012-04-02\r"
    print "i.e. python main.py smoke11 E:\soupioimages 296358805\n"
    print "pathForImages - optional argument. if you leave it empty it will make folder 'soup_io_images' in your script directory\n"
    print "since/date - optional argument, you can put date in format date=YYYY-MM-DD, \r"
    print "or you can put since number - you can get it from soup.io url, when loading older post manually. \r"
    print "i.e. 'http://smoke11.soup.io/since/52838091?mode=own%3D8ee428d6102f5fcece4826e1cc4b6c3a' where wanted number is between 'since/'and '?' sign\r"
    print "if you leave it empty or put '0' it will start downloading from your newest reposted image from main site of user.\n"

if __name__ == "__main__":
    _usage()
    since_date=None
    username = sys.argv[1]
    if len(sys.argv)>2:
        main_folder = sys.argv[2]
        if main_folder[-1]!="/":
            main_folder+= "/"
    else:
        main_folder = "/soup_io_images/"
    if len(sys.argv)>3:
        since_date=sys.argv[3]
    if not os.path.exists(main_folder):
        try:
            os.makedirs(main_folder)
            log("Created folder for path: {0}\r".format(main_folder),False)
        except OSError:
            log("Can`t create folder: {0}. Probably no write rights on this disk/account or no free space.\r".format(main_folder),True)
            log("Exiting script.", False)
            exit()

    if username==None or username=="" or username==" ":
        log("You must specify username to run this script!\r")
        exit()
    if since_date!=None:
        main(username, since_date)
    else:
        main(username)

