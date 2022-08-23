# MVCLab-Summer-Course

### LineBot-Accounting
* **Date: 08/17**
    * **Start ngrok https server (default port:8787)**
        * > ngrok http 8787
        * > http://127.0.0.1:4040
    * **Step 2: Run main.py by uvicorn (default localhost:8787)**
        * > python main.py
* **How to run**
    * **#note [event] [+/-] [money]**
        * > Add new event
        * Example: #note 吃飯 - 200
    * **#report**
        * > Show all the records
    * **#delete [event] [+/-] [money]**
        * > Delete old event
        * > Event and money need to be identical to the event you added
        * Example: #delete 吃飯 - 200
    * **#sum [Time_duration]**
        * > Calculate the sum of money from now to Time_duration before
        * > Time_duration must be [number][s/m/h/d]
        * Example: 1d , 30m , 10h
    
