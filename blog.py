from ast import Pass, keyword
import email
from operator import methodcaller
from MySQLdb import MySQLError
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request #web sunucumuzu ayağa kaldırmamızı sağlayacak.Render template içine templatemizi vererek templetemizi response olarak dönücez.
#flask bir template yazıyorsak direkt olarak templates adlı bir klasöre bakıyor. o yüzden templatelerimizi oraya yazıyoruz.
#jinja template flask tarafından kullanılan bir html templatesi. html css ve bootstrap modülümüzü kullanıyoruz.
from flask_mysqldb import MySQL #mysqle bağlanmak için dahil ettik 
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt #veritabanına şifreyi gönderirken biz görmeyeceğiz. 
from functools import wraps 

#kullanıcı giriş decarotorı 
def login_required(f): #burada bir kontrol yapıyoruz. session işlemi başlatıldıysa urlden direk dasboarda gidebiliyoruz
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:  # burada session işlemi true dönerse git diyor.
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın","danger") #burada session değeri false dönerse hata mesajı yazdır ve login ekranına gönder diyoruz.
            return redirect(url_for("login"))
    return decorated_function
    

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

class LoginForm(Form): #giriş formu oluşturuyoruz.
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
#makale sayfasının görüntülenmesi 
@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles"
    result = cursor.execute(sorgu)

    if result > 0:
        articles = cursor.fetchall() #fetchall fonksiyonu bütün makaleleri bize liste içinde sözlük olarak dönecek.
        return render_template("articles.html",articles=articles)

    else:
        return render_template("articles.html") #bunları article.htmle gönderdik ve for döngüsü yardımı ile bunları orada göstericez.




#dashboard 
@app.route("/dashboard") 
@login_required
def dashboard(): #kendi makalemi almak istiyorum ve bunları yönetilebilir bir şekilde dashboardımıza atmak istiyoruz
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles where author = %s"
    result = cursor.execute(sorgu,(session["username"],))
    if result > 0: 
        articles = cursor.fetchall()
        return render_template("dashboard.html",articles=articles)

    else: 
        return render_template("dashboard.html")



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
        return redirect(url_for("login")) #index fonksiyonuyla ilişkili olan url'ye gidiyor.Yani bizi index sayfasına atıcak. 
    else:
        return render_template("register.html", form = form) #yukarda oluşturduğumuz formu direkt register.html e gönderiyoruz.
#login işlemi 
@app.route("/login",methods=["GET","POST"])
def login():
    form = LoginForm(request.form) 
    if request.method == "POST": # burada methodumuz postsa bilgileri veritabanında sorgulayacağız.
        username = form.username.data
        password_entered = form.password.data 
        #burada formdaki bilgileri aldık ve veritabanında bunları sorgulayacağız.
        #bunun için önce veritabanında işlem yapmamızı sağlayan cursoru oluşturucaz. 
        cursor = mysql.connection.cursor() 

        sorgu = "Select * From users where username = %s" 
        result = cursor.execute(sorgu,(username,)) #değeri demet olarak dönmemiz gerek. Tek elemanlı demetlerde sonuna , koyuyoruz.
         #burda sorgumuz bir değer dönecek.Eğer usernamemiz varsa bir değer dönecek. Eğer kullanıcı yoksa 0 dönecek. 
        if result > 0: #result 0 dan büyük olduğunda böyle bir kullanıcı var demektir. burada girilen parola ile kullanıcının parolasını sorgulamamız gerekiyor.
            # yukarda app.config yaparken dictcursor yaparak yani sözlük yaptık o yüzden sözlükten alıcaz. 
            data = cursor.fetchone() # burada kullanıcının bütün bilgilerini almış oluyoruz.fetchone fonksiyonu bütün bilgileri al demek. 
            real_password = data["password"] # bilgileri aldıktan sonra bunların üzerinde sözlüklerde olduğu gibi gezebiliyoruz.Burada da veritabanında ki passwordumuzu alıyoruz. 
            if sha256_crypt.verify(password_entered,real_password): # sha256 modülünün içindeki verify fonksiyonu ile girdiğimiz password ile veritabanında ki passwordu karşılaştırıyoruz.
                flash("Başarıyla giriş yaptınız.","success") #eğer doğruysa bu bloğa giriyor, alertimizi success yapıyoruz ve redirect yaparak verdiğimiz url ye gönderiyoruz.

                session["logged_in"] = True 
                session["username"] = username 

                #login işlemimizde başarıyla giriş yaptıktan sonra indexe gitmeden sessionu başlatmamız gerekiyor.
                return redirect(url_for("index"))
            else: # eğer passwordumuz yanlışsa bu bloğa giricek ve tekrar redirect yaparak verdiğimiz url yi dönücek. 
                flash("Parola yanlış.","danger")
                return redirect(url_for("login"))
        else:
            #burada resultumuz 0 demektir.Yani böyle bir username yok demek. Böyle yerlerde de bir flash mesajı patlatmamız gerek.
            flash("Böyle bir kullanıcı bulunamadı.","danger")
            return redirect(url_for("login"))

    return render_template("login.html", form = form)

