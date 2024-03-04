# PatsStrap Bluetooth - Retour Haptique pour VRChat
Ce projet ajoute le retour haptique pour les patpat sur VRChat en utilisant un ESP32 et quelque autres composants. Ce projet est basé sur le projet [Patstrap](https://github.com/danielfvm/Patstrap) par [danielfvm](https://github.com/danielfvm).

This README is also available in [English](https://github.com/kikookraft/HapticPatPat/blob/main/README.md).

## Quel est ce projet?
Ce projet (tout comme le projet PatStrap) est un projet open source qui permet d'ajouter le eretour Haptique pour les joueurs VR de VRChat.  
Voila comment fonctionne le projet:
- Quelqu'un vous patpat, grace a des contact sur votre avatar cela envoi un message OSC qui est ensuite recu par le serveur python 
- Une fois que le serveur a recu le message, il envoi un signal par bluetooth a l'ESP32
- L'ESP32 recois le message et active les moteurs enfonction du mesage recu (gauche, droite ou les eux moteurs)

### Pourquois faire une autre version de ce proje?
J'avais essayé d'utiliser le projet Patstrap cependant j'avais eu quelque problèmes avec lui, du coup je l'ai refais a ma sauce. 
Les problèmes que j'avais eu:
- La latence entre le contact et le retour haptique prennait entre 1 et 10 secondes (donc pas incroyable)
- Le serveur python prennait 12% de mon CPU pour aucune raison...

### Du coup, qu'est ce qui est différent?
- Déjà au lieu d'utiliser le wifi j'utililse le bluetooth, ce qui permet une latence bien réduite.   
 (beaucoup moin d'une seconde de latence)
- J'ai modifié le code du serveur pour qu'il puisse fonctionner avec le bluetooth tout en gardant la même interface.
- J'ai ajouté une version dompilé du serveur pour ne pas avoir besion d'installer python.

## Composant electroniques
Pour fabriquer ce projet, vous aurez besoin de:
- ESP32, j'ai utilisé un version [ESP32 30 Broches](https://aliexpress.com/item/1005005970816555.html) mais n'importe quel équivalent devrait fonctionner.  
Si vous utiliser un ESP différent vous devrez peut-être changer les pins dans le code.
- 2x [330Ω résistance](https://aliexpress.com/item/1005006362959267.html)
- 2x [Transistors](https://aliexpress.com/item/1005005755402536.html) (I used BC547)
- 2x [moteur vibrateur](https://aliexpress.com/item/1005001446097852.html)
- A [plaque pcb](https://aliexpress.com/item/1005006365975004.html) (ou tout autre support pour le circuit)
- Si vous utilisez un pcb, il est cool d'avoir des [sockets Dupont](https://amzn.eu/d/i0pZoIV) pour connecter l'ESP sans le souder directement
- 2x [Diodes](https://aliexpress.com/item/1005006054373731.html) (uniquement en cas d'utilisation de bateries)
- [batterie](https://www.amazon.com/dp/B0B7N2T1TD?psc=1&ref=ppx_yo2ov_dt_b_product_details) (J'ai utilisé une 3.7V 2000mAh)
- [chargeur de batterie](https://aliexpress.com/item/1005006274938832.html) (Pour ma pars : TP4056)
- [on/off interrupteur](https://aliexpress.com/item/1005003938856402.html) (Uniquement en cas d'utilisation de bateries)
- Ordinateur avec **bluetooth**   
 
Voici le circuit simplifié:  
![](https://raw.githubusercontent.com/kikookraft/HapticPatPat/main/img/circuit.png)

## Software
### Firmware
Le code du projet à été dévelopé avec [PlatformIO](https://platformio.org/platformio-ide) et [Visual Studio Code](https://code.visualstudio.com/).
Tout est placé dans le dossier `/firmware`.
Le code principal se trouve dans le fichier `/firmware/src/main.cpp`.

Après l'édition du code, vous pouvez uploader le code sur l'ESP en cliquant sur les boutons en bas dans VSCode.
![](https://raw.githubusercontent.com/kikookraft/HapticPatPat/main/img/vsc.png)

Quand déconnecté du bluetooth, la led de l'ESP va clignoter. Une fois connecté la led s'eteindra completement.

Voici a quoi ressemble le produit final:
![](https://raw.githubusercontent.com/kikookraft/HapticPatPat/main/img/geek_sandwich.jpg)

### Serveur
[Ici](https://github.com/kikookraft/HapticPatPat/releases) vous pourrez télécharger la version compilée du serveur.
Vous avez uniquement besoin de le lancer le serveur l'orsque vous utiliser le retour haptique.  
![](https://raw.githubusercontent.com/kikookraft/HapticPatPat/main/img/UI.png)

Si vous utiliser VRCOSC, vous pouvez ajouter l'executable dans les paramètres pour le démarer automatiquement avec VRChat. 
![](https://raw.githubusercontent.com/kikookraft/HapticPatPat/main/img/vrcosc.png)

Le serveur est essentiel pour faire fonctionner ce projet, il est utilisé pour connecter l'OSC de VRChat a l'ESP32.
L'interface est le même que le projet original, mais l'implémentation a été modifié pour permetre l'utilisation du bluetooth a la place du wifi.

Vous pouvez compiler vous même le serveur en lancant `/server/build.bat` ou en utilisant la commande :``` bash
pyinstaller -F -n PatPatHaptic -i icon.png --collect-submodules zeroconf --noconsole .\server\main.py
```
### VRChat & OSC
Vous pouvez suivre le tutoriel sur le projet original [Patstrap](https://github.com/danielfvm/Patstrap?tab=readme-ov-file#vrchat) pour la mise en place des contact sur l'avatar.
