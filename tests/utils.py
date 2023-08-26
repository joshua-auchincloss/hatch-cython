def true_if_eq(*vals):
    def inner(v):
        return any(v == val for val in vals)

    return inner
