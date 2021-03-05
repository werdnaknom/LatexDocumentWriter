from app.document_writer import DocumentWriter

if __name__ == '__main__':
    '''
    Update the CONFIG.INI file to specify the OUTPUT, SECTION, and IMAGE 
    directories!
    '''
    doc_writer = DocumentWriter(configuration_file="config.ini")
    doc_writer.run()
