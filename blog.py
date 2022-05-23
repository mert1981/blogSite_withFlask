import email
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request #web sunucumuzu ayağa kaldırmamızı sağlayacak.Render template içine templatemizi vererek templetemizi response olarak dönücez.
#flask bir template yazıyorsak direkt olarak templates adlı bir klasöre bakıyor. o yüzden templatelerimizi oraya yazıyoruz.
#jinja template flask tarafından kullanılan bir html templatesi. html css ve bootstrap modülümüzü kullanıyoruz.
from flask_mysqldb import MySQL #mysqle bağlanmak için dahil ettik 
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt #veritabanına şifreyi gönderirken biz görmeyeceğiz. 

#kullanıcı kayıt formu 
class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min = 4,max = 25)])
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min = 5,max = 35)])
    email = StringField("Email Adresi",validators=[validators.Email(message = "Lütfen Geçerli Bir Email Adresi Girin...")])
    password = PasswordField("Parola:",validators=[
        validators.DataRequired(message = "Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname = "confirm",message="Parolanız Uyuşmuyor...")
    ])
    confirm = PasswordField("Parola Doğrula")
class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")
app = Flask(__name__)
app.secret_key= "ybblog"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)
@app.route("/") # bu adrese gitmek istiyoruz diyoruz ve adresi buraya yazıyoruz ve bu adrese bir response dönmek istiyoruz
def index(): 
    return render_template("index.html") #render template diyerek ve içine bir template göndererek onu response olarak dönüyor. 
    #template yazdığımız zaman önce templates klasör,üne bakıyor.

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/article/<string:id>") # burada herhangi bir id yazıldığında bu id yi bunun altına yazılan fonksiyondan almak istiyoruz. id'nin string olduğunu ve bunun da id değişkeninde tutulduğuınu söylüyoruz.
def detail(id): #böylece bunu yazarak id yazdığımızda veritabanına gidip o id deki veriyi çekicek
    return "Article id: " + id


if __name__ == "__main__":
    app.run(debug=True) #debug=True yaptığımızda kodda bir değişiklik yaptığımız zaman sunucuyu yeniden çalıştırmamıza gerek yok. otomatik yeniliyor kendini. 
 