#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <Adafruit_Fingerprint.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <esp_system.h>  // 🔎 para esp_reset_reason()
#include <LittleFS.h>
#define MEMORY_FILE "/members.csv"
#define MASTER_TEMPLATES "/master_templates.dat"
// ===================== CONFIG WIFI =====================
//const char* ssid = "GYM.EVOLUTION";
//const char* password = "Gym50263";

const char* ssid = "ALEXA_QUINTERO";
const char* password = "yuki551222";

// URL del backend Flask
const char* backend_url = "http://192.168.100.181:8000/api";
String lastMessage = "";
// ===================== RELÉ =====================
#define RELAY_PIN 5
#define RELAY_ACTIVE_HIGH 0        // pon 0 si tu módulo es activo en LOW CAMBIAR A 1
const uint32_t RELAY_MAX_MS = 2000;  // por recomendación del fabricante

bool relayOn = false;
uint32_t relayStartMs = 0;
uint32_t relayDurationMs = 0;

inline void relayWrite(bool on) {
  if (RELAY_ACTIVE_HIGH) {
    digitalWrite(RELAY_PIN, on ? HIGH : LOW);
  } else {
    digitalWrite(RELAY_PIN, on ? LOW : HIGH);
  }
}

void beginRelaySafeState() {
  pinMode(RELAY_PIN, OUTPUT);
  relayWrite(false);
}

void pulseRelay(uint32_t ms) {
  if (ms == 0) ms = 1000;
  if (ms > RELAY_MAX_MS) ms = RELAY_MAX_MS;  // nunca exceder 2s
  relayDurationMs = ms;
  relayStartMs = millis();
  relayOn = true;
  relayWrite(true);
  // Si sospechas que el UART del sensor acopla ruido, puedes:
  // mySerial.end();
}

void handleRelayPulseLoop() {
  if (relayOn && (millis() - relayStartMs >= relayDurationMs)) {
    relayWrite(false);
    relayOn = false;
    // Reabrir el puerto si lo cerraste arriba:
    // mySerial.begin(57600, SERIAL_8N1, 16, 17);
  }
}

// ===================== OLED =====================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// ===================== Sensor huella =====================
HardwareSerial mySerial(2);  // RX=16, TX=17
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

// ===================== WebServer =====================
WebServer server(80);

//*************************Biometric Icons*********************************
// (Dejé tus bitmaps tal cual. Si cambias alguno, respeta dimensiones)
#define Wifi_start_width 54
#define Wifi_start_height 49
const uint8_t PROGMEM Wifi_start_bits[] = { }

#define Wifi_connected_width 63
#define Wifi_connected_height 49

const uint8_t PROGMEM Wifi_connected_bits[] = { };


#define FinPr_start_width 64
#define FinPr_start_height 64
const uint8_t PROGMEM FinPr_start_bits[] = { };

#define FinPr_valid_width 64
#define FinPr_valid_height 64
const uint8_t PROGMEM FinPr_valid_bits[] = { };

#define FinPr_invalid_width 64
#define FinPr_invalid_height 64
const uint8_t PROGMEM FinPr_invalid_bits[] = { };


#define FinPr_failed_width 64
#define FinPr_failed_height 64
const uint8_t PROGMEM FinPr_failed_bits[] = {};

#define FinPr_scan_width 64
#define FinPr_scan_height 64
const uint8_t PROGMEM FinPr_scan_bits[] = { };
//************************************************************************


//************************************************************************

// ===================== Forward declarations =====================
void handleEnroll();
bool enrollFingerprint(int id);
void sendToBackend(int template_id, String user_id);
void checkFingerprint();
void validateFingerprint(int template_id);
int getFreeTemplateID();
void handleResetFingerprints();
void handleStatus();

void showMessage(String message) {
  return;
  if (message == lastMessage) return;  // no redibujar lo mismo
  lastMessage = message;
  display.clearDisplay();

  if (message.startsWith("Sensor OK") || message.startsWith("Huella reconocida") || message.startsWith("Pon dedo otra vez") || message.startsWith("Error registro huella") || message.startsWith("Huella registrada") || message.startsWith("Quita el dedo")) {
    display.setTextSize(2);
  } else {
    display.setTextSize(1);
  }

  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println(message);

  if (message.startsWith("Sensor OK")) {
    display.drawBitmap(35, 10, FinPr_start_bits, FinPr_start_width, FinPr_start_height, WHITE);
  } else if (message.startsWith("Huella reconocida")) {
    display.drawBitmap(35, 10, FinPr_valid_bits, FinPr_valid_width, FinPr_valid_height, WHITE);
  } else if (message.startsWith("No autorizado")) {
    display.drawBitmap(35, 10, FinPr_invalid_bits, FinPr_invalid_width, FinPr_invalid_height, WHITE);
  } else if (message.startsWith("Huella no encontrada")) {
    display.drawBitmap(35, 10, FinPr_failed_bits, FinPr_failed_width, FinPr_failed_height, WHITE);
  } else if (message.startsWith("Pon tu dedo")) {
    display.drawBitmap(35, 10, FinPr_scan_bits, FinPr_scan_width, FinPr_scan_height, WHITE);
  }

  display.display();
}

