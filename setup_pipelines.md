Voici une procédure complète pour installer et exécuter automatiquement le projet **Pipelines** sous Ubuntu, **dans le répertoire `/opt/pipelines`**, avec **Python 3.11** (via le PPA Deadsnakes). Cette version utilise **SSH** pour le clonage Git (déposé sur `git@github.com:ino-ca/pipelines.git`), et inclut une configuration **systemd** pour un démarrage au boot.

---

# 1. Installer Python 3.11 via Deadsnakes

Sur Ubuntu, vous pouvez installer Python 3.11 en suivant ces étapes :

```bash
sudo apt update
sudo apt install -y software-properties-common curl git
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

- **`sudo add-apt-repository ppa:deadsnakes/ppa -y`** ajoute le PPA Deadsnakes qui fournit des versions récentes de Python.  
- **`python3.11`** sera utilisé pour Open WebUI (et donc Pipelines) sans remplacer la version Python fournie de base par Ubuntu.  

Vérifiez l’installation :

```bash
python3.11 --version
```
Vous devriez voir `Python 3.11.x`.

---

# 2. Préparer le répertoire `/opt/pipelines`

1. **Créer** le dossier `/opt/pipelines` (s’il n’existe pas déjà) :
   ```bash
   sudo mkdir -p /opt/pipelines
   ```
2. **Ajuster les droits** pour qu’un utilisateur précis (par exemple l’utilisateur courant) puisse y écrire :
   ```bash
   sudo chown -R $USER:$USER /opt/pipelines
   ```
   - Remplacez `$USER:$USER` par le nom d’utilisateur voulu (ex. `ubuntu:ubuntu`), selon votre configuration.

3. **Se rendre** dans ce répertoire :
   ```bash
   cd /opt/pipelines
   ```

---

# 3. Configurer l’accès SSH à GitHub (si nécessaire)

Pour cloner via **SSH**, vous devez disposer d’une clé SSH publique associée à votre compte GitHub.

- **Générer une clé SSH** (si vous n’en avez pas déjà) :
  ```bash
  ssh-keygen -t ed25519 -C "votre_email@exemple.com"
  ```
  (ou `rsa` si nécessaire, mais **ed25519** est recommandé).

- **Copier** la clé publique (généralement dans `~/.ssh/id_ed25519.pub`) sur votre compte GitHub, dans **Settings > SSH and GPG Keys**.

- **Tester la connexion** :
  ```bash
  ssh -T git@github.com
  ```
  Vous devriez voir un message de bienvenue ou du type : *"Hi X! You've successfully authenticated..."*.

---

# 4. Cloner le dépôt Pipelines dans `/opt/pipelines` via SSH

1. **Cloner le projet** depuis `git@github.com:ino-ca/pipelines.git` **dans le dossier courant** (`/opt/pipelines`) :
   ```bash
   git clone git@github.com:ino-ca/pipelines.git .
   ```
   - Le point final (`. `) indique que vous clonez le contenu du dépôt dans le dossier courant.

2. **Reprendre la propriété** si besoin (pour confirmer les droits) :
   ```bash
   sudo chown -R $USER:$USER /opt/pipelines
   ```

3. **Rendre le script de démarrage exécutable** :
   ```bash
   chmod +x start.sh
   ```

---

# 5. (Optionnel) Créer un environnement virtuel Python

Pour isoler les dépendances, il est recommandé d’utiliser un environnement virtuel :

1. **Créer** l’environnement (par exemple `.venv`) dans `/opt/pipelines` :
   ```bash
   python3.11 -m venv .venv
   ```
2. **Activer** l’environnement virtuel :
   ```bash
   source .venv/bin/activate
   ```
   Vous devriez voir un préfixe `(.venv)` dans votre console.

> *Si vous ne souhaitez pas utiliser d’environnement virtuel*, vous pouvez passer cette étape, mais veillez à gérer soigneusement les dépendances sur votre système principal.

---

# 6. Installer les dépendances

Le fichier `requirements.txt` du projet Pipelines liste les librairies nécessaires.

1. **Mettre à jour** pip (dans l’éventuel venv) :
   ```bash
   python3.11 -m ensurepip --upgrade
   pip install --upgrade pip
   ```
2. **Installer** les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

---

# 7. Démarrer le serveur Pipelines (manuel)

1. **Lancer** le script `start.sh` :
   ```bash
   bash ./start.sh --mode full
   ```
   - Vous verrez des logs indiquant les services démarrés et le port utilisé (généralement `http://localhost:9099`).

2. **Arrêter** le serveur :
   - Appuyez sur `Ctrl + C` dans la console pour interrompre l’application.

---

# 8. Créer un service systemd pour le démarrage automatique

