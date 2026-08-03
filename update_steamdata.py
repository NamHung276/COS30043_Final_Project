with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\src\components\SteamDataPanel.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace steamData with game
text = text.replace('steamData', 'game')

# Replace game.is_free with game.price (actually there is no is_free in UnifiedGameDetail, just check if price.final == 0)
text = text.replace('game.is_free', 'game.price?.final === 0')

# Replace initial_formatted with something we generate
# UnifiedPrice has initial, final, discount_percent
text = text.replace('game.price.final_formatted', '`$${this.game.price.final.toFixed(2)}`')
text = text.replace('game.price.initial_formatted', '`$${this.game.price.initial.toFixed(2)}`')

# Fix store note
text = text.replace('on Steam (USD)', 'on {{ game.price?.store_name || "Store" }} ({{ game.price?.currency || "USD" }})')

# Fix steam url
text = text.replace('game.steam_url', 'game.steam_url || game.price?.url')

# Fix component name internally
text = text.replace('name: "SteamDataPanel"', 'name: "ExtraDataPanel"')

with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\src\components\SteamDataPanel.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated SteamDataPanel.vue')
