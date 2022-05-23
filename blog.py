from ast import Pass
import email
from operator import methodcaller
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
    password = PasswordField("Parola",validators=[
        validators.DataRequired(message = "Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname = "confirm",message="Parolanız Uyuşmuyor...")
    ])
    confirm = PasswordField("Parola Doğrula")

class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")

app = Flask(__name__)
app.secret_key= "yg_blog" #flash mesajlarını kullanabilmek için  uygulamalarımızın secret_keyinin olması

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "yg_blog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)
@app.route("/") # bu adrese gitmek istiyoruz diyoruz ve adresi buraya yazıyoruz ve bu adrese bir response dönmek istiyoruz
def index(): 
    return render_template("index.html") #render template diyerek ve içine bir template göndererek onu response olarak dönüyor. 
    #template yazdığımız zaman önce templates klasör,üne bakıyor.

@app.route("/about")
def about():
    return render_template("about.html")

# Biz bir sayfaya ulaştığımızda get request yapmış oluyoruz. get request yaptığımızda server bunu anlıyor ve o sayfanın html içeriğini döndürüyor.
# bide post requestimiz var. post request herhangi bir formu submit ettiğimizde oluşacak http request türü.
#register sayfası 
@app.route("/register",methods = ["GET","POST"]) #burada iki türlü request alabileceiğini söyledik. söylemezsek hata döner.
def register():
    form = RegisterForm(request.form) #Post request yapıldığında formun içindeki bütün verileri almak için yukarda dahil ettiğimiz request içindeki formu kullanmamız gerekiyor.
    #sayfamıza bir request atılmışsa ve bu post requestse bunun içindeki tüm bilgiler bu register formuna yerleşcek ve bu form üzerinden veritabanına kaydedicez.
    if request.method == "POST" and form.validate(): #validate methodu formumuzda bir sıkıntı yoksa true dönücek ve biz aşağıdaki bloğa giricez.Eğer sıkıntı varsa false dönücek.
        #eğer bu sayfamıza bir post request yapılmışsa bu bloğa giricek.
        #formumuzda bir sıkıntı yoksa ve methodumuz postsa artık formdaki bilgileri alıcaz ve mysqle bağlanıcaz.
        name = form.name.data 
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data) # sha256 crypt içindeki encrypt fonksiyonu ile passwordu şifreleyip kaydediyor.
        # formdaki bilgileri aldık ve şimdi mysqle bağlanmamız gerekiyor.
        cursor = mysql.connection.cursor() #mysql üzerinde işlem yapmamız için gereken cursoru oluşturuyoruz
        sorgu = "Insert Into users (name,email,username,password) VALUES(%s,%s,%s,%s)" #eklemek istediimiz değerleri %s yazarak gönderiyoruz.
        cursor.execute(sorgu,(name,email,username,password)) #cursor.execute diyerek sql sorgusunun çalıştırmak istediğimizi söylüyoruz. sorgumuzu yazıp değerlerimizi giriyoruz.
        mysql.connection.commit() #veritabanında herhangi bir değişiklik yapmak istiyorsak güncelleme silme gibi bu commiti kullanmamız gerekiyor.
        cursor.close() #değişiklik yaptıkran sonra mysql bağlantısını kapatıyoruz.Arakdaki kaynakların gereksiz kullanılmaması için gayet önemli oluyor.
        #formadan aldığımız veriler mysqle eklendi. 
        flash("Başarıyla kayıt oldunuz","success") # sayfada post request oldğunda flash yapıyoruz ve index sayfasına get yapıyoruz.
        return redirect(url_for("index")) #index fonksiyonuyla ilişkili olan url'ye gidiyor.Yani bizi index sayfasına atıcak. 
    else:
        return render_template("register.html", form = form) #yukarda oluşturduğumuz formu direkt register.html e gönderiyoruz.
     
@app.route("/article/<string:id>") # burada herhangi bir id yazıldığında bu id yi bunun altına yazılan fonksiyondan almak istiyoruz. id'nin string olduğunu ve bunun da id değişkeninde tutulduğuınu söylüyoruz.
def detail(id): #böylece bunu yazarak id yazdığımızda veritabanına gidip o id deki veriyi çekicek
    return "Article id: " + id


if __name__ == "__main__":
    app.run(debug=True) #debug=True yaptığımızda kodda bir değişiklik yaptığımız zaman sunucuyu yeniden çalıştırmamıza gerek yok. otomatik yeniliyor kendini. 
 