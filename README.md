# DuckBot
A Python 3.7 Discord.py bot created for ASA.    
    
## Requirements   
discord.py    
    
## Example bot/config.py    
```py
counting_channel = 123456780 # Your channel ID
embed_color = 0x000000 # Your color of choice
prefix = "Your prefix"
token = "Your token"
version = "Version name"

embed_footer_text = "Your choice of embed footer"
```    
    
## Example data_storage.json
```json
{
    "counting": {
        "last-count": {
            "number": 0,
            "member": 0
        },
        "record": 0
    }
}