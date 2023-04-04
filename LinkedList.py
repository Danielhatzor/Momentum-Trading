import pandas as pd


class LNode:
    def __init__(self, data=None, ref=None):
        self.data = data
        self.parent = None
        self.nextval = None
        self.prevval = None
        self.ref = ref

    @classmethod
    def append_to_dict(cls, dict, date, description, unit_yield, total_return, count_investments):
        dict["Date"].append(date)
        dict["Investment"].append(description)
        dict["Yield"].append(unit_yield)
        dict["Return"].append(total_return)
        dict["Investments Count"].append(count_investments)

    # makes a dataframe ready for graph. not for excel output
    def to_dataframe(self, data_key, stop_date=None):
        node = self

        row = 0
        total_return = 1
        dict = {"Date": [], "Investment": [], "Yield": [], "Return": [], "Investments Count": []}

        data = data_key(node)
        self.__class__.append_to_dict(dict, data.date, data.description, float('nan'), total_return,
                                      data.count_investments)

        while node is not None:
            data = data_key(node)
            if stop_date is not None and data.until_date > stop_date:
                break
            total_return *= data.data
            self.__class__.append_to_dict(dict, data.until_date, data.description, data.data, total_return,
                                          data.count_investments)
            row += 1
            node = node.nextval

        dataframe = pd.DataFrame(dict)
        return dataframe


class InvestMetadata:
    def __init__(self):
        self.metadata_df = None
        self.sector = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.data = None

    # Function to add node at begining
    def Atbegining(self, NewNode):
        self.head.prevval = NewNode
        NewNode.nextval = self.head
        self.head = NewNode

    # Print the linked list
    def listprint(self):
        printval = self.head
        while printval is not None:
            # print("asset: " + printval.asset + ", yield: " + str(printval.data))
            print(printval.data)

            printval = printval.nextval

## Function to add node in between
#   def Inbetween(self,middle_node,newdata):
#      if middle_node is None:
#         print("The mentioned node is absent")
#         return
#
#      NewNode = Node(newdata)
#      NewNode.nextval = middle_node.nextval
#      middle_node.nextval = NewNode
#
## Function to add newnode at end
#   def AtEnd(self, newdata):
#      NewNode = Node(newdata)
#      if self.head is None:
#         self.head = NewNode
#         return
#      laste = self.head
#      while(laste.nextval):
#         laste = laste.nextval
#      laste.nextval=NewNode
#
## Function to remove node
#   def RemoveNode(self, Removekey):
#      HeadVal = self.head
#
#      if (HeadVal is not None):
#         if (HeadVal.data == Removekey):
#            self.head = HeadVal.nextval
#            HeadVal = None
#            return
#      while (HeadVal is not None):
#         if HeadVal.data == Removekey:
#            break
#         prev = HeadVal
#         HeadVal = HeadVal.nextval
#
#      if (HeadVal == None):
#         return
#
#      prev.nextval = HeadVal.nextval
#      HeadVal = None
