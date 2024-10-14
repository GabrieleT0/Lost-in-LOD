import requests
import os
import json
import utils
from cryptography.fernet import Fernet
KEY = 'ybi1hJAXk2E7Y4NZ2WD-maNdvoiN1iXoj3wutWWJWCE='

def getMetadati(idKG):
    url = 'gAAAAABnDNTqPLeTZ7-lO8WlrRrUmNv-0QulHU7dLnn9wTwk-hrYVzq_h9L28r8z66zre_XGCehujmwRg9hrmD-1xEAl3Yw-a7-ZRkCzuP-xaflzVP5MaUJ1QAHeRb1XJ2Ss62D0kpp-oBX1Xox95GD1_IlAbVxL0X5OzvCK8Nio-oDPo_aS6MM='
    cipher = Fernet(KEY)
    decrypted_url = (cipher.decrypt(url).decode()) + idKG
    try:
        response = requests.get(decrypted_url)    
        if response.status_code == 200:
            response = response.json()
            results = response.get('results')
            return results
        else:
            print("Connection failed to AGAPI")
            return False
    except:
        print('Connection failed to AGAPI')
        return False

def getAllKg():
    url = 'gAAAAABnDNTqPLeTZ7-lO8WlrRrUmNv-0QulHU7dLnn9wTwk-hrYVzq_h9L28r8z66zre_XGCehujmwRg9hrmD-1xEAl3Yw-a7-ZRkCzuP-xaflzVP5MaUJ1QAHeRb1XJ2Ss62D0kpp-oBX1Xox95GD1_IlAbVxL0X5OzvCK8Nio-oDPo_aS6MM='
    cipher = Fernet(KEY)
    decrypted_url = cipher.decrypt(url).decode()
    try:
        response = requests.get(decrypted_url)    
        if response.status_code == 200:
            print("Connection to API successful and data recovered")
            response = response.json()
            results = response.get('results')
            return results
        else:
            print("Connection failed")
            return False
    except:
        print('Connection failed')
        return False

def getSparqlEndpoint(metadata):
    if isinstance(metadata,dict):
        sparqlInfo = metadata.get('sparql')
        if not sparqlInfo:
            return False
        accessUrl = sparqlInfo.get('access_url')
        return accessUrl

def getNameKG(metadata):
    if isinstance(metadata,dict):
        title = metadata.get('title')
        return title
    else: 
        return False

def getIdByName(keyword):
    url = 'gAAAAABnDNTqPLeTZ7-lO8WlrRrUmNv-0QulHU7dLnn9wTwk-hrYVzq_h9L28r8z66zre_XGCehujmwRg9hrmD-1xEAl3Yw-a7-ZRkCzuP-xaflzVP5MaUJ1QAHeRb1XJ2Ss62D0kpp-oBX1Xox95GD1_IlAbVxL0X5OzvCK8Nio-oDPo_aS6MM='
    cipher = Fernet(KEY)
    decrypted_url = (cipher.decrypt(url).decode()) + keyword
    try:
        response = requests.get(decrypted_url)    
        if response.status_code == 200:
            print("Connection to API successful and data recovered")
            response = response.json()
            results = response.get('results')
            kgfound = []
            for i in range(len(results)):
                d = results[i]
                id = d.get('id')
                name = d.get('title')
                kgfound.append((id,name))
            return kgfound
        else:
            return False 
    except:
        return False
        
