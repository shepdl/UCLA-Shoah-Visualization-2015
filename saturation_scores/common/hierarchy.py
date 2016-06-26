import common.db as db

def get_children_of(child, table="thesaurus_parents", levels=None):
    q = query(("""SELECT child_id FROM %s WHERE """ % table)  + """id = %s""", (child,))
    for result in q.results:
        return get_children_of(result)

