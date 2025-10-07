from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader('7.Langchain Document Loader/cg-internal-docs.pdf')

docs = loader.load()

print(len(docs))

print(docs[0].page_content)
print(docs[1].metadata)