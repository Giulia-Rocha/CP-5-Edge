# Smart-Lamp-IoT + DHT 22 🧠💡
Uma entidade "Smart Lamp"  (ou "Lâmpada Inteligente") é um conceito dentro da plataforma FIWARE que representa uma lâmpada conectada, capaz de interagir com um ecossistema de IoT. Ela é modelada como uma entidade de dados que possui atributos e metadados associados que definem seu comportamento e características.

E dessa vez com um elemento a mais, o DHT 22 para capturar a Umidade e Temperatura do ambiente.

# Descrição 📝
O projeto executa a plataforma FIWARE como back-end da solução de monitoramento de vinheria (Smart Lamp). Além disso, utiliza a Azure ☁️ como serviço de nuvem para hospedar os servidores e componentes do FIWARE.

# Tecnologias Usadas 
- FIWARE
- Postman
- Docker 🐳
- Microsoft Azure ☁️
- C++ (Código-fonte para o ESP32)
- Python e biblioteca Dash (Dashboard Interativo)
# Configuração e Instalação
## 1° Passo - Configurar a VM
- Configurar uma VM com Ubuntu Server LTS na Plataforma da Azure
- Seguir o passo a passo do [Github](https://github.com/fabiocabrini/fiware) do FIWARE Descomplicado.
## 2° Configurar uma Entidade no Postman
- Seguir o passo a passo da [Playlist](https://www.youtube.com/watch?v=8oHkAlXdWo8)
## 3° Configurar o WOKWI usando o código fonte
- Faça uma cópia do Projeto no [WOKWI](https://wokwi.com/projects/410480914974507009)
- Configure as variáveis editáveis de acordo com os comentários no [Código Fonte](codigo-fonte.ino)
## 4° Rodar o script em Pyhton na VM para exibir o dashboard
- Crie um arquivo em .py na VM e coloque este [código](dashboard.py)
- Rode o código com o comando python3 nome_do_arquivo.py
- obs: configure a porta 8050 para isto.
  

# Funcionalidades Testadas
### - Ligar e Desligar o LED on board
### - Verificar o status da Luminosidade recebida do LDR
### - Verificar os valores de Umidade e Temperatura
### - Exibir um Dashboard com os valores dos atributos

# Autores
- [Giulia Barbizan](https://github.com/Giulia-Rocha)
- [Gustavo Viega](https://github.com/Vieg4)
- [Felipe Marques](https://github.com/FelipeMarquesdeOliveira)
- [Felipe Men dos Santos]()
# Links Úteis
- [WOKWI](https://wokwi.com/projects/410480914974507009)
- [Vídeo Explicativo](https://drive.google.com/file/d/1Hiz93oEQ46Uy5WnyN6f2qI5uMu61ak1P/view?usp=sharing)