void printResetReason() {
  esp_reset_reason_t r = esp_reset_reason();
  Serial.print("🔎 Reset reason: ");
  Serial.println((int)r);  // 1=POWERON, 3=SW, 5=DEEPSLEEP, 6=BROWNOUT, etc.
}

bool downloadTemplateToBuffer(uint8_t* buffer) {
  uint8_t p = finger.getModel();
  if (p != FINGERPRINT_OK) return false;

  p = finger.downloadModel();
  if (p != FINGERPRINT_OK) return false;

  uint16_t index = 0;
  uint32_t start = millis();
  while (index < 512 && (millis() - start < 1500)) {
    if (mySerial.available()) {
      buffer[index++] = mySerial.read();
    }
  }
  return (index == 512);
}

// Compara dos templates byte a byte con un umbral de tolerancia
int compareSoftwareTemplates(uint8_t* current, uint8_t* saved) {
  int score = 0;
  for (int i = 0; i < 512; i++) {
    if (abs(current[i] - saved[i]) < 12) { // Tolerancia al ruido del sensor
      score++;
    }
  }
  return score; // Umbral de éxito sugerido > 380
}

// Busca en el archivo binario de LittleFS
int searchInLittleFS() {
  uint8_t currentFinger[512];
  if (!downloadTemplateToBuffer(currentFinger)) return -1;

  File file = LittleFS.open(MASTER_TEMPLATES, FILE_READ);
  if (!file) return -1;

  int foundID = -1;
  while (file.available()) {
    int savedID;
    uint8_t savedTemplate[512];
    
    if (file.read((uint8_t*)&savedID, sizeof(savedID)) != sizeof(savedID)) break;
    if (file.read(savedTemplate, 512) != 512) break;

    int score = compareSoftwareTemplates(currentFinger, savedTemplate);
    if (score > 380) { 
      foundID = savedID;
      break; 
    }
  }
  file.close();
  return foundID;
}

// ===================== LÓGICA DE MIEMBROS =====================

void syncLocalCache(String dataFromServer) {
  File file = LittleFS.open(MEMORY_FILE, FILE_WRITE);
  if (file) {
    file.print(dataFromServer); // Guardamos la relación ID,UUID
    file.close();
    Serial.println("✅ WhiteList vinculada con UUIDs guardada.");
  }
}

bool isMemberInCache(int template_id) {
  File file = LittleFS.open(MEMORY_FILE, FILE_READ);
  if (!file) return false;

  String idBusqueda = String(template_id) + ","; // Buscamos "250,"
  
  while (file.available()) {
    String line = file.readStringUntil('|'); // Separador entre registros
    if (line.startsWith(idBusqueda)) {
      file.close();
      return true; // Encontrado y está en la lista de activos
    }
  }
  file.close();
  return false;
}

