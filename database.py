import sqlite3 

def checkTableFile():
    conn = sqlite3.connect("binarian.db")
    c = conn.cursor()
                
    #get the count of tables with the name
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='file' ''')

    #if the count is 1, then table exists
    if c.fetchone()[0]==1 : 
        print('Table file exists.')
    else :
        conn.execute("CREATE TABLE file (text varchar (255), clean_text varchar (255));")
        print('Table file created')
                
    #commit the changes to db			
    conn.commit()
    #close the connection
    conn.close()

def checkTableText():       #untuk mengecek table jika sudah ada dia akan ngasih tau, klo belum ada dia akan buat baru
    conn = sqlite3.connect("binarian.db")
    c = conn.cursor()
                
    #get the count of tables with the name
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='string' ''')

    #if the count is 1, then table exists
    if c.fetchone()[0]==1 : 
        print('Table text exists.')
    else :
        conn.execute("CREATE TABLE string (text varchar (255), clean_text varchar (255));")
        print('Table text created')
                
    #commit the changes to db			
    conn.commit()
    #close the connection
    conn.close()

def insertTextString(a, b):
    conn = sqlite3.connect("binarian.db")
    conn.execute("insert into string (text, clean_text) values (?, ?)",(a, b))
    conn.commit()
    conn.close()
    print("Data berhasil disimpan di db sqlite")

def insertTextFile(a):
    a.rename(columns={'a': 'text', 'Tweet': 'clean_text'}, inplace=True)
    conn = sqlite3.connect('binarian.db') 
    a.to_sql('file', con=conn, index=False, if_exists='append') 
    conn.close()
    print("Data berhasil disimpan di db sqlite")
