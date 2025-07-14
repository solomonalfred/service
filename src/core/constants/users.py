from enum import Enum, auto


class UserType(str, Enum):
    '''
    ЮЛ - legal entity (LE)
    ФЛ - natural person (NP)
    ИП - individual entrepreneur (IE)
    Самозанятый - self-employed
    '''
    # LE = "legal entity"
    # NP = "natural person"
    # IE = "individual entrepreneur"
    # SE = "self-employed"
    LE = auto()
    NP = auto()
    IE = auto()
    SE = auto()

class UserRole(str, Enum):
    manager = "manager"
    employee = "employee"
