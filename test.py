import pandas as pd
import re


## Amazon Products
# data = pd.read_csv("/mnt/SuperData/Downloads/eCommerce-dataset-samples-main/amazon-products.csv")
# new_data = data[["title", "brand", "manufacturer", "categories"]].copy()
# new_data.dropna(inplace=True)
# pattern = r'[\u200E\u200F\u202A-\u202E]'
# new_data = new_data.apply(lambda col: col.map(lambda x: re.sub(pattern, "", str(x)) 
#                                   if isinstance(x, str) else x))


## Lazada Products
data = pd.read_csv("/mnt/SuperData/Downloads/eCommerce-dataset-samples-main/lazada-products.csv")
print(data.columns)
print(data.head())
exit()

new_data = data[["title", "brand",  "categories"]].copy()
new_data.dropna(inplace=True)
pattern = r'[\u200E\u200F\u202A-\u202E]'
new_data = new_data.apply(lambda col: col.map(lambda x: re.sub(pattern, "", str(x)) 
                                  if isinstance(x, str) else x))


## Save to CSV                                  
new_data.to_csv("fixtures/products-part3.csv", index=False, encoding="utf-8")