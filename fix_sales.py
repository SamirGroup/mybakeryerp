f = open('templates/sales.html', 'rb')
d = f.read().decode('utf-8')
f.close()

# birinchi {% endblock %} ni topish (extra_scripts bloki ichida)
# u })(); </script> {% endblock %} bilan tugaydi
# keyin eski kod boshlanadi

# Birinchi endblock dan keyin hamma narsani kesib tashlaymiz
# Lekin avval qaysi endblock ekanini aniqlaymiz

import re
matches = [(m.start(), m.end()) for m in re.finditer(r'\{%-?\s*endblock\s*-?%\}', d)]
print('endblock positions:', matches)
print('total len:', len(d))

# extra_scripts bloki boshlanishi
es_start = d.find('{% block extra_scripts %}')
print('extra_scripts at:', es_start)

# extra_scripts bloki ichidagi birinchi endblock
for pos, end in matches:
    if pos > es_start:
        print('first endblock after extra_scripts at:', pos, end)
        # shu endblock dan keyin hamma narsani o'chiramiz
        clean = d[:end]
        f2 = open('templates/sales.html', 'wb')
        f2.write(clean.encode('utf-8'))
        f2.close()
        print('DONE, new len:', len(clean))
        break
