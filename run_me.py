#from document_writer import DocumentWriter
from app.document_writer import DocumentWriter

if __name__ == '__main__':
    '''
    doc_writer = DocumentWriter(configuration_file="config.ini")

    doc_writer.run()
    '''
    doc_writer = DocumentWriter(configuration_file="config.ini")
    doc_writer.run()
