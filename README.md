# RaniaDE 0.1.5 Beta

A lightweight, independent desktop shell for Linux/X11, built with Python and PyQt5. RaniaDE has its own top panel, centered Start button, application launcher, dock, and Rania App Market window. It keeps the user's wallpaper and can use KWin or Openbox as the window manager. RaniaDE is not KDE Plasma and does not launch `plasmashell`.

**Interface languages:** Russian and English. **Beta:** 0.1.5. The images in [`screenshots/`](screenshots/) show the earlier 0.1.0 interface and are retained as historical references.

## Install and run (English)

### Requirements

On Debian or Ubuntu, you need Python 3, PyQt5 and an active **X11** graphical session. Openbox is a lightweight option if no window manager is already running:

```bash
sudo apt update
sudo apt install python3 python3-pyqt5 openbox
```

KWin is optional and can be installed through the first-run setup or from APT:

```bash
sudo apt install kwin-x11
```

A Wayland-only session is not supported. If a window manager is already running, do not start a second one unless you explicitly choose **Use KWin now…** from RaniaDE's Desktop menu.

### Install

Clone the repository and run the installer as your regular user, not with `sudo`:

```bash
git clone https://github.com/lolartem26-max/RaniaDE.git
cd RaniaDE
./install.sh
```

The installer copies the shell to `~/.local/bin/rania-shell.py`, installs its start icon, and creates a desktop launcher. It does not install system packages or change your login/session configuration.

### First run and KDE components

On first launch, RaniaDE offers optional checkboxes for the KWin X11 window manager and a group of KDE applications: Dolphin, Konsole, Kate, Gwenview, Okular, Ark, KCalc and System Settings. The exact APT package names are shown before installation. Nothing is installed until you confirm that list. A visible terminal runs `sudo apt-get`; enter any administrator password there, not in RaniaDE. The wizard does not install or launch the full Plasma desktop shell.

To switch the current X11 session to KWin later, use **Desktop → Use KWin now…** and confirm the replacement. To return to Openbox, run `openbox --replace` in a terminal. The change is limited to the current X11 session; RaniaDE does not edit the system login configuration.

### Launch

From a terminal inside an active X11 desktop session, run:

```bash
python3 ~/.local/bin/rania-shell.py
```

RaniaDE shows a brief startup screen, then its panels. The centered **Start** button opens a fresh scan of installed graphical applications. The RU/EN selector is on the right side of the top panel. The power menu separates **Restart RaniaDE** (the shell only) from computer restart and shutdown; the computer actions require confirmation.

If you are starting from a text console, first start an X11 session and a window manager. The shell cannot create an X server by itself and is not configured as a display-manager login session.

To use a particular wallpaper, set its path when launching (the image itself is not included):

```bash
RANIADE_WALLPAPER="$HOME/Pictures/wallpaper.png" python3 ~/.local/bin/rania-shell.py
```

### Change the interface language

Use **RU** or **EN** on the right side of the top panel and choose **Русский** or **English**. The shell replaces only its own process to apply the selection; the window manager and other applications continue running. The choice is saved in `~/.config/rania/language`. Russian is the default.

## Установка и запуск (русский)

### Что понадобится

Для Debian или Ubuntu нужны Python 3, PyQt5 и уже запущенный графический сеанс **X11**. Если оконного менеджера ещё нет, можно использовать Openbox:

```bash
sudo apt update
sudo apt install python3 python3-pyqt5 openbox
```

KWin необязателен; его можно установить через первоначальную настройку или APT:

```bash
sudo apt install kwin-x11
```

Сеанс только Wayland пока не поддерживается. Если оконный менеджер уже работает, не запускайте второй, пока явно не выберете **«Использовать KWin сейчас…»** в меню «Рабочий стол».

### Установка

Склонируйте репозиторий и запустите установщик от обычного пользователя, не через `sudo`:

```bash
git clone https://github.com/lolartem26-max/RaniaDE.git
cd RaniaDE
./install.sh
```

Установщик копирует оболочку в `~/.local/bin/rania-shell.py`, устанавливает иконку запуска и создаёт ярлык приложений. Он не устанавливает системные пакеты и не меняет настройки входа в систему.

### Первый запуск и компоненты KDE

При первом запуске RaniaDE предлагает отметить оконный менеджер KWin для X11 и набор приложений KDE: Dolphin, Konsole, Kate, Gwenview, Okular, Ark, KCalc и «Параметры системы». Перед установкой показывается точный список пакетов APT. Пакеты не устанавливаются без отдельного подтверждения. Команда `sudo apt-get` запускается в видимом терминале; если система запросит пароль администратора, вводите его там, а не в RaniaDE. Мастер не устанавливает и не запускает полную оболочку Plasma.

Чтобы переключить текущий сеанс X11 на KWin позже, выберите **«Рабочий стол → Использовать KWin сейчас…»** и подтвердите замену оконного менеджера. Чтобы вернуться к Openbox, выполните в терминале `openbox --replace`. Изменение действует только в текущем сеансе X11; RaniaDE не меняет системные настройки входа.

### Запуск

Откройте терминал внутри уже запущенного графического сеанса X11 и выполните:

```bash
python3 ~/.local/bin/rania-shell.py
```

После короткого экрана запуска появятся панели. Центральная кнопка **«Пуск»** открывает обновляемый список установленных графических приложений. Переключатель RU/EN находится справа на верхней панели. В меню питания **«Перезапустить RaniaDE»** перезапускает только оболочку; перезагрузка и выключение компьютера вынесены отдельно и требуют подтверждения.

Если вы находитесь в текстовой консоли, сначала запустите графический сеанс X11 и оконный менеджер. Оболочка не создаёт X-сервер и не настраивается как отдельный сеанс на экране входа.

Чтобы использовать конкретные обои, задайте путь при запуске (сам файл изображения не включён):

```bash
RANIADE_WALLPAPER="$HOME/Pictures/wallpaper.png" python3 ~/.local/bin/rania-shell.py
```

### Смена языка интерфейса

Нажмите **RU** или **EN** справа на верхней панели и выберите **«Русский»** или **English**. Для применения выбора перезапускается только процесс оболочки; оконный менеджер и другие приложения продолжают работать. Язык сохраняется в `~/.config/rania/language`. По умолчанию используется русский.

## Repository contents

- `src/rania-shell.py` — RaniaDE 0.1.5 shell source.
- `assets/rania-start-white.png` — custom Start icon.
- `screenshots/RaniaDE-English.png` and `screenshots/RaniaDE-Russian.png` — historical v0.1.0 screenshots.
- `install.sh` — user-local installer; it does not run `sudo` or install packages.
- `LICENSE` — MIT License.

No wallpaper, VNC/noVNC password, account credential or machine/session configuration is included. KDE branding and trademarks are separate from the RaniaDE source-code license; RaniaDE is an independent project, not an official KDE product.

## License

MIT; see [`LICENSE`](LICENSE).
