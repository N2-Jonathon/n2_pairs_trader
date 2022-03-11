def safe_number(self, dictionary, key, default=None):
    value = self.safe_string(dictionary, key)
    return self.parse_number(value, default)
