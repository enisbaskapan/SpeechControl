from app.service import Extract

text = "2 gün sonraya gidip haftaya Eskişehir trenine 2 yetişkin"

request_ = {"defaultLocation": "Ankara", 
            "text": f"{text}"} 

extract = Extract()
response = extract.extract(request_)
print(response)