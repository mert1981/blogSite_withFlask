from flask import Flask,render_template #web sunucumuzu ayağa kaldırmamızı sağlayacak.Render template içine templatemizi vereerek templetemizi response olarak dönücez.
#flask bir template yazıyorsak direkt olarak templates adlı bir klasöre bakıyor. o yüzden templatelerimizi oraya yazıyoruz.

app = Flask(__name__) #python dosyasını direkt terminalden çağırırsak namenin değeri main olacak.

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True) #debug=True yaptığımızda kodda bir değişiklik yaptığımız zaman sunucuyu yeniden çalıştırmamıza gerek yok. otomatik yeniliyor kendini. 
