import inspect
import sys


class AccessError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ReadOnly:
    __className = None

    def __init__(self, value):
        try:
            callingframe = sys._getframe(1)
            self.__className = inspect.stack()[1][3]
        except:
            raise AccessError(
                "Cannot create an instance of Private outside a class")

        if self.__className == "<module>":
            raise AccessError(
                "Cannot create an instance of Private outside a class")

        self.__value = value

    def __get__(self, instance, owner):
        return self.__value

    def __set__(self, instance, value):
        try:
            callingframe = sys._getframe(1)
            callingClassName = callingframe.f_locals['self'].__class__.__name__

        except:
            raise AccessError("Access Error for class %s" % (self.__className))
        if(self.__className == callingClassName):
            self.__value = value


class Private:

    __className = None

    def __init__(self, value):
        try:
            callingframe = sys._getframe(1)
            self.__className = inspect.stack()[1][3]
        except:
            raise AccessError(
                "Cannot create an instance of Private outside a class")

        if self.__className == "<module>":
            raise AccessError(
                "Cannot create an instance of Private outside a class")

        self.__value = value

    def __get__(self, instance, owner):
        try:
            callingframe = sys._getframe(1)
            callingClassName = callingframe.f_locals['self'].__class__.__name__

        except:
            raise AccessError("Access Error for class %s" % (self.__className))

        callingClassValid = False
        if(self.__className == callingClassName):
            return self.__value
        else:
            try:
                callingClass = owner

                parentClasses = inspect.getmro(callingClass)
            except:
                raise AccessError("Access Error for class %s" %
                                  (self.__className))
            c = len(parentClasses)
            i = 0
            while(i < c):
                parentCls = parentClasses[i]
                if parentCls.__name__ == self.__className:
                    callingClassValid = True
                if(callingClassValid):
                    break
                i = i + 1
            if not callingClassValid:
                raise AccessError("Access Error for class %s" %
                                  (self.__className))
                return
            callingMethod = (inspect.stack()[1][3])
            callingClassMethods = callingClass.__dict__
            if callingMethod in callingClassMethods:
                raise AccessError("Access Error for class %s" %
                                  (self.__className))
            else:
                return self.__value


class Protected(Private):

    __className = None

    def __init__(self, value):
        try:
            callingframe = sys._getframe(1)
            self.__className = inspect.stack()[1][3]
        except:
            raise AccessError(
                "Cannot create an instance of Private outside a class")

        if self.__className == "<module>":
            raise AccessError(
                "Cannot create an instance of Private outside a class")

        self.__value = value

    def __get__(self, instance, owner):
        try:
            callingframe = sys._getframe(1)
            callingClassName = callingframe.f_locals['self'].__class__.__name__

        except:
            raise AccessError("Access Error for class %s" % (self.__className))

        callingClassValid = False
        if(self.__className == callingClassName):
            return self.__value
        else:
            try:
                callingClass = owner

                parentClasses = inspect.getmro(callingClass)
            except:
                raise AccessError("Access Error for class %s" %
                                  (self.__className))
            c = len(parentClasses)
            i = 0
            while(i < c):
                parentCls = parentClasses[i]
                if parentCls.__name__ == self.__className:
                    callingClassValid = True
                if(callingClassValid):
                    break
                i = i + 1
            if callingClassValid:
                return self.__value
            else:
                raise AccessError("Access Error for class %s" %
                                  (self.__className))
