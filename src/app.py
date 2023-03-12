from PySide6.QtCore import (
    Qt,
    Slot
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    # MORE WIDGETS
    QPushButton,
    QLabel,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QScrollArea,
    QLineEdit,
    QFileDialog,
)
import sys
import json
import os

# Definir el nombre del archivo JSON
archivo_json = 'chats.json'
# Definimos la variable global chats
chats = [] # UN ARREGLO DE CHATS

def saveChats():
    # Guardar los cambios en el archivo JSON
    with open(archivo_json, 'w') as archivo:
        json.dump({'chats':chats}, archivo)

class ChatArea(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        # Layout para el contenedor
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)

        # Layout para los mensajes del chat
        container = QWidget()
        self.area_layout = QVBoxLayout(container)
        self.area_layout.setAlignment(Qt.AlignTop)

        # Set Container chats
        self.setWidget(container)

    def clean(self):
        for i in reversed(range(self.area_layout.count())): 
            self.area_layout.itemAt(i).widget().deleteLater()

    def addMessage(self, message):
        container = QWidget()
        if message['role'] == 'user':
            container.setStyleSheet("QWidget { background-color : green; }")
        elif message['role'] == 'assistent':
            container.setStyleSheet("QWidget { background-color : grey; }")

        message_layout = QHBoxLayout(container)
        # message_layout.setAlignment(Qt.AlignCenter)

        role_label = QLabel(message['role'] ) #CHAGE WITH IMAGE
        role_label.setMaximumWidth(80)
        role_label.setAlignment(Qt.AlignTop)
        content_label = QLabel(message['content'] )

        message_layout.addWidget(role_label)
        message_layout.addWidget(content_label)
        #ADD SEPARATOR

        self.area_layout.addWidget(container)


class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.messages=[]
        self.layout = QVBoxLayout(self)
        # Create zona de los mensajes
        self.chat_area = ChatArea()
        
        input_layout = QHBoxLayout()

        self.input_box = QLineEdit()

        load_button = QPushButton("Cargar Prompt")
        load_button.clicked.connect(self.cargar_archivo)

        # input_box.setFixedHeight(30)
        self.input_box.setPlaceholderText("Ingresa tu mensaje aquí...")
        # input_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        send_button = QPushButton("Enviar")
        send_button.clicked.connect(self.sendMessage)

        input_layout.addWidget(load_button)
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(send_button)

        self.layout.addWidget(self.chat_area)
        self.layout.addLayout(input_layout)

    def connect(self, method):
        self.createChat = method

    def loadMessages(self, messages): # list de los mensajes
        self.chat_area.clean()
        self.messages = messages #manda la referencia del objeto messages
        for message in messages:
            self.chat_area.addMessage(message)

    def sendMessage(self):
        content = self.input_box.text()
        # limpia el mensaje
        self.input_box.setText('')
        message = {"role": "user", "content": content}
        #SI !messages.count() # Entonces crea un nuevo chat
        if not self.messages:
            self.createChat()
        # despues inserta el mensaje al chat y lo guarda
        self.chat_area.addMessage(message)
        self.messages.append(message)
        self.saveChat()

        # content = 'Result for consult'
        # rol = 'assistent'
        # self.chat_area.addMessage(rol,content)

    def cargar_archivo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "", "Text Files (*.txt);;Python Files (*.py);;All Files (*)")
        if file_name:
            with open(file_name, 'r') as f:
                content = f.read()
                message = {"role": "assistent", "content": content}
                self.chat_area.addMessage(message)
                self.messages.append(message)
                self.saveChat()

    def saveChat(self):
        saveChats()


class ChatsScrollWidget(QScrollArea):
    def __init__(self, chat_widget):
        super().__init__()
        self.chat_widget = chat_widget
        self.setWidgetResizable(True)
        # Layout para el contenedor
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)

        # Layout para los botones de chats
        container = QWidget()
        self.chats_layout = QVBoxLayout(container)
        self.chats_layout.setAlignment(Qt.AlignTop)

        # Set Container chats
        self.setWidget(container)
        
        self.loadChatsBtns()

    def selectChatHanlder(self):
        # Obtenemos una referencia al botón que envió la señal usando el objeto sender()
        btn = self.sender()
        chat_name = btn.text()
        self.loadChat(chat_name)

    def loadChat(self, chat_name):
        for chat in chats:
            # USO LAS EXCEPCIONES PARA SABER QUE NO ES EL CHAT CORRECTO
            try: 
                data = chat[chat_name]
                # CARGAR MENSAJES AL CHAT AREA --- Manda el obj messages
                self.chat_widget.loadMessages(data["messages"])
                # SI LO ENCUENTRA TERMIAN
                break
            except:
                continue

    def loadChatsBtns(self):
        for chat in chats:
            for clave, _ in chat.items():
                self.createButton(clave)

    def addNewChat(self):
        chat_name = f'Chat {self.chats_layout.count()+1}'
        self.createButton(chat_name)
        # Save json
        global chats
        aux_chat = {chat_name: {'messages':[{"role": "system", "content": "Eres un asistente."}]}}
        chats.append(aux_chat)
        saveChats()
        # CUANDO CREA UN NUEVO CHAT LO SETEA PARA USAR
        self.loadChat(chat_name)

    def createButton(self, name):
        new_btn = QPushButton(name)
        new_btn.clicked.connect(self.selectChatHanlder)
        self.chats_layout.addWidget(new_btn)

class ToolsWidget(QWidget):
    def __init__(self, chat_widget):
        super().__init__()
        # Configuración del layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        
        # ChatsScrollWidget para los chats
        scroll_area = ChatsScrollWidget(chat_widget)
        
        # Botón de nuevo chat
        new_chat_button = QPushButton("+ Nuevo chat")
        new_chat_button.clicked.connect(scroll_area.addNewChat)
        chat_widget.connect(scroll_area.addNewChat)

        # Layout para los botones de exportar e importar
        export_button = QPushButton("Exportar")
        import_button = QPushButton("Importar")

        # Ordena los layouts
        self.layout.addWidget(new_chat_button)
        self.layout.addWidget(scroll_area)
        self.layout.addWidget(export_button)
        self.layout.addWidget(import_button)

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout(self)

        chat_widget = ChatWidget()
        tools_widget = ToolsWidget(chat_widget)
        tools_widget.setMaximumWidth(250)

        self.layout.addWidget(tools_widget)
        self.layout.addWidget(chat_widget)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        main_widget = MainWidget()
        self.setCentralWidget(main_widget)

def loadChats():
    global chats
    # Si el archivo no existe, crear uno nuevo con una estructura JSON vacía
    if not os.path.exists(archivo_json):
        with open(archivo_json, 'w') as archivo:
            json.dump({'chats':[]}, archivo)

    # Leer el archivo JSON
    with open(archivo_json, 'r') as archivo:
        chats = json.load(archivo)['chats']

if __name__ == "__main__":
    loadChats()
    app = QApplication(sys.argv)

    root = App()

    root.setWindowTitle("ChatGPT - pyClient")
    root.resize(1080, 720)
    root.show()

    sys.exit(app.exec())