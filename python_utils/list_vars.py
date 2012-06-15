def list_locals():
    for k in locals().keys(): print k

def list_globals():
    for k in globals().keys(): print k

def list_scope():
    for v in dir(): print v
    