// ===================== SETUP =====================
void setup() {
  Serial.begin(115200);
  delay(1000);  // Dale tiempo al Monitor Serial para abrirse
  Serial.println("--- PRUEBA DE INICIO ---");
  //printResetReason();

  mySerial.begin(57600, SERIAL_8N1, 16, 17);

  //Wire.begin(21, 22);
  //Wire.setClock(50000);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("❌ Falló el inicio físico de la pantalla");
    // No bloqueamos, dejamos que el código siga para ver el resto
  } else {
    Serial.println("✅ Pantalla inicializada correctamente");
  }

  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi...");

  /* display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.print(F("Connecting to \n"));
  display.setCursor(0, 50);
  display.setTextSize(2);
  display.print(ssid);
  display.drawBitmap(73, 10, Wifi_start_bits, Wifi_start_width, Wifi_start_height, WHITE);
  display.display(); */

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("✅ Conectado");
  Serial.print("📡 IP ESP32: ");
  Serial.println(WiFi.localIP());

 /*  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(8, 0);
  display.print(F("Connected \n"));
  display.drawBitmap(33, 15, Wifi_connected_bits, Wifi_connected_width, Wifi_connected_height, WHITE);
  display.display(); */

  finger.begin(57600);
  if (finger.verifyPassword()) {
    Serial.println("🟢 Sensor conectado correctamente.");
    showMessage("Sensor OK");
  } else {
    Serial.println("🔴 No se pudo conectar al sensor.");
    showMessage("Sensor ERROR");
  }

  beginRelaySafeState();

  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.on("/enroll", handleEnroll);
  server.on("/status", handleStatus);
  server.on("/reset-fingerprints", handleResetFingerprints);
  server.on("/list-fingers", storedsIds);
  server.on("/delete-finger", deletId);

  // NUEVO: probar relé sin pasar por huella/backend
  server.on("/relay-test", []() {
    server.sendHeader("Access-Control-Allow-Origin", "*");
    uint32_t ms = 1000;
    if (server.hasArg("ms")) {
      ms = server.arg("ms").toInt();
      if (ms == 0) ms = 1000;
    }
    pulseRelay(ms);
    server.send(200, "text/plain", "Relay pulsed for " + String(ms) + " ms");
  });


  ///

  // Endpoint para ver la lista blanca (ID,UUID)
  server.on("/debug/whitelist", []() {
    if (!LittleFS.exists(MEMORY_FILE)) {
      server.send(404, "text/plain", "Archivo de Whitelist no encontrado.");
      return;
    }
    File file = LittleFS.open(MEMORY_FILE, FILE_READ);
    String content = file.readString();
    file.close();
    server.send(200, "text/plain", "CONTENIDO WHITELIST (ID,UUID):\n" + content);
  });

  // Endpoint para ver cuántas huellas hay en el disco duro (Master Templates)
  server.on("/debug/templates", []() {
    if (!LittleFS.exists(MASTER_TEMPLATES)) {
      server.send(404, "text/plain", "Archivo maestro de huellas no encontrado.");
      return;
    }
    File file = LittleFS.open(MASTER_TEMPLATES, FILE_READ);
    size_t fileSize = file.size();
    int totalRegistros = fileSize / 516; // 4 bytes ID + 512 bytes Template
    
    String info = "REPORTE DE DISCO DURO:\n";
    info += "Tamaño total del archivo: " + String(fileSize) + " bytes\n";
    info += "Total de huellas respaldadas: " + String(totalRegistros) + "\n\n";
    info += "Listado de IDs presentes:\n";

    while (file.available()) {
      int id;
      uint8_t temp[512];
      file.read((uint8_t*)&id, sizeof(id));
      file.read(temp, 512);
      info += "- ID: " + String(id) + "\n";
    }
    file.close();
    server.send(200, "text/plain", info);
  });
  ///

  server.begin();
  Serial.println("🌐 Servidor HTTP listo.");
  syncLocalCache("1,uuid-admin|5,uuid-cliente-active|250,uuid-cliente-infinito");
  showMessage("Pon tu dedo...");

 
}

// ===================== LOOP =====================
void loop() {
  server.handleClient();
  handleRelayPulseLoop();  // atiende el pulso no bloqueante
  checkFingerprint();
  delay(20);  // respiro pequeño, no bloqueante
}

// ===================== HANDLERS =====================
void handleStatus() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "text/plain", "Esp32 working!");
}

void syncLocalCache(String mockData) {
  if (!LittleFS.begin(true)) {
    Serial.println("❌ Error al montar LittleFS");
    return;
  }

  File file = LittleFS.open(MEMORY_FILE, FILE_WRITE);
  if (!file) {
    Serial.println("❌ Error al abrir archivo para escribir");
    return;
  }

  if (file.print(mockData)) {
    Serial.println("✅ Caché sincronizado localmente");
  } else {
    Serial.println("❌ Falló la escritura del caché");
  }
  file.close();
}

bool isMemberInCache(int template_id) {
  if (!LittleFS.begin(true)) return false;

  File file = LittleFS.open(MEMORY_FILE, FILE_READ);
  if (!file) return false;

  String content = file.readString();
  file.close();

  // Buscamos el ID en la cadena (ej: "1,5,10")
  String searchStr = String(template_id);
  
  // Lógica simple de búsqueda en CSV
  int index = content.indexOf(searchStr);
  while (index >= 0) {
    // Verificar que sea el número exacto y no parte de otro (ej: buscar 1 en 10)
    bool prevOk = (index == 0 || content[index - 1] == ',');
    bool nextOk = (index + searchStr.length() == content.length() || content[index + searchStr.length()] == ',');
    
    if (prevOk && nextOk) return true;
    index = content.indexOf(searchStr, index + 1);
  }

  return false;
}



