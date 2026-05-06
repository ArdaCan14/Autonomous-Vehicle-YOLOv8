# Autonomous-Vehicle-YOLOv8
Yüksek Hassasiyetli ve Düşük Gecikmeli Otonom Sürüş Ekosistemi
Bu proje, Derin Öğrenme (Deep Learning) ve Gömülü Sistemler (Embedded Systems) teknolojilerini harmanlayan, yüksek hızlı Wi-Fi tabanlı bir otonom araç mimarisidir. Projenin temel amacı; karmaşık trafik senaryolarını gerçek zamanlı olarak analiz etmek ve milisaniyeler içinde karar verme mekanizmalarını tetiklemektir.

1. Algı Katmanı: YOLOv8 & 55,000 Görüntülük Veri Seti
Model: Nesne algılama dünyasının en güncel ve hızlı mimarilerinden biri olan YOLOv8 kullanılmaktadır.

Veri Seti: Model, trafik işaretleri, engeller ve yol geometrisini en yüksek doğrulukla tanıyabilmesi için 55.000'den fazla yüksek çözünürlüklü ve etiketlenmiş görselden oluşan kapsamlı bir veri kümesiyle eğitilmiştir.

Optimizasyon: Eğitim süreci, modelin değişken ışık ve hava koşullarında bile yüksek mAP (Mean Average Precision) skorları üretmesini sağlayacak şekilde optimize edilmiştir.

2. İletişim ve İşleme Mimarisi: 5GHz Ultra-Low Latency
Görüntü Aktarımı: Görüntü kaynağı olarak endüstriyel segmentteki Hikvision DS-2CD1123G2-LIUF IP kamera kullanılmaktadır.

Ağ Altyapısı: Geleneksel 2.4GHz bandındaki tıkanıklıkları aşmak için sistem, 5GHz yüksek bant genişliğine sahip bir router (GL.iNet Mango vb.) üzerinden haberleşir. Bu sayede RTSP üzerinden gelen görüntü akışı, minimum gecikmeyle işleme birimine (PC) ulaştırılır.

Karar Mekanizması: Laptop üzerinde (NVIDIA GTX 1650 GPU desteğiyle) işlenen veriler, anlık olarak otonom sürüş kararlarına dönüştürülür ve UDP/TCP protokolleri üzerinden araçtaki kontrolcüye gönderilir.

3. Donanım ve Güç Yönetimi: İzolasyonlu Çift Kanallı Güç Sistemi
Kontrol Birimi: Aracın mekanik kontrolü ve ağ geçidi görevini ESP32 mikrodenetleyicisi üstlenir.

Güç Mimarisi: Sistemde elektriksel gürültüyü (noise) engellemek için güç hatları birbirinden ayrılmıştır.

Lojistik Katman: ESP32 ve ağ birimleri bir Powerbank üzerinden beslenir.

Mekanik Katman: 4 adet DC motor ve TB6612FNG motor sürücüsü, yüksek akım kapasitesine sahip 7.4V seri bağlı Li-ion 18650 pil paketi ile beslenerek maksimum tork ve sürüş stabilitesi sağlanır.
