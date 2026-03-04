import re

with open('app/main.py', 'r') as f:
    lines = f.readlines()

# Patrones a buscar y reemplazar
replacements = [
    (r'ProductoElaborado\("Vacio", 12\.99, tipo="ROTACION"\)', 
     'ProductoElaborado(nombre="Vacio", precio_venta=12.99, tipo="ROTACION")'),
    
    (r'ProductoElaborado\("Bife de Chorizo", 15\.50, tipo="PREMIUM"\)',
     'ProductoElaborado(nombre="Bife de Chorizo", precio_venta=15.50, tipo="PREMIUM")'),
    
    (r'ProductoElaborado\("Nalga", 7\.00, tipo="ROTACION"\)',
     'ProductoElaborado(nombre="Nalga", precio_venta=7.00, tipo="ROTACION")'),
    
    (r'ProductoElaborado\("Primo Molido", 7\.50, tipo="ROTACION"\)',
     'ProductoElaborado(nombre="Primo Molido", precio_venta=7.50, tipo="ROTACION")'),
    
    (r'ProductoElaborado\("Grasa y Hueso \(Merma\)", 0\.50, tipo="BAJO_VALOR"\)',
     'ProductoElaborado(nombre="Grasa y Hueso (Merma)", precio_venta=0.50, tipo="BAJO_VALOR")')
]

new_lines = []
for line in lines:
    new_line = line
    for pattern, replacement in replacements:
        new_line = re.sub(pattern, replacement, new_line)
    new_lines.append(new_line)

with open('app/main.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Líneas corregidas en main.py")