void storedsIds() {
  String stored = "";
  String empty = "";
  bool firstStored = true;
  bool firstEmpty = true;

  // Recorremos todos los espacios posibles del sensor
  for (int i = 1; i <= 243; i++) {
    // Intentamos cargar el modelo para ver si el ID está ocupado
    if (finger.loadModel(i) == FINGERPRINT_OK) {
      if (!firstStored) stored += ",";
      stored += String(i);
      firstStored = false;
    } else {
      // Si falla la carga, asumimos que el espacio está vacío
      if (!firstEmpty) empty += ",";
      empty += String(i);
      firstEmpty = false;
    }
  }

  // Construimos el JSON final
  String json = "{";
  json += "\"stored\": [" + stored + "],";
  json += "\"available\": [" + empty + "]";
  json += "}";

  server.send(200, "application/json", json);
};


void deletId() {
  if (!server.hasArg("id")) {
    server.send(400, "text/plain", "Falta el ID");
    return;
  }

  int idToDelete = server.arg("id").toInt();
  uint8_t result = finger.deleteModel(idToDelete);

  if (result == FINGERPRINT_OK) {
    server.send(200, "text/plain", "ID " + String(idToDelete) + " borrado con éxito");
    Serial.println("Huella borrada: " + String(idToDelete));
  } else {
    server.send(500, "text/plain", "Error al borrar ID");
  }
};


void handleEnroll() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  if (!server.hasArg("user_id")) {
    server.send(400, "text/plain", "Falta user_id");
    return;
  }

  int nextID = getNextID();
  int template_id = getFreeTemplateID();

  Serial.printf("📥 Iniciando registro para user_id=%s con template_id=%d\n", user_id.c_str(), nextID);

  if (enrollFingerprint(nextID)) {
    sendToBackend(nextID, user_id);
    server.send(200, "text/plain", "Huella registrada correctamente");
    showMessage("Huella registrada");
  } else {
    server.send(500, "text/plain", "Error registrando huella");
    showMessage("Error registro huella");
  }
  delay(2000);
  showMessage("Pon tu dedo...");
}

// ===================== LÓGICA DE HUELLA =====================
bool enrollFingerprint(int idReal, String uuid) {
  // --- PASO 1: Captura de huella (Lógica estándar) ---
  int p = -1;
  while (p != FINGERPRINT_OK) { p = finger.getImage(); yield(); }
  if (finger.image2Tz(1) != FINGERPRINT_OK) return false;
  
  delay(2000); // Esperar a que quite el dedo
  p = 0;
  while (p != FINGERPRINT_NOFINGER) { p = finger.getImage(); yield(); }
  
  while (p != FINGERPRINT_OK) { p = finger.getImage(); yield(); }
  if (finger.image2Tz(2) != FINGERPRINT_OK) return false;
  if (finger.createModel() != FINGERPRINT_OK) return false;

  // --- PASO 2: Rotación Física (Solo para el sensor) ---
  // Si idReal es 241, slotDestino será 1. Si idReal es 242, slotDestino será 2.
  int slotDestino = (idReal > 240) ? (idReal % 240) : idReal;
  if (slotDestino == 0) slotDestino = 240;

  if (finger.storeModel(slotDestino) == FINGERPRINT_OK) {
    
    // --- PASO 3: Guardar Firma en Disco (ID REAL) ---
    uint8_t templateData[512];
    if (downloadTemplateToBuffer(templateData)) {
      File fData = LittleFS.open(MASTER_TEMPLATES, FILE_APPEND);
      if (fData) {
        fData.write((uint8_t*)&idReal, sizeof(idReal)); // Guardamos 241, no 1
        fData.write(templateData, 512);
        fData.close();
      }
    }

    // --- PASO 4: Actualizar WhiteList Local (ID REAL) ---
    File fMem = LittleFS.open(MEMORY_FILE, FILE_APPEND);
    if (fMem) {
      fMem.print("|" + String(idReal) + "," + uuid);
      fMem.close();
    }
    
    Serial.printf("✅ Socio %d guardado físicamente en slot %d y respaldado en disco.\n", idReal, slotDestino);
    return true;
  }
  return false;
}