Pour que Pipelines se lance automatiquement au démarrage de la machine :

1. **Créer** (ou modifier) le fichier de service `/etc/systemd/system/pipelines.service` :
   ```bash
   sudo nano /etc/systemd/system/pipelines.service
   ```

2. **Insérer** le contenu suivant en adaptant si nécessaire :

   ```ini
   [Unit]
   Description=Pipelines Server
   After=network.target

   [Service]
   # L'utilisateur et le groupe qui exécuteront le service (ex: ubuntu:ubuntu).
   User=ubuntu
   Group=ubuntu

   # Le répertoire de travail à utiliser
   WorkingDirectory=/opt/pipelines

   # (Optionnel) Définir le PATH pour utiliser l'environnement virtuel
   Environment="PATH=/opt/pipelines/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

   # La commande à exécuter pour démarrer Pipelines (mode full)
   ExecStart=/opt/pipelines/start.sh --mode full

   # Redémarrer automatiquement le service en cas de panne
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

   > **Points importants** :
   > - Remplacez `User=ubuntu` et `Group=ubuntu` par l’utilisateur et le groupe de votre choix (celui qui a accès à `/opt/pipelines`).  
   > - Si vous n’utilisez pas d’environnement virtuel, ajustez ou retirez la ligne `Environment=...`.  
   > - Changez également le chemin dans `ExecStart` si nécessaire (autre mode, autre script, etc.).

3. **Enregistrer** et fermer (dans Nano : Ctrl+O, Enter, Ctrl+X).

4. **Recharger** la configuration systemd :
   ```bash
   sudo systemctl daemon-reload
   ```

5. **Démarrer** et **activer** le service :
   ```bash
   sudo systemctl start pipelines
   sudo systemctl enable pipelines
   ```

6. **Vérifier** le statut :
   ```bash
   systemctl status pipelines
   ```
   Vous devriez voir `active (running)` si tout se passe bien.

7. **Consulter les journaux** :
   ```bash
   journalctl -u pipelines -f
   ```
   (Ctrl+C pour arrêter le suivi.)

---

# 9. Ajuster les permissions selon vos besoins

- Si vous exécutez le serveur en tant que service système (cf. ci-dessus), vérifiez que l’utilisateur défini dans `pipelines.service` possède bien les droits de lecture/exécution (et d’écriture si besoin) sur `/opt/pipelines`.
- Vous pouvez renforcer la sécurité en limitant les droits sur ce dossier :
  ```bash
  sudo chmod -R 755 /opt/pipelines
  ```
  Ainsi, seul le propriétaire a les droits d’écriture, les autres n’ayant que lecture/exécution.

---

# 10. Conseils supplémentaires

1. **Exécution en arrière-plan (alternatives)**  
   - Au lieu d’un service systemd, vous pouvez utiliser `tmux`, `screen` ou `nohup`, mais systemd est généralement plus fiable pour la gestion au démarrage.

2. **Sécurité**  
   - Vérifiez votre pare-feu (ex. `ufw`) et l’exposition du port si vous ne souhaitez pas rendre l’application publique.  
   - En production, vous pouvez placer un proxy HTTP/HTTPS (Nginx, Apache, Caddy…) devant Pipelines.

3. **Mises à jour**  
   - Pour mettre à jour, allez dans `/opt/pipelines` et faites :
     ```bash
     git pull
     ```
     puis (si besoin) :
     ```bash
     pip install -r requirements.txt
     ```
   - Redémarrez ensuite le service :  
     ```bash
     sudo systemctl restart pipelines
     ```

---

# Récapitulatif

1. **Installer Python 3.11** via Deadsnakes.  
2. **Créer** le répertoire `/opt/pipelines` et **ajuster les droits**.  
3. **Configurer l’accès SSH** à GitHub (si pas déjà fait), puis **cloner** via `git clone git@github.com:ino-ca/pipelines.git .`.  
4. **(Optionnel) Créer un environnement virtuel** et l’activer.  
5. **Installer** les dépendances (`pip install -r requirements.txt`).  
6. **Démarrer** Pipelines manuellement avec `start.sh` ou configurer **systemd**.  
7. **Créer** le fichier `pipelines.service`, **démarrer** et **activer** le service (`systemctl start pipelines && systemctl enable pipelines`).  
8. **Surveiller** les journaux via `journalctl -u pipelines -f`.  

Cette procédure complète vous permet d’installer, de configurer et de faire tourner automatiquement **Pipelines** après chaque redémarrage de votre serveur Ubuntu, le tout dans le dossier `/opt/pipelines` avec Python 3.11, tout en utilisant un mécanisme de déploiement par **SSH**.