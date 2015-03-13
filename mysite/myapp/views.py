from django.http import HttpResponse

from bs4 import BeautifulSoup, Comment
import urllib3, requests, re, codecs, pprint
def fancyPrint(msg, s):
    pp = pprint.PrettyPrinter(indent=4)
    print msg
    pp.pprint(s)
    print''
    

def printEncoding(s):
    if isinstance(s, str):
        print "ordinary string"
        print ' '
    elif isinstance(s, unicode):
        print "unicode string"
        print ' '
    else:
        print "not a string"
        print ' '

def findHyperlinks(rootUrl):
    r  = requests.get("http://" +rootUrl)
    data = r.text
    soup = BeautifulSoup(data)
    hyperlinks = []
    for link in soup.find_all('a'):
        try:
            hyperlinks.append(link.get('href').encode())
        except: 
            pass
    return hyperlinks
    
def filterByTails(listToFilter, firstInputUrl):
    parser = urllib3.util.url
    tailCount = countTails(parser.parse_url(firstInputUrl).path)
    newList = []
    for link in listToFilter:
        if (("http://" not in link) and ("https://" not in link) and ("@" not in link) and ("terms_of_use" not in link) and ("privacy_policy" not in link)):
            lengthOfSplittedArray = len(link.split("/"))
            if (lengthOfSplittedArray == (tailCount+1)):
                newList.append(link)
            if ("/?" in link): #don't care about size because if it has ? it won't match up anyways
                newList.append(link)
    return list(set(newList)) #removes duplicates
            
def filterByAMPM(listToFilter):
    found = 0
    for page in listToFilter:
        meetsCriteria(page) #tofinish
        
def getSoupEncoding(soup):
    encod = soup.meta.get('charset')
    if encod == None:
        encod = soup.meta.get('content-type')
        if encod == None:
            content = soup.meta.get('content')
            match = re.search('charset=(.*)', content)
            if match:
                encod = match.group(1)
            else:
                raise ValueError('unable to find encoding')
    return encod
 
def activityTester(suspectListOfLinks, rootUrl):
    activityPages = []
    for suspectLink in suspectListOfLinks:
        if (len(activityPages) >= 10):
            break
        else:
            suspectUrl = 'http://' + rootUrl + suspectLink #debug
            suspectEvidence = meetsCriteria(suspectUrl)
            if ((len(suspectEvidence) > 1) and (len(suspectEvidence) < 12)): #TODO: How many AM/PM matches are good enough?
                activityPages.append(suspectUrl)
            activityPages = list(set(activityPages))
    return activityPages

def purge(soup):
    for s in soup('script'):
        s.extract()
    for t in soup('table'):
        if (t.get('summary') is not None):
            t.extract()
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    for comment in comments:
        comment.extract()
    return soup    
    
#Note: Encoding of res.text is unicode string, soupTemplate is not a string
def meetsCriteria(endpoint):
    res = requests.get(endpoint)
    soupTemplate = BeautifulSoup(res.text)
    soupTemplate = purge(soupTemplate)
    encoding = getSoupEncoding(soupTemplate)
    pretty = soupTemplate.prettify(encoding) 
    #fancyPrint('meetsCriteria.pretty',pretty) #debug
    pat = r'(\d{1,2}:\d{2}|\d{1,2})\s*(?:(AM|PM|am|pm|a\.m\.|p\.m\.|A\.M\.|P\.M\.|a$|p$|A$|P$))' #here goes nothing
    timestringList = re.findall(pat, pretty) #finds all occurences of pattern in the big pretty print
    return timestringList
        
    
      
#hostUri is root.com/might/have/tails may change depending on when its called
def aggregator(firstInputUrl, hostUri, root):    
    print'hostUri: ',hostUri #hostUri is '...com' or '...com/some/path'
    #gets all hyperlinks found on the root page as a list
    sameLevelLinks = [] #contains all hyperlinks that come out of hostUri relative to its current depth
    sameLevelLinks = findHyperlinks(hostUri) #sameLevelLinks must remove all links with tails not equal to ..com/foo/bar/standardevent
    #debug
    #print'aggregator().sameLevelLinks: ',sameLevelLinks 
    #filters the list to match the number of tails in original REST endpoint
    suspectLinks = []
    suspectLinks = filterByTails(sameLevelLinks,firstInputUrl) 
    #Calls a tester to actually go to all pages in Suspects[]
    finalList = []
    finalList = activityTester(suspectLinks,root)#passes in suspctLinks to be appended at the end of root
    #debug
    #fancyPrint('Aggregator()finalList: ',finalList)
    if (len(finalList) < 10):
        return finalList 
    elif (len(finalList) >=10):
        return finalList
    else:
        print 'EXCEPTION: aggregator hit else clause. No exit occured'
        return finalList
        
