with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\src\components\SteamChartsPanel.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace variables
text = text.replace('steamchartsData.current', 'steamchartsData.live')
text = text.replace('steamchartsData.peak_all', 'steamchartsData.peak_all_time')

with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\src\components\SteamChartsPanel.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated SteamChartsPanel.vue')
