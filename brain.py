class AutonomousBrain:
    def __init__(self):
        # --- EŞİK DEĞERLERİ (Kalibrasyon Gerektirebilir) ---
        self.HARD_STOP_DIST = 30       # Fiziksel Engel (cm)
        self.LIVING_DANGER_AREA = 4000 # Canlı Çok Yakın (Piksel)
        self.LIVING_CAUTION_AREA = 800 # Canlı İleride (Piksel)
        self.LIGHT_NEAR_AREA = 3200    # Işık Dibimizde (Piksel)
        
        # --- DURUM DEĞİŞKENLERİ ---
        self.current_distance = 999    
        self.target_speed_limit = 65   # Genel hız sınırı
        self.steering_angle = 0        # 0: Düz, -1: Sol, 1: Sağ

    def update_distance(self, dist):
        """UDP'den gelen mesafeyi günceller."""
        self.current_distance = float(dist)

    def decide(self, detections):
        """
        detections: [{'label': 'red', 'bbox': [x1, y1, x2, y2]}, ...]
        Return: (Aksiyon, Hız, Direksiyon)
        """
        dist = self.current_distance
        labels_in_frame = [obj['label'] for obj in detections]

        # --- 1. KATMAN: SENSÖR GÜVENLİĞİ (EN ÜST ÖNCELİK) ---
        if dist <= self.HARD_STOP_DIST:
            return "EMERGENCY_STOP_SENSOR", 0, 0

        # --- 2. KATMAN: CANLI VARLIK GÜVENLİĞİ (YOLO + SENSÖR HİBRİT) ---
        # 54k veri setiyle Person, Cat, Dog tespiti
        living = [obj for obj in detections if obj['label'] in ['person', 'cat', 'dog']]
        if living:
            best_living = max(living, key=lambda x: (x['bbox'][2]-x['bbox'][0]) * (x['bbox'][3]-x['bbox'][1]))
            area = (best_living['bbox'][2] - best_living['bbox'][0]) * (best_living['bbox'][3] - best_living['bbox'][1])
            
            if area > self.LIVING_DANGER_AREA: 
                return "LIVING_STOP", 0, 0
            elif area > self.LIVING_CAUTION_AREA: 
                return "LIVING_SLOW", 20, 0  # Erken yavaşlama (Konforlu sürüş)

        # --- 3. KATMAN: YASAKLAYICI TABELALAR ---
        if 'noentry_sign' in labels_in_frame: 
            return "NO_ENTRY_STOP", 0, 0
        
        # Dönüş yasaklarını kontrol et
        no_left = 'donotturnleft_sign' in labels_in_frame
        no_right = 'donotturnright_sign' in labels_in_frame

        # --- 4. KATMAN: MANEVRA VE DÖNÜŞLER ---
        if 'turnleft_sign' in labels_in_frame and not no_left:
            return "MANEUVER_LEFT", 25, -1 # Yavaşla ve sola kır
        
        if 'turnright_sign' in labels_in_frame and not no_right:
            return "MANEUVER_RIGHT", 25, 1  # Yavaşla ve sağa kır
            
        if 'keepleft_sign' in labels_in_frame: return "KEEP_LEFT", 40, -0.5
        if 'keepright_sign' in labels_in_frame: return "KEEP_RIGHT", 40, 0.5

        # --- 5. KATMAN: TRAFİK IŞIĞI MANTIĞI ---
        lights = [obj for obj in detections if obj['label'] in ['red', 'yellow', 'green', 'off']]
        if lights:
            best_light = max(lights, key=lambda x: (x['bbox'][2]-x['bbox'][0]) * (x['bbox'][3]-x['bbox'][1]))
            label = best_light['label']
            area = (best_light['bbox'][2] - best_light['bbox'][0]) * (best_light['bbox'][3] - best_light['bbox'][1])
            
            if label == 'red':
                if area > self.LIGHT_NEAR_AREA: return "RED_STOP", 0, 0
                return "RED_SLOWING", 20, 0
            elif label == 'yellow':
                if area > self.LIGHT_NEAR_AREA: return "YELLOW_PASS", 40, 0
                return "YELLOW_PREPARE", 15, 0
            elif label == 'off': return "LIGHTS_OFF_CAUTION", 30, 0

        # --- 6. KATMAN: HIZ SINIRLARI VE STOP TABELASI ---
        if 'stop_sign' in labels_in_frame: 
            return "STOP_SIGN", 0, 0
            
        if 'speed30_sign' in labels_in_frame: 
            self.target_speed_limit = 30
        elif 'speed50_sign' in labels_in_frame: 
            self.target_speed_limit = 50

        # --- 7. KATMAN: TAKİP MESAFESİ (DİĞER ARAÇLAR) ---
        if any(x in labels_in_frame for x in ['car', 'bus', 'truck', 'motorcycle', 'bicycle']):
            if dist < 150: 
                return "VEHICLE_FOLLOWING_SLOW", 25, 0
            return "VEHICLE_FOLLOWING", 45, 0

        # --- 8. KATMAN: YOL TEMİZ (VARSA TABELA HIZINA GÖRE) ---
        return "CRUISE_CONTROL", self.target_speed_limit, 0