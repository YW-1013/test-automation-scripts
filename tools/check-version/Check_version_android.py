import pandas as pd

# 读取 Excel 文件
file_path = 'version.xlsx'
df = pd.read_excel(file_path)
# 将应用名称和版本号存储到列表中
apps_versions = [(row['固件名称'], row['固件版本']) for _, row in df.iterrows()]

# 打印存储的列表
print(apps_versions)
