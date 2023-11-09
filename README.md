# adCreative.ai Case Çözüm
TODO:
- Parametreleri environment degiskeni olarak gec.
- Endpoint'lardaki parametreler icin dogrulama yaz.
- Image boyutunu dusur.

## Task1
Stable Diffusion’un Img2Img algoritmasını kullanarak verilen görsele benzer yeni
bir görsel üretmek. Bunu seçeceğiniz hazır bir modelle yapabilirsiniz. Üretilen görselde
bizim verdiğimiz bir rengin de kullanılmasını bekliyoruz.

### Çözüm
Promt ve görsel kabul eden bir model istenmiş. Bu yüzden bir ControlNet kullanmayı tercih ettim. Bu sayede Stable Diffusion modelleri uzerinde kontrol sağlanabilir. Kullandığım checkpoint *Canny Edge* üzerinden ControlNet'i şartlar. Model card'a [buradan](https://huggingface.co/lllyasviel/sd-controlnet-canny) ulaşılabilir.

Bu modeli kullanabilmek icin oluşturulan pipeline bir Canny Image ihtiyaci duyar. Bu yuzden bir on işleme operasyonu vardir. Bu operasyon `core.py` icinde implement edilmistir. `generate_image` fonksiyonunun son satiri haric, tum satirlari bu operasyona hizmet eder.

Kullanici bu modeli kullanabilmek icin `/paint` endpoint'ini kullanabilir. Bu endpoint aşağidaki parametrelere ihtiyac duyar:
1. Image, file
2. Prompot, string
3. Theme Color, string

Burada `fastapi` ve `ray` frameworkleri kullanilmiştir. Birden fazla kullanicinin ayni anda inference yapabilmesi icin `ray serve` tercih edilmistir. 

Bu endpoint uygulamanin calistigi cihazin filesystem'i uzerinde `lightroom` klasoru altinda `raw_image` ve `generated_image` adinda iki png dosyasi olusturur. Uygulama kapandiginda bu klasor temizlenir. Bu save operasyonlari performans icin dezavantajdir ancak implementasyon kolayligi sagladigi icin terich edilmistir. Ayrica filesystem olarak S3 gibi object storage cozumleri de tercih edilebilirdi ancak basitlik icin tercih edilmedi. 

Uretilen gorselin kaydedilmesi ve diger endpointlere sunulmasi API consumer tarafindan gerceklestirilmelidir, bu uygulama state saklamamaktadir.

## Task 2 
Üretilen görseli ve diğer inputları kullanarak basit bir dinamik reklam template’i üretmek. En tepede logo, ortada görsel, altında punchline ve en altta button olacak şekilde tasarlayabilirsiniz. Button’un ve punchline’ın rengi ayrı bir input olarak verilecek. Aşağıdaki örnek görsele çok benzer bir çıktı üretmenizi bekliyoruz.

### Çözum
Bu islevi dinamik yolla ve ozellestirilebilir sekilde halletmek icin `jinja2` kutuphanesi kullanilmistir. Bu kutuphane bir html template ve arguman dictionary'si kabul eder ve bir html dosyasi render eder. Bunu png veya svg olarak export edebilmek icin `imgkit` adli kutuphane kullanilmistir. Elde edilmek istenen son gorsele ait tempalte `templates` klasoru altinda `jinja2` template syntax'e uygun olarak yazilmis `basic.hmtl` dosyasi icinde bulunur. Daha sonrasinda bu dosya uzerinde yapilan ozellestirmeler ve stil degisiklikleri endpoint'in ciktisini degistirecektir. 

Kullanicilar bu fonksiyonalite icin `/generate` endpoint'ine `POST` istegi gonderebilir. Gerekli parametreler asagidaki gibidir:
1. AI Generated Image, file
2. Logo, file
3. Theme Color, string
4. Punchline, string
5. Button Text, string

Bu endpoint handler'i logo ve resimi filesystem uzerine kaydeder. `core` icindeki `generate_ad` fonksiyonu ile `lightroom/output.png` dosyasina elde edilmek istenilen gorsel yazilir. Ayni endpoint bu dosyayi gonderir.

## Task 3
Tasarladığınız bu sistemi cloud üzerinde veya kendi bilgisayarınızı kullanarak deploy etmenizi ve API yoluyla ulaşılabilir olmasını istiyoruz. Bunun için istediğiniz teknolojik altyapıları kullanabilirisiniz. API yoluyla bahsedilen inputları alacak ve reklam görseli döndürecek bir yapı kurmanızı bekliyoruz.

### Çözüm
Daha uyumlu bir uygulama elde etmek icin butun uygulama icin bir `Dockerfile` yazilmistir ve build edilerek `docker run -p 8000:8000 -p 8265:8265 ray-serve-app` komutu ile kullanilabilir. Burada port 8000 endpoint'ler icindir ve port 8265 `ray cluster` dashboard'ina erismek icin kullanilir. Bu dashboard uzerinde mevcut cluster'lar ve calisan uygulama instance'lari gozlemlenebilir. Ayni zamanda node kaynaklari hakkinda bilgi alinabilir ve harici log mekanizmalari entegre edilebilir. 

Uygulama icin tercih edilen `replica` sayisi `app.py` icindeki `@serve.deployment` decorator'u icinde de build islemi oncesinde belirtileblilr. Daha sonraki asamalarda bu parametrelerin image'a ortam degiskeni olarak sunulmasi daha kullanisli olacaktir.

