# certificstes-google-sheets-generator


Create arts to a event using Google Sheets and Google Drive
## To Run

```bash
    #Copy and configure env variables
    cp setting_example.toml setting.toml
    #Install Libs
    pip install -r requirements.txt 
    #Run to generate files and upload to google drive
    python src/main.py -s ./setting.toml
```