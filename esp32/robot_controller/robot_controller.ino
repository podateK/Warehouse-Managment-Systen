#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

#define UART_TX 17
#define UART_RX 18
#define UART_BAUD 9600

const char* WIFI_SSID = "WIFI_SSID";
const char* WIFI_PASS = "WIFI_PASSWORD";

IPAddress LOCAL_IP(10, 91, 170, 213);
IPAddress GATEWAY(10, 91, 170, 1);
IPAddress SUBNET(255, 255, 255, 0);
IPAddress DNS1(8, 8, 8, 8);

WebServer server(80);

void sendToArduino(const String& cmd) {
    Serial1.println(cmd);
}

void handleCmd() {
    if (server.method() != HTTP_POST) {
        server.send(405, "application/json", "{\"error\":\"Method Not Allowed\"}");
        return;
    }

    String body = server.arg("plain");
    StaticJsonDocument<128> doc;
    DeserializationError err = deserializeJson(doc, body);

    if (err || !doc.containsKey("command")) {
        server.send(400, "application/json", "{\"error\":\"Bad Request\"}");
        return;
    }

    String command = doc["command"].as<String>();
    sendToArduino(command);
    server.send(200, "application/json", "{\"status\":\"ok\"}");
}

void handleStatus() {
    server.send(200, "application/json", "{\"status\":\"online\"}");
}

void handleNotFound() {
    server.send(404, "application/json", "{\"error\":\"Not Found\"}");
}

void setup() {
    Serial.begin(115200);
    Serial1.begin(UART_BAUD, SERIAL_8N1, UART_RX, UART_TX);

    WiFi.config(LOCAL_IP, GATEWAY, SUBNET, DNS1);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }

    server.on("/cmd", handleCmd);
    server.on("/status", HTTP_GET, handleStatus);
    server.onNotFound(handleNotFound);
    server.begin();
}

void loop() {
    server.handleClient();
}
