def to_dict(d: dict):
    _d = dict()
    for key, val in d.items():
        if hasattr(val, 'to_dict'):
            _d[key] = val.to_dict()
        else:
            if isinstance(val, dict):
                _d[key] = to_dict(val)
            else:
                _d[key] = val
    return _d


class BaseType(object):
    def to_dict(self):
        return to_dict(self.__dict__)

    @classmethod
    def from_dict(cls, dikt):
        return cls(**dikt)

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, type(self)):
            return False
        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    def __repr__(self):
        """For `print` and `pprint`"""
        return str(self.to_dict())
