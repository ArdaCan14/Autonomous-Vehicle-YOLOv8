import socket  # Python'un standart ağ haberleşme kütüphanesi

class ESP32Comm:
    """
    Bu sınıf, Python (Brain) ve ESP32 (Araba) arasındaki 
    çift yönlü UDP köprüsünü yönetir.
    """
    
    def __init__(self, esp32_ip, send_port=1234, recv_port=1235):
        # 1. Ayarlar: ESP32'nin router'dan aldığı IP ve port numaraları
        self.esp32_address = (esp32_ip, send_port)
        self.recv_port = recv_port
        
        # 2. Socket Oluşturma: AF_INET (IPv4), SOCK_DGRAM (UDP protokolü)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # 3. Dinleme Ayarı: Bilgisayarın kendi üzerindeki portu rezerve eder.
        # "" ifadesi 'tüm ağ arayüzlerini dinle' demektir.
        self.sock.bind(("", self.recv_port))
        
        # 4. Non-Blocking Modu: Bu ÇOK KRİTİK. 
        # Eğer veri gelmezse programın "beklemesini" engeller, akışı durdurmaz.
        self.sock.setblocking(False)

    def send_command(self, action, speed, steering):
        """
        Brain.py'dan gelen kararları paketleyip ESP32'ye gönderir.
        Format: "AKSIYON:HIZ:DIREKSIYON" (String formatı parçalaması kolaydır)
        """
        # Veriyi bir string haline getiriyoruz (Örn: "MANEUVER_LEFT:25:-1")
        message = f"{action}:{speed}:{steering}"
        
        try:
            # UDP üzerinden veriyi byte formatına çevirip (encode) gönderiyoruz
            self.sock.sendto(message.encode('utf-8'), self.esp32_address)
        except Exception as e:
            print(f"⚠️ Veri gönderme hatası: {e}")

    def receive_distance(self):
        """
        ESP32'den (Sensörlerden) gelen mesafe verisini okur.
        """
        try:
            # Gelen veriyi 1024 byte'lık tampon belleğe (buffer) alıyoruz
            data, addr = self.sock.recvfrom(1024)
            # Byte veriyi okunabilir yazıya (string) çeviriyoruz
            return data.decode('utf-8') 
        except BlockingIOError:
            # Eğer o milisaniyede yeni bir veri gelmemişse hata verme, None dön.
            return None
        except Exception as e:
            print(f"⚠️ Veri alma hatası: {e}")
            return None