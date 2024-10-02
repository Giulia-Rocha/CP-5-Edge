#include <WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"

// Configurações - variáveis editáveis
const char* default_SSID = "Wokwi-GUEST"; // Nome da rede Wi-Fi
const char* default_PASSWORD = ""; // Senha da rede Wi-Fi
const char* default_BROKER_MQTT = "52.137.83.133"; // IP do Broker MQTT
const int default_BROKER_PORT = 1883; // Porta do Broker MQTT
const char* default_TOPICO_SUBSCRIBE = "/TEF/lamp003/cmd"; // Tópico MQTT de escuta (comandos para o dispositivo)
const char* default_TOPICO_PUBLISH_1 = "/TEF/lamp003/attrs"; // Tópico MQTT de envio de estado (ex.: estado da lâmpada)
const char* default_TOPICO_PUBLISH_2 = "/TEF/lamp003/attrs/l"; // Tópico MQTT de envio de luminosidade
const char* default_TOPICO_PUBLISH_3 = "/TEF/DHT001/attrs/t"; // Tópico MQTT de envio de temperatura
const char* default_TOPICO_PUBLISH_4 = "/TEF/DHT001/attrs/h"; // Tópico MQTT de envio de umidade
const char* default_ID_MQTT = "fiware_003"; // ID do cliente MQTT
const int default_D4 = 2; // Pino do LED onboard

// Variáveis para configurações editáveis
char* SSID = const_cast<char*>(default_SSID);
char* PASSWORD = const_cast<char*>(default_PASSWORD);
char* BROKER_MQTT = const_cast<char*>(default_BROKER_MQTT);
int BROKER_PORT = default_BROKER_PORT;
char* TOPICO_SUBSCRIBE = const_cast<char*>(default_TOPICO_SUBSCRIBE);
char* TOPICO_PUBLISH_1 = const_cast<char*>(default_TOPICO_PUBLISH_1);
char* TOPICO_PUBLISH_2 = const_cast<char*>(default_TOPICO_PUBLISH_2);
char* TOPICO_PUBLISH_3 = const_cast<char*>(default_TOPICO_PUBLISH_3);
char* TOPICO_PUBLISH_4 = const_cast<char*>(default_TOPICO_PUBLISH_4);
char* ID_MQTT = const_cast<char*>(default_ID_MQTT);
int D4 = default_D4;

WiFiClient espClient; // Cliente Wi-Fi
PubSubClient MQTT(espClient); // Cliente MQTT
char EstadoSaida = '0'; // Estado inicial do LED (0: desligado)

// Definição do pino para o sensor DHT22
const int DHT_PIN = 15;
DHTesp dht; // Instância do sensor DHT22

// Função para inicializar o monitor serial
void initSerial() {
    Serial.begin(115200);
}

// Função para conectar ao Wi-Fi
void initWiFi() {
    delay(10);
    Serial.println("------Conexao WI-FI------");
    Serial.print("Conectando-se na rede: ");
    Serial.println(SSID);
    Serial.println("Aguarde");
    reconectWiFi(); // Verifica e tenta conectar ao Wi-Fi
}

// Função para configurar o MQTT
void initMQTT() {
    MQTT.setServer(BROKER_MQTT, BROKER_PORT); // Configura o servidor MQTT
    MQTT.setCallback(mqtt_callback); // Define o callback para mensagens recebidas
}

// Função de setup inicial do sistema
void setup() {
    InitOutput(); // Inicializa o LED onboard
    initSerial(); // Inicializa o monitor serial
    initWiFi(); // Conecta ao Wi-Fi
    initMQTT(); // Configura o MQTT
    dht.setup(DHT_PIN, DHTesp::DHT22); // Configura o sensor DHT22 no pino especificado
    delay(5000); // Aguarda 5 segundos antes de iniciar o envio de dados
    MQTT.publish(TOPICO_PUBLISH_1, "s|on"); // Publica o estado inicial ("s|on") no tópico do LED
}

// Função principal que roda em loop
void loop() {
    VerificaConexoesWiFIEMQTT(); // Verifica e reconecta ao Wi-Fi e ao MQTT, se necessário
    EnviaEstadoOutputMQTT(); // Envia o estado atual do LED ao broker MQTT
    handleLuminosity(); // Lê e publica a luminosidade
    handleDHT(); // Lê e publica a temperatura e umidade
    MQTT.loop(); // Mantém a conexão MQTT ativa
}

// Função para reconectar ao Wi-Fi, se a conexão cair
void reconectWiFi() {
    if (WiFi.status() == WL_CONNECTED)
        return; // Se já estiver conectado, não faz nada
    WiFi.begin(SSID, PASSWORD); // Tenta conectar com SSID e senha fornecidos
    while (WiFi.status() != WL_CONNECTED) { // Aguarda até conseguir conexão
        delay(100);
        Serial.print(".");
    }
    Serial.println();
    Serial.println("Conectado com sucesso na rede ");
    Serial.print(SSID);
    Serial.println("IP obtido: ");
    Serial.println(WiFi.localIP()); // Imprime o IP local obtido

    // Garantir que o LED inicie desligado
    digitalWrite(D4, LOW);
}

