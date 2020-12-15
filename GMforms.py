
class GMform:


    def __init__(self):
        self._arrForm={}
        self._arrLayounts={}
        self._arrFields={}

    def addForm(self,arr):
        self._arrForm=arr

    def  addLayout(self,idx,arr):
        self._arrLayounts[idx]=arr

    def addField(self,idx,arr):
        self._arrFields[idx]=arr

    def keysFields(self):
        return self._arrFields.keys()

    def countFields(self):
        return len(self._arrFields)

    def keysLayounts(self):
        return self._arrLayounts.keys()

    def countLayounts(self):
        return len(self._arrLayounts)

    def getField(self,key):
        return self._arrFields[key]

    def getLayount(self,key):
        return self._arrLayounts[key]

    def getForm(self):
        return self._arrForm


