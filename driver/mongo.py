import pymongo

def get_db_mongo():
    connection_string = "mongodb+srv://guilhermeaugustosfc1:aIVlKXsQV0FNC3Pu@cluster0.yiwrufx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = pymongo.MongoClient(connection_string)
    db = client["economeizei"]
    return db
  