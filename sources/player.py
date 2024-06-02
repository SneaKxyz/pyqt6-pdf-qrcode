# Ce fichier contient l'interface graphique de l'application

import os  # importation du module os
import pynput # importation du module pynput

# importation des composants du module PyQt6
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QToolBar
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView # composant du module PyQt6 qui créer un moteur de rendu pour les fichers html et pdf
from camera import CameraApp # composant qui gère les qrcodes

from config import SCROLL_SPEED

from pynput.keyboard import Key

keyboard = pynput.keyboard.Controller() # creation d'un objet pour le clavier
mouse = pynput.mouse.Controller() # creation d'un objet pour la souris

###############################
#### CREATION DE LA CLASSE ####
###############################

# utilisation de la programmation orienté objet (POO)
# creation de la fenêtre
class Player(QMainWindow): # création de la classe (fenêtre)
    def __init__(self):
        super(Player, self).__init__()

        self.tabs = {}
        
        self.tabMenu = QTabWidget() # création du Widget des onglets
        self.tabMenu.setDocumentMode(True) # supprime le cadre blanc autour des pages
        self.tabMenu.setTabsClosable(False) # autorise la fermeture des onglets
        self.setCentralWidget(self.tabMenu) # défini la barre d'onglet comme element central de la fenetre

        self.toolbar = QToolBar() # Création de la toolbar
        self.toolbar.setMovable(False) # empêche de pouvoir déplacer la toolbar
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon) # met le texte a côté du l'icone qui lui est associée
        self.toolbar.setFixedSize(500, 30) # défini la taille de la ToolBar
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.toolbar) # ajout de la ToolBar sur la fenêtre et la place en pied de page

        # Création des QActions ("texte d'affichage") qui iront dans la QToolBar
        self.toolbar.addAction(QIcon('./sources/images/icon/joystick.png'), 'Navigation')
        self.toolbar.addAction(QIcon('./sources/images/icon/button_vert.png'), 'Intéragir')
        self.toolbar.addAction(QIcon('./sources/images/icon/button_bleu.png'), 'Scanner QR-Code')
        self.toolbar.addAction(QIcon('./sources/images/icon/button_rouge.png'), 'Retour')

        self.add_file('index.html') # page d'accueil au demarrage de l'application
        self.default_style() # applique le style css pour la toolbar

    def __repr__(self): # representation de la classe
        return str(self.tabs) #on affiche la liste des pages dans le dico

    #################################
    #### CREATIONS DES FONCTIONS ####
    #################################

    def open_scan(self):
        self.scanner = CameraApp() # créer une variable qui corresond à la caméra
        self.scanner.show() # affice le retour vidéo de la caméra
        self.scanner.start_camera(self.stopCamera) # lance la fonction qui gère la caméra et renvoie la sortie sur la fonction stopCamera

    def stopCamera(self, data):
        self.scanner.close() # arrete la camera
        del self.scanner # destruction de l'objet camera
        self.add_file(data) # la data vers la fonction add_file

    def add_file(self, data):
        """
        Fonction permettant l'ajout de nouveaux onglets
        """
        if (str(data) == '') or (data is None): # on vérifie si l'url n'est pas vide
            print('Donnée récupéré par la caméra : ' + str(data) + ', ce fichier n\'existe pas !')
            return
        
        page = Page(str(data)) # creer un objet de type Page
        page.dir = data.split('.')[-1]

        def createUrl(page):
            page.url = os.path.split(os.path.abspath(__file__))[0]+r'/content/' + str(page.dir) + "/" + str(data) # creer l'url de la page et modifie la valeur de l'attribut url
            self.tabs[page.name] = page.url # creer un clé et une valeur pour la page dans le dico tabs
            
        def createBrowser(page, label='chargement...'):
            browser = QWebEngineView() # creation de la partie graphique "moteur de rendu" qui affichera les fichiers ouverts
            # paramètrage afin de supporter les documents pdf
            browser.settings().setAttribute(browser.settings().WebAttribute.PluginsEnabled, True) # autorisarion des plugins dans le moteur de rendu
            browser.settings().setAttribute(browser.settings().WebAttribute.PdfViewerEnabled, True) # autorisation des fichiers pdf dans le moteur de rendu
            browser.setUrl(QUrl.fromLocalFile(page.url)) # ajoute la page avec l'url/fichier renseigner
            
            i = self.tabMenu.addTab(browser, label) # attribut l'onglet actuel à une variable
            self.tabMenu.setCurrentIndex(i) # fixe l'indice de l'onglet

            browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabMenu.setTabText(i, browser.page().title()))
            
        createUrl(page) # fonction pour créer l'url d'une page
        createBrowser(page) # creer le moteur de rendu de la page (charge l'url et l'affiche)

    def close_tab(self):
        """
        Permet de fermer un onglet.
        """
        try:
            # arrete et supprime l'objet camera si elle existe
            if self.scanner.statut == True:
                self.stopCamera(None)
                return
        except AttributeError:
            pass
        
        if self.tabMenu.count() < 2: # Garde au moins un onglet ouvert
            return # ne retourne rien pour faire aucune action et ne pas arreter le programme

        # supprime une fenetre
        current_tab_index = self.tabMenu.currentIndex() # recupere l'indice de l'onglet actuel
        self.tabMenu.removeTab(current_tab_index) # supprime l'onglet actuel
    
    ################################
    #### GESTIONS DES COMMANDES ####
    ################################     

    # Programmation Evenementielle
    # Les actions proviennent du fichier command.py suite à l'activation d'un bouton ou du joystick
    
    def command_handler(self, command):
        """
        Fonction qui détecte lorsque qu'une touche spécifique est pressée ou qu'une action précise est réalisée.
        """
        if command == 'z': # on monte la page vers le haut (scroll vers le haut)
            mouse.scroll(0,SCROLL_SPEED) # if dont work replace the line by 'keyboard.tap(Key.up)'
        elif command == 's': # on descend la page (scroll vers le bas)
            mouse.scroll(0,-SCROLL_SPEED) # if dont work replace the line by 'keyboard.tap(Key.down)'
        elif command == 'q': # déplace le curseur sur la gauche pour passer au bouton précédent
            keyboard.press(Key.shift)
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
            keyboard.release(Key.shift)
        elif command == 'd': # déplace le curseur sur la droite pour passer au bouton suivant
            keyboard.tap(Key.tab)
        elif command == 'b': # supprime l'onglet actif
            self.close_tab()
        elif command == 'c': # active la caméra
            self.open_scan()
        elif command == 'x': # presse la touche entrer pour valider une action
            keyboard.tap(Key.enter)
        elif command == 'w': # quitte l'application
            self.close()
            print('/!\ Vous venez de quitter l\'application.')
            print('/!\ Veuillez fermer ce terminal.')
            print("\n/!\ Ne pas tenir compte de l'erreur ci-dessous.\n")
            raise Exception('Vous venez de quitter l\'application.')

    def default_style(self):
        """
        Style CSS sur l'application concerne la toolbar.
        """
        self.setStyleSheet('''
            QWidget{
                background-color: rgb(24,24,24);
                border-color: transparent;
                color: #f2f2f9;
            }
                            ''')


############################
#### CREATION DE CLASSE ####
############################
        
class Page():
    def __init__(self, name):
        self.name = name # nom du fichier cible
        self.url = None # chemin du fichier cible
        self.dir = None # dossier du fichier cible
        
    def __repr__(self):
        return self.name # affiche le nom de la page
    
    def __str__(self):
        return self.name + ', ' + self.url # affiche le nom et l'url de la page