// Callback para processar mensagens MQTT recebidas
void mqtt_callback(char* topic, byte* payload, unsigned int length) {
    String msg;
    for (int i = 0; i < length; i++) {
        char c = (char)payload[i]; // Concatena o payload recebido
        msg += c;
    }
    Serial.print("- Mensagem recebida: ");
    Serial.println(msg);

    // Compara o tópico recebido com os comandos esperados
    String onTopic = String(topicPrefix) + "@on|";
    String offTopic = String(topicPrefix) + "@off|";

    // Se a mensagem for para ligar o LED, aciona o pino D4
    if (msg.equals(onTopic)) {
        digitalWrite(D4, HIGH);
        EstadoSaida = '1'; // Define o estado como ligado
    }

    // Se a mensagem for para desligar o LED, desativa o pino D4
    if (msg.equals(offTopic)) {
        digitalWrite(D4, LOW);
        EstadoSaida = '0'; // Define o estado como desligado
    }
}

// Verifica as conexões Wi-Fi e MQTT, e tenta reconectar se necessário
void VerificaConexoesWiFIEMQTT() {
    if (!MQTT.connected())
        reconnectMQTT(); // Reconecta ao MQTT, se desconectado
    reconectWiFi(); // Reconecta ao Wi-Fi, se desconectado
}

// Envia o estado atual do LED ao broker MQTT
void EnviaEstadoOutputMQTT() {
    if (EstadoSaida == '1') {
        MQTT.publish(TOPICO_PUBLISH_1, "s|on"); // Publica "on" se o LED estiver ligado
        Serial.println("- Led Ligado");
    }

    if (EstadoSaida == '0') {
        MQTT.publish(TOPICO_PUBLISH_1, "s|off"); // Publica "off" se o LED estiver desligado
        Serial.println("- Led Desligado");
    }
    Serial.println("- Estado do LED onboard enviado ao broker!");
    delay(1000); // Aguarda 1 segundo entre envios
}

// Inicializa o LED onboard e realiza um piscar de teste
void InitOutput() {
    pinMode(D4, OUTPUT); // Define o pino D4 como saída
    digitalWrite(D4, HIGH); // Liga o LED inicialmente
    boolean toggle = false;

    // Faz o LED piscar 10 vezes para indicar inicialização
    for (int i = 0; i <= 10; i++) {
        toggle = !toggle;
        digitalWrite(D4, toggle);
        delay(200);
    }
}

// Função para reconectar ao MQTT
void reconnectMQTT() {
    while (!MQTT.connected()) { // Tenta até conseguir se conectar
        Serial.print("* Tentando se conectar ao Broker MQTT: ");
        Serial.println(BROKER_MQTT);
        if (MQTT.connect(ID_MQTT)) { // Tenta conectar com o ID especificado
            Serial.println("Conectado com sucesso ao broker MQTT!");
            MQTT.subscribe(TOPICO_SUBSCRIBE); // Inscreve-se no tópico de comandos
        } else {
            Serial.println("Falha ao reconectar no broker.");
            Serial.println("Haverá nova tentativa de conexão em 2s");
            delay(2000); // Aguarda 2 segundos antes de tentar novamente
        }
    }
}

// Função para ler o valor da luminosidade e publicá-lo no MQTT
void handleLuminosity() {
    const int potPin = 34; // Define o pino de leitura do potenciômetro (simulando luminosidade)
    int sensorValue = analogRead(potPin); // Lê o valor analógico do sensor
    int luminosity = map(sensorValue, 0, 4095, 0, 100); // Mapeia o valor lido para 0-100%
    String mensagem = String(luminosity); // Converte para string
    Serial.print("Valor da luminosidade: ");
    Serial.println(mensagem.c_str());
    MQTT.publish(TOPICO_PUBLISH_2, mensagem.c_str()); // Publica o valor no tópico MQTT
}

// Função para ler temperatura e umidade do sensor DHT22 e publicar no MQTT
void handleDHT(){
    TempAndHumidity  data = dht.getTempAndHumidity(); // Lê temperatura e umidade
    String mensagemTemperatura = String(data.temperature, 2); // Converte temperatura para string
    String mensagemUmidade = String(data.humidity, 1); // Converte umidade para string

    Serial.println("Temp: " + String(data.temperature, 2) + "°C");
    Serial.println("Humidity: " + String(data.humidity, 1) + "%");
    Serial.println("---");
  
    MQTT.publish(TOPICO_PUBLISH_3, mensagemTemperatura.c_str());  // Publica a temperatura no MQTT
    MQTT.publish(TOPICO_PUBLISH_4, mensagemUmidade.c_str());      // Publica a umidade no MQTT
}
