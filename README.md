# MVCLab-Summer-Course

### This is 2022 MVCLab Summer Vacation Training Courses.

## Course Review

### AWS (Amazon Web Server)
* **Date: 08/09**

### FastAPI
* **Date: 08/11**
* **How to run**
    * **Step 1: Install Python Packages**
        * > pip install -r requirements.txt
    * **Step 2: Run by uvicorn (Localhost)**
        * > uvicorn main:app --reload
        * Default host = 127.0.0.1, port = 8000
    * **Step 3: Test your API using Swagger UI**
        * http://127.0.0.1:8000/docs
### LineBot
* **Date: 08/17**
* **How to run**
    * **Step 0: Go to main path**
        * > cd ./MVCLab-Summer-Course/LineBot
    * **Step 1: Install Python Packages**
        * > pip install -r requirements.txt
    * **Start ngrok https server (default port:8787)**
        * > ngrok http 8787
        * > http://127.0.0.1:4040
    * **Step 2: Run main.py by uvicorn (default localhost:8787)**
        * > python main.py