def filterByKeyword(listToTrim, keywordsList):
    newList = []
    for item in listToTrim: #for each hyperlink that may contain a keyword
        for key in keywordsList: #for each keyword
            if (("http://" not in item) and ("https://" not in item)):
                if key in item:
                    newList.append(item) #append links that only have 'event', 'calendar' in them
                    break #breaks out of inner loop
    return newList  
        
def countTails(pathnm): #if original input has 3 tails, therefore our suspects will also have 3 tails
    tcount = len(pathnm.split('/')) #4, for the case of boston
    if (pathnm[-1] == '/'): #detect trailing slash in input url
        tcount -= 2 #because BeautifulSoup automatically truncates trailing slashes
    else:
        tcount -= 1 #account for starting slash increasing the len(A.split)
    return tcount
    
    
def unused():
    urlInput = 'foo';
    stfd = 'http://events.stanford.edu/events/353/35309/'       
    boston = 'http://calendar.boston.com/lowell_ma/events/show/274127485-mrt-presents-shakespeares-will'
    mom = 'http://www.sfmoma.org/exhib_events/exhibitions/513'
    wshop = 'http://www.workshopsf.org/?page_id=140&id=1328'
    lacma = 'http://www.lacma.org/event/louie-beltran'
    userInput = raw_input("Enter which website to test: 1=stfd, 2=boston, 3=mom, 4=wshop, 5 = lacma")        
    if (userInput == '1'):
        urlInput = stfd
    elif (userInput == '2'):
        urlInput = boston
    elif (userInput == '3'):
        urlInput = mom
    elif (userInput == '4'):
        urlInput = wshop
    elif (userInput == '5'):
        urlInput = lacma      
    else:
        raise Exception("Bad argument")
        
def command(urlInput):
    parser = urllib3.util.url
    parseResult = parser.parse_url(urlInput)
    
    #collect single line information that we'll need later
    hostName = parseResult.host #calendar.boston.com
    root = hostName #save this for later
    pathName = parseResult.path #/lowell_ma/events/show/274127485-mrt-presents-shakespeares-will
    #collect array sized information that well need later
    #debug
    baseLinks = []
    baseLinks = findHyperlinks(hostName) #initially the root level
    #fancyPrint('baseLinks: ',baseLinks) #debug

    scrapedPages = aggregator(urlInput, hostName, hostName) #scrapedPages is an array containing our first attempt at scraping, add more to this list if its under 10
    #debug
    #print'scrapedPages: ',scrapedPages
    scrapedPages = list(set(scrapedPages))
    if (len(scrapedPages) >= 10):
        fancyPrint('Try these fun activities(first try): ', scrapedPages) #done, so print
    elif (len(scrapedPages) < 10): #append a lot of links to our first attempt if it wasn't good enough
        downOneLevelLinks = filterByKeyword(baseLinks,['event','calendar']) #E.g. /exhib_events, /exhib_events/playartfully, /exhib_events/calendar, /exhib_events/archive, /get_involved/member_donor_events
        #fancyPrint('downOneLevelLinks: ', downOneLevelLinks)#debug
        for endpoint in downOneLevelLinks:
            if (len(scrapedPages) >= 10):
                #fancyPrint('before break -> scrapedPages: ', scrapedPages) #debug
                break
            fullUrl = hostName+endpoint;
            #print'fullUrl: ',fullUrl #debug
            activityPages = aggregator(urlInput, fullUrl, root)#hostname+endpoint = full url. 
            print'activityPages: ',activityPages #debug
            for endpoint in activityPages:
                scrapedPages.append(endpoint)
            scrapedPages = list(set(scrapedPages))    
        fancyPrint('Try these fun activities(second try): ', scrapedPages) #done, so print 
    else: 
        print 'Something went wrong at the very end'
        
    if (len(scrapedPages) < 10):#still less than 10
        moreScrapedPages = []
        for queryString in scrapedPages:
            stringAfterPop = queryString[:-2]
            for i in range(11,99):
                s = str(i)
                putBack = stringAfterPop + s
                a,b,c,d = putBack.split('/')
                relativeLink = '/'+d
                moreScrapedPages.append(relativeLink)
        moreScrapedPages = list(set(moreScrapedPages))
        for endpoint in moreScrapedPages:
            if (len(scrapedPages) >= 10):
                break
            fullUrl = hostName+endpoint;
            activityPages = aggregator(urlInput, fullUrl, root)#hostname+endpoint = full url. 
            for endpoint in activityPages:
                scrapedPages.append(endpoint)
            scrapedPages = list(set(scrapedPages))
    return scrapedPages
        

def hello(request):
    if request.method == 'GET':
        httpGet = request.GET.get('q', '')
        httpGet = 'http://'+httpGet
        list = []
        list = command(httpGet)
        newList = ''
        for item in list:
            newList += "<a href=\""
            newList += (str(item))
            newList += "\">"
            newList += (str(item))+"</a>"
            newList += "<br>"
            
            
        return HttpResponse("<p>Activity Pages: <br> " + newList + "</p>")
    elif request.method == 'POST':
        return HttpResponse("<h1><p>Whats up, world</p></h1>")
    
