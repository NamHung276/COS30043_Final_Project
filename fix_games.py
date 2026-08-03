with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\backend\app\routers\games.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix BaseException casting
text = text.replace('isinstance(detail_res, Exception)', 'isinstance(detail_res, BaseException)')
text = text.replace('isinstance(screenshots_res, Exception)', 'isinstance(screenshots_res, BaseException)')
text = text.replace('isinstance(trailers_res, Exception)', 'isinstance(trailers_res, BaseException)')
text = text.replace('isinstance(secondary_results[0], Exception)', 'isinstance(secondary_results[0], BaseException)')
text = text.replace('isinstance(secondary_results[1], Exception)', 'isinstance(secondary_results[1], BaseException)')
text = text.replace('isinstance(secondary_results[2], Exception)', 'isinstance(secondary_results[2], BaseException)')
text = text.replace('isinstance(secondary_results[3], Exception)', 'isinstance(secondary_results[3], BaseException)')
text = text.replace('isinstance(secondary_results[4], Exception)', 'isinstance(secondary_results[4], BaseException)')
text = text.replace('isinstance(secondary_results[5], Exception)', 'isinstance(secondary_results[5], BaseException)')

# Fix float casting with None
text = text.replace('float(cs_best.get("normalPrice", cs_val) or cs_val)', 'float(cs_best.get("normalPrice") or cs_val)')
text = text.replace('float(cs_best.get("normalPrice", cs_best.get("cheapest", 0)))', 'float(cs_best.get("normalPrice") or cs_best.get("cheapest", 0))')

with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\backend\app\routers\games.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Fixed typing errors in games.py')
