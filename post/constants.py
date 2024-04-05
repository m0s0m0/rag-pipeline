from enum import Enum
from typing import List, Tuple

class FileFormats(Enum):
    PDF = "PDF"
    CSV = "CSV"
    NA = "NA"

class ProcessingStatus(Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    



def get_choices(enum_class: Enum) -> List[Tuple[str, str]]:
    return [(item.name, item.value) for item in enum_class]
