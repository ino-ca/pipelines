Voici une procédure mise à jour pour installer le projet **Pipelines** sous Ubuntu, **dans le répertoire `/opt/pipelines`**, avec **Python 3.11** (via le PPA Deadsnakes), en ajustant également les droits. Cette version utilise **SSH** pour le clonage Git (à partir du dépôt `git@github.com:ino-ca/pipelines.git`).

---

## 1. Installer Python 3.11 via Deadsnakes

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

## 2. Préparer le répertoire `/opt/pipelines`

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

## 3. Configurer l’accès SSH à GitHub (si nécessaire)

Pour cloner via **SSH**, vous devez disposer d’une clé SSH publique associée à votre compte GitHub.

- **Générer une clé SSH** (si vous n’en avez pas déjà) :
  ```bash
  ssh-keygen -t ed25519 -C "votre_email@exemple.com"
  ```
  (ou `rsa` si nécessaire, mais ed25519 est recommandé).

- **Copier** la clé publique (généralement dans `~/.ssh/id_ed25519.pub`) sur votre compte GitHub, dans **Settings > SSH and GPG Keys**.

- **Tester la connexion** :
  ```bash
  ssh -T git@github.com
  ```
  Vous devriez voir un message de bienvenue (même s’il dit "Hi X! You've successfully authenticated...").

---

## 4. Cloner le dépôt Pipelines dans `/opt/pipelines` via SSH

1. **Cloner le projet** depuis `git@github.com:ino-ca/pipelines.git` dans le dossier courant (`/opt/pipelines`) :
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

## 5. (Optionnel) Créer un environnement virtuel Python

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

## 6. Installer les dépendances

Le fichier `requirements.txt` du projet Pipelines liste les librairies nécessaires.

1. **Mettre à jour** pip (dans le venv si vous en avez créé un) :
   ```bash
   python3.11 -m ensurepip --upgrade
   pip install --upgrade pip
   ```
2. **Installer** les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

---

## 7. Démarrer le serveur Pipelines

1. **Lancer** le script `start.sh` :
   ```bash
   sh ./start.sh
   ```
   - Vous verrez des logs indiquant les services démarrés et le port utilisé (généralement `http://localhost:8000`).

2. **Vérifier l’accès** :
   - Dans un navigateur, rendez-vous à l’adresse mentionnée dans les logs (ex. `http://localhost:8000`).

3. **Arrêter** le serveur :
   - Appuyez sur `Ctrl + C` dans la console pour interrompre le processus.

---

## 8. Ajuster les permissions selon vos besoins

- Si vous exécutez le serveur en tant que service système ou avec un autre utilisateur, vérifiez que cet utilisateur dispose des droits suffisants (lecture/exécution sur `/opt/pipelines`, écriture si nécessaire pour les logs, etc.).
- Pour des règles plus strictes, vous pouvez faire par exemple :
  ```bash
  sudo chmod -R 755 /opt/pipelines
  ```
  Ainsi, seul le propriétaire a les droits d’écriture, tandis que les autres utilisateurs ont uniquement lecture/exécution.

---

## 9. Conseils supplémentaires

1. **Exécution en arrière-plan** :
   - Si vous souhaitez garder le serveur actif après fermeture de la session, utilisez `tmux`, `screen` ou un service `systemd`.
2. **Sécurité** :
   - Vérifiez votre pare-feu et l’exposition du port si vous ne souhaitez pas rendre l’application publique.
   - En production, prévoyez un proxy (Nginx, Apache, Caddy…) pour gérer HTTPS et le routage.
3. **Mises à jour** :
   - Pour mettre à jour, rendez-vous dans `/opt/pipelines`, exécutez `git pull` pour récupérer les modifications.
   - Réinstallez éventuellement les dépendances (`pip install -r requirements.txt`) si `requirements.txt` a changé.

---

## Récapitulatif

1. **Installer Python 3.11** via Deadsnakes.  
2. **Créer** le répertoire `/opt/pipelines` et **ajuster les droits**.  
3. **Configurer l’accès SSH** à GitHub (si pas déjà fait), puis **cloner** via `git clone git@github.com:ino-ca/pipelines.git .`  
4. **(Optionnel) Créer un environnement virtuel** et l’activer.  
5. **Installer** les dépendances (`pip install -r requirements.txt`).  
6. **Démarrer** Pipelines avec `start.sh`.  
7. **Ajuster les permissions** et/ou exécuter en service selon les besoins.

Cette procédure vous permet d’installer et d’exécuter **Pipelines** dans un dossier dédié `/opt/pipelines`, avec Python 3.11, tout en gérant la sécurisation (droits, SSH) de manière organisée.