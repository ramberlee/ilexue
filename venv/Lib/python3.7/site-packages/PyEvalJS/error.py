class JSError(Exception):
    def __init__(self,ErrorInfo):
        super(JSError,self).__init__()
        self.errorinfo = ErrorInfo
    def __str__(self):
        return self.errorinfo