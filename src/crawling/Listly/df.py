import requests
import csv

API_URL = "https://www.listly.io/api/single?key=fPR4gjCr&selected=1&arrange=y&href=y&header=y&file=csv"
API_TOKEN = "7YqGgH2YabaLTMMofTBzD8MocZ6rl2Oq"
headers = {	"Authorization": API_TOKEN }

response = requests.get(url=API_URL, headers=headers)
content = response.content

with open('./result.csv', 'wb') as f:
		f.write(content)