#Detay sayfası 
@app.route("/article/<string:id>")
def article(id):
    cursor = mysql.connection.cursor() # burada bağlantıyı yaptık 
    sorgu = "Select * from articles where id = %s"  # burada veritabanından id leri almak istediğimizi söylüyoruz.
    result = cursor.execute(sorgu,(id,)) 

    if result > 0: #burada id'miz 0'dan büyükse yani böyle bir article varsa bu bloğa giriyor.
        article = cursor.fetchone()
        return render_template("article.html",article=article)

    else:
        return render_template("article.html")






#logout işlemi 
@app.route("/logout")
def logout():
    session.clear() # sessionu temizliyoruz ve çıkış yapıyor.
    return redirect(url_for("index"))

@app.route("/article/<string:id>") # burada herhangi bir id yazıldığında bu id yi bunun altına yazılan fonksiyondan almak istiyoruz. id'nin string olduğunu ve bunun da id değişkeninde tutulduğuınu söylüyoruz.
def detail(id): #böylece bunu yazarak id yazdığımızda veritabanına gidip o id deki veriyi çekicek
    return "Article id: " + id

#makale ekleme 
@app.route("/addarticle",methods=["GET","POST"])
def addarticle():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        cursor = mysql.connection.cursor()

        sorgu = "Insert Into articles(title,author,content) Values(%s,%s,%s) " 
        cursor.execute(sorgu,(title,session["username"],content))
        mysql.connection.commit() #veritabanında değişiklik yapacağımız için commit işlemi yapacağız.
        cursor.close()
        flash("Makale Başarıyla Eklendi","success")
        return redirect(url_for("dashboard"))

    return render_template("addarticle.html",form = form) 

# Makale silme 
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()

    sorgu = "Select * from articles where author = %s and id = %s"

    result = cursor.execute(sorgu,(session["username"],id))
    
    if result > 0:
        sorgu2 = "Delete from articles where id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        return redirect(url_for("dashboard"))
    else:
        flash("Böyle bir makale yok veya böyle bir yetkiniz yok. ","danger")
        return redirect(url_for("index"))

#Makale Güncelleme
@app.route("/edit/<string:id>",methods = ["GET","POST"])
@login_required
def update(id):
   if request.method == "GET":
       cursor = mysql.connection.cursor()

       sorgu = "Select * from articles where id = %s and author = %s"
       result = cursor.execute(sorgu,(id,session["username"]))

       if result == 0:
           flash("Böyle bir makale yok veya bu işleme yetkiniz yok","danger")
           return redirect(url_for("index"))
       else:
           article = cursor.fetchone()
           form = ArticleForm()

           form.title.data = article["title"]
           form.content.data = article["content"]
           return render_template("update.html",form = form)

   else:
       # POST REQUEST
       form = ArticleForm(request.form)

       newTitle = form.title.data
       newContent = form.content.data

       sorgu2 = "Update articles Set title = %s,content = %s where id = %s "

       cursor = mysql.connection.cursor()

       cursor.execute(sorgu2,(newTitle,newContent,id))

       mysql.connection.commit()

       flash("Makale başarıyla güncellendi","success")

       return redirect(url_for("dashboard"))

       pass
        
        




# makale formu 
class ArticleForm(Form):
    title = StringField("Makale Başlığı",validators=[validators.length(min=5,max=100)])
    content = TextAreaField("Makale içeriği",validators=[validators.length(min=10)])

# Arama URL
@app.route("/search",methods = ["GET","POST"])
def search():
   if request.method == "GET":
       return redirect(url_for("index"))
   else:
       keyword = request.form.get("keyword")

       cursor = mysql.connection.cursor()

       sorgu = "Select * from articles where title like '%" + keyword +"%'"

       result = cursor.execute(sorgu)

       if result == 0:
           flash("Aranan kelimeye uygun makale bulunamadı...","warning")
           return redirect(url_for("articles"))
       else:
           articles = cursor.fetchall()

           return render_template("articles.html",articles = articles)


if __name__ == "__main__":
    app.run(debug=True) #debug=True yaptığımızda kodda bir değişiklik yaptığımız zaman sunucuyu yeniden çalıştırmamıza gerek yok. otomatik yeniliyor kendini. 
 