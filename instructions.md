# 📘 Application Instructions

---

## 🧩 OpenOffice Macros Setup

Follow these steps to create and manage macros in OpenOffice.

1. Open OpenOffice.
2. Navigate to:
    
    💡 Tools → Macros → Organize Macros → OpenOffice Basic
    
3. In the Organizer window:
    - Go to the Libraries section.
    - Click "New..."
    - Enter a name for the new library (for example: TranscriptionMacros) and click OK.
4. Switch to the Modules section:
    - Select your new library.
    - Click "New..."
    - Enter a name for the module (for example: PDFMacro) and click OK.

---

### 🛠️ Inserting Macro Code

Once your first module is created:

- Select the new module and click Edit.
- Delete the default code.
- Paste your custom macro code.
- Repeat this process for additional macros. You can either create new modules for each macro or reuse the same module if you prefer to keep them together.

---

## 🎛️ Configuring Macro Shortcuts

You can assign keyboard shortcuts to your macros for quick execution.

1. In OpenOffice, go to: Tools → Customize → Keyboard
2. Under Shortcut Keys, select your preferred key combination.
3. Assign the macros as follows:
    - Ctrl+7 → Notification or Message Macro
    - Ctrl+9 → PDF Upload Macro
    - Ctrl+M → Multiple PDFs
4. Click OK to save your shortcut settings.

Now all three macros can be executed instantly using your chosen shortcuts.

---

## 🧭 Automating with Windows Task Scheduler

You can automatically run your macros or launch your application using a scheduled task that triggers a .bat file.

---

### 📄 Creating the .bat File

1. Open Notepad (or any plain text editor).
2. Paste the following two lines into the file:
    
    ```batch
    @echo off
    pythonw "D:\TranscriptionTool\main.py"
    ```
    
    (Replace the path above with the actual location of your main.py file.)
    
3. Save the file as run_app.bat inside your project folder (for example: D:\TranscriptionTool\run_app.bat).
4. Test it by double-clicking the file — the app should start quietly in the background.

---

### 🪄 Step-by-Step: Create a Scheduled Task

1. Open Task Scheduler.
    
    Press Win + S, search for "Task Scheduler", and open it.
    
2. Click "Create Task..." (not "Create Basic Task").
3. General Tab:
    - Name: ExportPDFMacroTask (or any descriptive name)
    - Description: Optional
    - Check "Run with highest privileges"
    - Configure for: Choose your Windows version (use Windows 10 if unsure)

---

### ⏰ Triggers Tab

1. Click "New..."
2. Begin the task: Select "At log on"
3. Click OK to save the trigger.

---

### ⚙️ Actions Tab

1. Click "New..."
2. Action: Select "Start a program"
3. Program/script: Browse or paste the path to your .bat file (for example: D:\TranscriptionTool\run_app.bat)
4. Click OK.

---

## 📦 Final Setup: Download & Run the App

Follow these final steps to install and run the command-listening app.

---

### ⬇️ 1. Download the App

- Download the app archive (ZIP file).
- Unzip it into your desired folder (for example: D:\TranscriptionTool).

---

### 🛠️ 2. Configure config.py

- Open the config.py file inside the project folder.
- Find and edit the line that sets "pdf_dir" to match your preferred directory.

---

### 💾 3. Install Dependencies

Open a terminal or command prompt in the root of the project folder and run:

pip install -r requirements.txt

---

### 🚀 4. Run the App

Once installation is complete, start the app manually by running:

python main.py

Or let Task Scheduler handle it automatically via your .bat file at logon.

**Important:** Change app.toml to include absolute path to app folder