Python version: 2.7.7

How to use:
    1. Install python 2.7.7 and required packages
    2. Install Django
    3. C:\<workspace>\server\mysite>python manage.py runserver
            Default port is 8000
    4. Main code is written on server\mysite\myapp\views.py. 
       http://localhost:8000/?q=events.stanford.edu/events/353/35309/
       http://localhost:8000/?q=calendar.boston.com/lowell_ma/events/show/274127485-mrt-presents-shakespeares-will
       http://localhost:8000/?q=workshopsf.org/?page_id=140&id=1328'
       http://localhost:8000/?q=sfmoma.org/exhib_events/exhibitions/513
       

Required packages for python: 
    pip: If on linux, install pip the standard method
    pip: http://stackoverflow.com/questions/4750806/how-to-install-pip-on-windows
         1. If installing on windows, Download get-pip.py, being careful to save it as a .py file
            rather than .txt (pip.py: https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py)
         2. Place get-pip.py where python.exe is located. Then execute python get-pip.py
         3. Should install it to C:/<python-directory>/Scripts
         4. In that directory, execute 
               pip install beautifulsoup4
               pip install urllib3
               pip install requests
               pip install Django==1.6.5
     Beautiful Soup 4: included above
     Urllib3: included above
     Requests: included above
     Django: included above
     
Criteria:
    Precision: All URLs returned in the four given pages return an activity. 
    Scalability: Works well on the following alternate sites. 
                    /?q=lacma.org/event/louie-beltran
                    /?q=mfah.org/calendar/hard-days-night/9653/
                 With more time, I would have implemented
                 better adapted regexes to handle time, date, location, pricing. If those four fields
                 are placed next to a large paragraph description, it's very likely to be at the page
                 specific to that event. That's because a list of events in a "upcoming events calendar" 
                 would not be able to fit large paragraph descriptions for each event. 
    Simplicity: Computationally efficient because it aims to minimize the number of pages searched. 3-step 
                 process that returns well formatted pages fast. If it can't find at least 10, 
                 it will broaden its search breadth and depth.
    Simplicity: Used only one language (Python 2.7.7). 
    
    