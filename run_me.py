from app.document_writer import DocumentWriter

if __name__ == '__main__':
    doc_writer = DocumentWriter(configuration_file="config.ini")
    doc_writer.run()