void sendToBackend(int template_id, String user_id) {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(String(backend_url) + "/fingerprints");
  http.addHeader("Content-Type", "application/json");

  String body = "{\"user_id\":\"" + user_id + "\", \"template_id\":" + String(template_id) + "}";

  Serial.println("Enviando body:");
  Serial.println(body);

  int code = http.POST(body);

  Serial.printf("📤 POST /fingerprints [%d] %s\n", code, http.getString().c_str());
  Serial.print("POST to backend URL: ");
  Serial.println(String(backend_url) + "/fingerprints");

  http.end();
}

void checkFingerprint() {
  // Intentamos capturar la huella del sensor
  if (finger.getImage() != FINGERPRINT_OK) return;
  if (finger.image2Tz() != FINGERPRINT_OK) return;

  // PASO A: Búsqueda rápida en el Hardware (Slots 1-240)
  int result = finger.fingerSearch();
  
  if (result == FINGERPRINT_OK) {
    int idEncontrado = finger.fingerID;
    Serial.printf("🔍 ID encontrado en Hardware: %d\n", idEncontrado);
    validateFingerprint(idEncontrado); // Validamos contra WhiteList/Backend
  } 
  else {
    // PASO B: Si el hardware no lo tiene, buscamos en el "Disco Duro" (LittleFS)
    showMessage("Buscando en\nPersistencia...");
    int idPersistente = searchInLittleFS(); // Esta función devuelve el ID REAL (ej: 350)
    
    if (idPersistente != -1) {
      Serial.printf("💾 ID encontrado en Persistencia: %d\n", idPersistente);
      validateFingerprint(idPersistente);
    } else {
      Serial.println("❌ Huella no reconocida en ninguna base");
      showMessage("No encontrado");
      delay(1500);
      showMessage("Pon tu dedo...");
    }
  }
}

void handleResetFingerprints() {
  Serial.println(" Reiniciando todas las huellas guardadas...");
  if (finger.emptyDatabase() == FINGERPRINT_OK) {
    Serial.println("Base de datos de huellas vaciada correctamente.");
    server.send(200, "text/plain", "Todas las huellas han sido reiniciadas.");
    showMessage("Base de datos vacia");
  } else {
    Serial.println(" Error al vaciar la base de datos de huellas.");
    server.send(500, "text/plain", "Error al reiniciar las huellas.");
    showMessage("Error reiniciando");
  }
}
// ===================== VALIDACIÓN Y BACKEND =====================

void validateFingerprint(int template_id) {
  // 1. CHEQUEO EN CACHÉ LOCAL (White List de IDs activos)
  // Aquí es donde comparamos el ID (sea 14 o 500) contra el archivo members.csv
  if (isMemberInCache(template_id)) {
    Serial.printf("🚀 ACCESO LOCAL CONFIRMADO: ID %d\n", template_id);
    showMessage("Autorizado\n(Modo Local)");
    pulseRelay(1500); 
    return; 
  }

  // 2. SI NO ESTÁ EN CACHÉ LOCAL, CONSULTAMOS AL BACKEND (Fallback)
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    // IMPORTANTE: Tu API de Flask debe recibir el template_id real
    String url = String(backend_url) + "/fingerprints/" + String(template_id) + "/verify";
    
    http.begin(url);
    int code = http.GET();
    
    if (code == 200) {
      Serial.println("✅ Backend confirma: Socio Activo");
      showMessage("Autorizado\nBackend");
      pulseRelay(1500);
    } else if (code == 403) {
      Serial.println("⛔ Backend confirma: Membresía Vencida");
      showMessage("Vencido\nPase a Recepcion");
    } else {
      Serial.printf("⚠️ Error de servidor (%d). Acceso denegado.\n", code);
      showMessage("Error Servidor");
    }
    http.end();
  } else {
    // Si no hay internet y no estaba en el caché de activos, denegamos por seguridad
    Serial.println("🔒 Offline y no está en caché de activos.");
    showMessage("No autorizado\nSin Conexion");
  }
}

int getFreeTemplateID() {
  for (int i = 1; i < 243; i++) {
    if (finger.loadModel(i) != FINGERPRINT_OK) return i;
  }
  return -1;
}

int getNextID() {
  // 1. Intentamos ver cuántos registros hay en el archivo maestro
  File file = LittleFS.open(MASTER_TEMPLATES, FILE_READ);
  if (!file) return 1; // Si no existe, empezamos en 1

  int totalRegistros = file.size() / 516; // Cada registro mide 516 bytes (4 ID + 512 Template)
  file.close();

  return totalRegistros + 1; // El siguiente ID disponible
}


// Master finger
