class ConsumerMgr(object):
    """docstring for ConsumerMgr"""
    def __init__(self):
        super(ConsumerMgr, self).__init__();
        self.__loginConsumersDict = {};
        self.__appConsumerDict = {};
    
    def addLoginConsumer(self, loginId, consumer):
        if loginId not in self.__loginConsumersDict:
            self.__loginConsumersDict[loginId] = [];
        self.__loginConsumersDict[loginId].append(consumer);

    def removeLoginConsumer(self, loginId, consumer):
        if loginId not in self.__loginConsumersDict:
            return;
        if consumer in self.__loginConsumersDict[loginId]:
            self.__loginConsumersDict[loginId].remove(consumer);
        if len(self.__loginConsumersDict[loginId]) == 0:
            self.__loginConsumersDict.pop(loginId);
    
    def getLoginConsumers(self, loginId):
        return self.__loginConsumersDict.get(loginId, []);
    
    def addAppConsumer(self, appId, consumer):
        self.__appConsumerDict[appId] = consumer;

    def removeAppConsumer(self, appId):
        if appId in self.__appConsumerDict:
            self.__appConsumerDict.pop(appId);
    
    def getAppConsumer(self, appId):
        return self.__appConsumerDict.get(appId, None);