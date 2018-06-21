with open('testimonies_with_even_segments.txt') as in_file:
    x = ','.join([x.strip() for x in in_file.readlines()])
    print x
