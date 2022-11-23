import requests
from bs4 import BeautifulSoup

from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
app = Flask(__name__)

@app.route("/")
def index():
    homepage = "<h1>資管二A陳咨穎的求職網頁</h1>"
    homepage += "<a href=/aboutme>我的個人簡介</a><br>"
    homepage += "<a href=/hello>相關工作介紹</a><br>"
    homepage += "<a href=/text>職涯測驗結果</a><br>"
    homepage += "<a href=/name>求職履歷自傳</a><br>"
    homepage += "<a href=/next>選修課程查詢</a><br>"
    homepage += "<br><a href=/movie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    return homepage

@app.route("/aboutme")
def aboutme():
    now = datetime.now()
    return render_template("aboutme.html", datetime = str(now))



@app.route("/hello")
def hello():
    now = datetime.now()
    return render_template("hello.html", datetime = str(now))



@app.route("/text")
def text():
    now = datetime.now()
    return render_template("text.html", datetime = str(now))

@app.route("/name")
def name():
    now = datetime.now()
    return render_template("name.html", datetime = str(now))


@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    user = request.values.get("nick")
    return render_template("welcome.html", name=user)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.methods == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號密碼是:" + user + ";密碼為:" + pwd
        return result
    else:
        return render_template("account.html")

@app.route("/next", methods=["GET", "POST"])
def next():
    if request.method == "POST":
        search = request.form["search"]
        teacher = request.form["teacher"]
        db = firestore.client()
        collection_ref = db.collection("111")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if search in dict["Course"] and teacher in dict["Leacture"]:
                #print("{}老師開的{}課程,每週{}於{}上課".format(dict["Leacture"], dict["Course"],  dict["Time"],dict["Room"]))
                result += dict["Leacture"] + "老師開的" + dict["Course"] + "課程,每週"
                result += dict["Time"] + "於" + dict["Room"] + "上課<br>"
        if result =="":
            result = "Sorry，查無相關條件的選修課程"   
        return result
    else:
        return render_template("next.html")
@app.route("/movie")
def movie():
    url = "http://www.atmovies.com.tw/movie/next/"
Data = requests.get(url)
Data.encoding = "utf-8"
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.select(".filmListAllX li")
info=""
rate=""
lastUpdate = sp.find("div", class_="smaller09").text[5:]
#print(result[2])
for x in result:
  picture = x.find("img").get("src").replace(" ", "")

  title = x.select("a")[1].text
  print("片名:"+title)
  movie_id = x.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")

  images = x.select("img")
  if len(images) == 1:
    rate = "尚無電影分級資訊"
  else:
    rate = images[1].get("src")
    if rate == "/images/cer_G.gif":
        rate = "普遍級(一般觀眾皆可觀賞)"
    if rate == "/images/cer_P.gif":
        rate = "保護級(未滿六歲之兒童不得觀賞，六歲以上未滿十二歲之兒童須父母、師長或成年親友陪伴輔導觀賞)"
    if rate == "/images/cer_F2.gif":
        rate = "輔導級(未滿十二歲之兒童不得觀賞)"
    if rate == "/images/cer_F5.gif":
        rate = "輔導級(未滿十五歲之人不得觀賞)"
    if rate=="/images/cer_R.gif":
      rate = "限制級(未滿十八歲之人不得觀賞)"

  #print("電影分級:" + rate + "\n")

    #temp = x.select(".runtime")[0]
    #temp = x.find(class_="runtime") #找第一個或找一個時適用
    #print(temp.text + "\n")
  #print("海報:" + x.find("img").get("src") + "\n")
    
  hyperlink = "http://www.atmovies.com.tw" + x.find("div", class_="filmtitle").find("a").get("href")
  show = x.find("div", class_="runtime").text.replace("上映日期：", "")
  show = show.replace("片長：", "")
  show = show.replace("分", "")
  showDate = show[0:10]
  showLength = show[13:]

  info  += picture + "\n" + title + "\n" + hyperlink + "\n"+showDate + "\n" +showLength+"\n\n"+"電影分級:" + rate + "\n"
  print(info)
  docs = [
  {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate,
        "rate":rate
    }
        ]
  collection_ref = db.collection("咨穎電影 ").document(movie_id)
  for doc in docs:
    collection_ref.set(doc)
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 




if __name__ == "__main__":
    app.run()
