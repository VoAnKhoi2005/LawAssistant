from bson import ObjectId


class Document:
    def __init__(self, _id: str, document_number: str):
        self._id = _id
        self.document_number = document_number

    def to_dict(self):
        return {"_id": self._id, "document_number": self.document_number}


class Concept:
    def __init__(self, name: str, documents: list[Document], synonym: list[str] = None, description=None, _id=None):
        self.id = _id or ObjectId()
        self.name = name
        self.documents = documents
        self.synonym = synonym or []
        self.description = description

    def to_dict(self):
        return {
            "_id": self.id,
            "name": self.name,
            "documents": [doc.to_dict() if isinstance(doc, Document) else doc for doc in self.documents],
            "synonym": self.synonym,
            "description": self.description
        }


class Relation:
    def __init__(self, name: str, documents: list[Document], synonym: list[str] = None, description=None, _id=None):
        self.id = _id or ObjectId()
        self.name = name
        self.documents = documents
        self.synonym = synonym or []
        self.description = description

    def to_dict(self):
        return {
            "_id": self.id,
            "name": self.name,
            "documents": [doc.to_dict() if isinstance(doc, Document) else doc for doc in self.documents],
            "synonym": self.synonym,
            "description": self.description
        }


class Triplet:
    def __init__(self, subject_id, relation_id, object_id, subject_name=None, relation_name=None, object_name=None, _id=None):
        self.id = _id or ObjectId()
        self.subject_id = subject_id
        self.relation_id = relation_id
        self.object_id = object_id
        self.subject_name = subject_name
        self.relation_name = relation_name
        self.object_name = object_name

    def to_dict(self):
        return {
            "_id": self.id,
            "subject_id": self.subject_id,
            "relation_id": self.relation_id,
            "object_id": self.object_id,
            "subject_name": self.subject_name,
            "relation_name": self.relation_name,
            "object_name": self.object_name
        }